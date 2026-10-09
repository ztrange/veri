"""status.sh's computations, run in-process."""
import contextlib
import glob
import io
import json
import os
import re
import subprocess
import sys
import time

from event_log import read_events, usage_totals
from ledger import ledger_steps
from run_dir import run_file

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def conductor_answers(pid_file):
    try:
        with open(pid_file) as f:
            os.kill(int(f.read().strip()), 0)
        return True
    except (OSError, ValueError):
        return False


def run_activity(events_path, pid_file, timeout, as_json=False):
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
    if as_json:
        return json.dumps({"phase": phase, "actor": actor, "leaf": leaf, "elapsed_seconds": elapsed,
                           "attempts": attempts, "dollars": round(dollars, 2), "tokens": tokens,
                           "state": state.split(" ")[0], "pr": end.get("pr", ""),
                           "bail_phase": end.get("phase", ""),
                           "classification": end.get("classification", ""),
                           "stop_mode": end.get("mode", "")})
    return "%s  %s  %s %ds  attempt %d  $%.2f  %d tokens  %s" % (phase, actor, leaf, elapsed,
           attempts, dollars, tokens, state)


def scope_totals(name, solvable, event_paths, as_json=False):
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
    if as_json:
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
    first = listed.split("\n", 1)[0]
    return first[len("worktree "):] if first.startswith("worktree ") else first


def step_of_total(text):
    """"<n> of <m>": the first open step of the ledger's <m>, or <m> when none is open."""
    records = ledger_steps(text)
    total = records[-1][0] if records else "0"
    step = next((index for index, state, *_ in records if state == "open"), total)
    return "%s of %s" % (step, total)


def branch_of(run):
    return subprocess.run(["git", "-C", run, "symbolic-ref", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def solvable_count(name):
    """"<count>" solvable-issues.sh lists for scope <name>, or "?" when it gave no answer."""
    listed = subprocess.run([os.path.join(SCRIPTS, "solvable-issues.sh")], stdout=subprocess.PIPE,
                            text=True, env=dict(os.environ, VERI_LABEL=name))
    if listed.returncode == 0:
        return str(sum(1 for line in listed.stdout.split("\n") if line))
    if listed.returncode == 3:
        return "0"
    return "?"


def parse_args(argv):
    """(json, scope, watch seconds or None), or None for an unknown option."""
    scope, as_json, watch = os.environ.get("VERI_LABEL", ""), False, None
    args = list(argv)
    while args:
        arg = args.pop(0)
        if arg == "--watch":
            watch = 2
            if args and re.fullmatch(r"[0-9]+", args[0]):
                watch = int(args.pop(0))
        elif arg == "--json":
            as_json = True
        elif arg == "--scope":
            scope = args.pop(0) if args else ""
        else:
            sys.stderr.write("status.sh: unknown option '%s'\n" % arg)
            return None
    return as_json, scope, watch


def render(as_json, scope):
    timeout = os.environ.get("VERI_TIMEOUT") or "900"
    main_tree = main_working_tree()
    runs = sorted(glob.glob(os.path.join(main_tree, ".tdd", "wt", "*", ""))) if main_tree else []
    if not runs:
        print("no runs")
        return 3
    events, run_objects = [], []
    for run in runs:
        run = run.rstrip("/")
        branch = branch_of(run)
        activity = ""
        events_path = run_file(run, "events.jsonl")
        if os.path.isfile(events_path):
            events.append(events_path)
            activity = run_activity(events_path, run_file(run, "conductor.pid"),
                                    timeout, as_json) or ""
            if not as_json:
                activity = "  " + activity
        ledger = run_file(run, "issue-%s.md" % os.path.basename(run))
        if not os.path.isfile(ledger):
            continue
        with open(ledger) as f:
            text = f.read()
        heading = text.split("\n", 1)[0]
        if heading.startswith("# Plan for #"):
            heading = heading[len("# Plan for #"):]
        parts = heading.split(" — ", 1)
        issue, title = parts[0], parts[-1]
        step = step_of_total(text)
        if as_json:
            run_objects.append(run_object(issue, title, branch, step, activity))
            continue
        print("#%s  %s  %s  step %s%s" % (issue, title, branch, step, activity))
    scope_line = None
    if scope:
        scope_line = scope_totals(scope, solvable_count(scope), events, as_json)
    if as_json:
        print('{"runs": [%s], "scope": %s}' % (",".join(run_objects), scope_line or "null"))
    elif scope_line is not None:
        print(scope_line)
    return 0


def watch_loop(seconds, as_json, scope):
    while True:
        frame = io.StringIO()
        with contextlib.redirect_stdout(frame):
            render(as_json, scope)
        sys.stdout.write("\033[H\033[2J%s\n" % frame.getvalue().rstrip("\n"))
        sys.stdout.flush()
        time.sleep(seconds)


def main(argv):
    parsed = parse_args(argv)
    if parsed is None:
        return 2
    as_json, scope, watch = parsed
    if watch is not None:
        watch_loop(watch, as_json, scope)
    return render(as_json, scope)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
