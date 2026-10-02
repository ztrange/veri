"""status.sh's computations, run in-process."""
import json
import os
import sys
import time

from event_log import read_events, usage_totals


def conductor_answers(pid_file):
    try:
        with open(pid_file) as f:
            os.kill(int(f.read().strip()), 0)
        return True
    except (OSError, ValueError):
        return False


def run_activity(events_path, pid_file, timeout):
    """The activity line for one run, or None when it has launched no leaf."""
    last, attempts = None, 0
    newest, end = None, {}
    events = read_events(events_path)
    dollars, tokens = usage_totals(events)
    for line in events:
        newest = line
        if line.get("event") == "launch":
            if line.get("step") != (last or {}).get("step"):
                attempts = 0
            last = line
            attempts += 1
        elif line.get("event") in ("done", "bail", "stop"):
            end = line
        elif line.get("event") == "resume":
            end = {}

    now = int(time.time())
    if end.get("event") == "done":
        state = "done %s" % end.get("pr", "")
    elif end.get("event") == "stop":
        state = "stopped %s" % end.get("mode", "")
    elif end.get("event") == "bail":
        state = "bailed %s %s" % (end.get("phase", ""), end.get("classification", ""))
    elif newest is not None and now - int(newest["ts"]) > int(timeout) \
            and not conductor_answers(pid_file):
        state = "stale"
    else:
        state = "running"
    if last is None:
        return None
    if os.environ.get("STATUS_JSON") == "1":
        return json.dumps({"phase": last.get("phase", ""), "actor": last.get("actor", ""),
                           "leaf": last.get("name", ""), "elapsed_seconds": now - int(last["ts"]),
                           "attempts": attempts, "dollars": round(dollars, 2), "tokens": tokens,
                           "state": state.split(" ")[0], "pr": end.get("pr", ""),
                           "bail_phase": end.get("phase", ""),
                           "classification": end.get("classification", ""),
                           "stop_mode": end.get("mode", "")})
    return "%s  %s  %s %ds  attempt %d  $%.2f  %d tokens  %s" % (last.get("phase", ""),
           last.get("actor", ""), last.get("name", ""), now - int(last["ts"]),
           attempts, dollars, tokens, state)


def main(argv):
    if argv[0] == "run-activity":
        line = run_activity(*argv[1:4])
        if line is not None:
            print(line)


if __name__ == "__main__":
    main(sys.argv[1:])
