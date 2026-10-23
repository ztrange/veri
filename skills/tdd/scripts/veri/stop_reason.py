"""stop-reason.sh's report, run in-process."""
import os
import sys

import event_log
import tunables


def main(argv):
    if len(argv) != 1:
        sys.stderr.write("usage: stop-reason.sh <issue>\n")
        return 2
    if not os.path.isdir(os.path.join(".tdd", "wt", argv[0])):
        sys.stderr.write("stop-reason.sh: no run for issue %s under .tdd/wt\n" % argv[0])
        return 2
    gap = tunables.read("VERI_SLEEP_GAP", "900")
    if not (gap.isascii() and gap.isdigit() and int(gap) >= 1):
        sys.stderr.write("stop-reason.sh: VERI_SLEEP_GAP must be a whole number >= 1, got %r\n" % gap)
        return 2
    log = os.path.join(".tdd", "wt", argv[0], ".tdd", "events.jsonl")
    if not os.path.isfile(log):
        sys.stderr.write("stop-reason.sh: no events log at %s\n" % log)
        return 2
    conductor_log = _conductor_log(argv[0])
    events = event_log.read_events(log)
    last = events[-1]
    if last.get("event") == "done":
        sys.stdout.write("done %s\n" % last.get("pr"))
    elif last.get("event") == "bail":
        sys.stdout.write("bailed %s %s\n" % (last.get("phase"), last.get("classification")))
    elif last.get("event") == "stop":
        sys.stdout.write("stopped %s\n" % last.get("mode"))
    elif _live(os.path.join(os.path.dirname(log), "conductor.pid")):
        sys.stdout.write("running\n")
    elif not os.path.isfile(conductor_log):
        sys.stderr.write("stop-reason.sh: no conductor log at %s\n" % conductor_log)
        return 2
    else:
        reason = _usage_limit(argv[0], conductor_log)
        sys.stdout.write("killed\n" if reason is None else reason)
    for a, b in zip(events, events[1:]):
        if b["ts"] - a["ts"] > int(gap):
            sys.stdout.write("gap %s %s\n" % (a["ts"], b["ts"]))
    return 0


def _live(pidfile):
    try:
        with open(pidfile) as f:
            os.kill(int(f.read()), 0)
    except (OSError, ValueError):
        return False
    return True


def _conductor_log(issue):
    own = os.path.join(".tdd", "wt", issue, ".tdd", "conductor-%s.log" % issue)
    if os.path.isfile(own):
        return own
    return os.path.join(".tdd", "conductor-%s.log" % issue)


def _usage_limit(issue, conductor_log):
    result = None
    for r in event_log.read_events(conductor_log):
        if r.get("type") == "system" and r.get("subtype") == "init":
            result = None
        elif r.get("type") == "result":
            result = r
    if result is None:
        return None
    text = result.get("result", "")
    if "limit" not in text and not _rate_limited(issue):
        return "unknown %s\n" % text
    reset = text.partition(" resets ")[2]
    return "usage-limit %s\n" % reset if reset else "usage-limit\n"


def _rate_limited(issue):
    run = os.path.join(".tdd", "wt", issue, ".tdd")
    logs = sorted((os.path.join(run, n) for n in os.listdir(run) if n.endswith(".log")), key=os.path.getmtime)
    if not logs:
        return False
    return any(r.get("error") == "rate_limit" for r in event_log.read_events(logs[-1]))


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
