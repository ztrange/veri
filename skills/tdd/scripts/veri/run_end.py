"""One rule for whether a run has ended."""
import os
import re
import subprocess

from event_log import read_events

MARKS = {"done": "done", "bail": "bailed", "stop": "stopped"}


def _ps(field, pid):
    out = subprocess.run(["ps", "-o", field + "=", "-p", str(pid)],
                         capture_output=True, text=True)
    return out.stdout.strip()


def command_line(pid):
    return _ps("command", pid)


def parent_pid(pid):
    return int(_ps("ppid", pid) or 0)


def _is_conductor(line, issue):
    return re.search(r"(run-conductor\.sh|run_conductor\.py)\s+%s(\s|$)" % re.escape(issue), line)


def _live(run_dir, issue):
    try:
        with open(os.path.join(run_dir, ".tdd", "conductor.pid")) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
    except (OSError, ValueError):
        return False
    if _is_conductor(command_line(pid), issue):
        return True
    return bool(_is_conductor(command_line(parent_pid(pid)), issue))


def _usage_limited(run_dir, issue):
    tdd = os.path.join(run_dir, ".tdd")
    path = os.path.join(tdd, "conductor-%s.log" % issue)
    if not os.path.isfile(path):
        path = os.path.join(".tdd", "conductor-%s.log" % issue)
    if not os.path.isfile(path):
        return False
    result = None
    for r in read_events(path):
        if r.get("type") == "system" and r.get("subtype") == "init":
            result = None
        elif r.get("type") == "result":
            result = r
    if result is None:
        return False
    if "limit" in result.get("result", ""):
        return True
    logs = sorted((os.path.join(tdd, n) for n in os.listdir(tdd) if n.endswith(".log")),
                  key=os.path.getmtime)
    return bool(logs) and any(r.get("error") == "rate_limit" for r in read_events(logs[-1]))


def run_end(run_dir):
    """(ended, cause, standing mark) for the run at run_dir."""
    mark = {}
    events = read_events(os.path.join(run_dir, ".tdd", "events.jsonl"))
    for event in events:
        if event.get("event") in MARKS:
            mark = event
        elif event.get("event") in ("resume", "step-added"):
            mark = {}
    if not mark:
        issue = str(events[-1].get("issue", "")) if events else ""
        if _live(run_dir, issue):
            return False, None, mark
        if _usage_limited(run_dir, issue):
            return True, "usage-limit", mark
        return True, "unknown", mark
    return True, MARKS[mark["event"]], mark
