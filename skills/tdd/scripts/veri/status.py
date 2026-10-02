"""status.sh's computations, run in-process."""
import glob
import json
import os
import subprocess
import sys
import time

from event_log import read_events, usage_totals
from ledger import ledger_steps


def json_mode():
    return os.environ.get("STATUS_JSON") == "1"


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
    phase, actor, leaf = last.get("phase", ""), last.get("actor", ""), last.get("name", "")
    elapsed = now - int(last["ts"])
    if json_mode():
        return json.dumps({"phase": phase, "actor": actor, "leaf": leaf, "elapsed_seconds": elapsed,
                           "attempts": attempts, "dollars": round(dollars, 2), "tokens": tokens,
                           "state": state.split(" ")[0], "pr": end.get("pr", ""),
                           "bail_phase": end.get("phase", ""),
                           "classification": end.get("classification", ""),
                           "stop_mode": end.get("mode", "")})
    return "%s  %s  %s %ds  attempt %d  $%.2f  %d tokens  %s" % (phase, actor, leaf, elapsed,
           attempts, dollars, tokens, state)


def scope_totals(name, solvable, event_paths):
    """The scope totals line over every run's events."""
    attempted = done = bailed = wall = 0
    dollars = 0.0
    for path in event_paths:
        attempted += 1
        events = read_events(path)
        dollars += usage_totals(events)[0]
        done += sum(1 for line in events if line.get("event") == "done")
        bailed += sum(1 for line in events if line.get("event") == "bail")
        if events:
            wall += int(events[-1]["ts"]) - int(events[0]["ts"])
    if json_mode():
        return json.dumps({"name": name, "attempted": attempted, "done": done,
                           "bailed": bailed, "wall_seconds": wall, "dollars": round(dollars, 2),
                           "solvable": int(solvable) if solvable.isdigit() else solvable})
    return "scope %s  attempted %d  done %d  bailed %d  wall %ds  $%.2f  solvable %s" % (
        name, attempted, done, bailed, wall, dollars, solvable)


def run_object(issue, title, branch, step, activity):
    """One run's --json object: the ledger fields, then the activity object's."""
    run = {"issue": issue, "title": title, "branch": branch, "step": step}
    run.update(json.loads(activity) if activity else {})
    return json.dumps(run)


def main_working_tree():
    listed = subprocess.run(["git", "worktree", "list", "--porcelain"],
                            capture_output=True, text=True).stdout
    return listed.split("\n", 1)[0][len("worktree "):]


def step_of_total(text):
    """"<n> of <m>": the first open step of the ledger's <m>."""
    records = ledger_steps(text)
    step = next(index for index, state, *_ in records if state == "open")
    return "%s of %s" % (step, records[-1][0])


def render():
    for run in sorted(glob.glob(os.path.join(main_working_tree(), ".tdd", "wt", "*", ""))):
        run = run.rstrip("/")
        with open(os.path.join(run, ".tdd", "issue-%s.md" % os.path.basename(run))) as f:
            print("step %s" % step_of_total(f.read()))


def main(argv):
    if not argv:
        render()
    elif argv[0] == "run-activity":
        line = run_activity(*argv[1:4])
        if line is not None:
            print(line)
    elif argv[0] == "scope-totals":
        print(scope_totals(argv[1], argv[2], argv[3:]))
    elif argv[0] == "run-object":
        print(run_object(*argv[1:6]))


if __name__ == "__main__":
    main(sys.argv[1:])
