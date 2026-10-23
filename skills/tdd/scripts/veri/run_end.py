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


def conductor_log(run_dir, issue):
    own = os.path.join(run_dir, ".tdd", "conductor-%s.log" % issue)
    if os.path.isfile(own):
        return own
    return os.path.join(".tdd", "conductor-%s.log" % issue)


def latest_result(path):
    """(launched, the latest launch's result record or None) for the conductor log at path."""
    result = None
    launched = False
    for r in read_events(path):
        if r.get("type") == "system" and r.get("subtype") == "init":
            result = None
            launched = True
        elif r.get("type") == "result":
            result = r
    return launched, result


def _launch_cause(run_dir, issue):
    tdd = os.path.join(run_dir, ".tdd")
    path = conductor_log(run_dir, issue)
    if not os.path.isfile(path):
        return None
    launched, result = latest_result(path)
    if result is None:
        return "killed" if launched else None
    if "limit" in result.get("result", ""):
        return "usage-limit"
    logs = sorted((os.path.join(tdd, n) for n in os.listdir(tdd) if n.endswith(".log")),
                  key=os.path.getmtime)
    limited = bool(logs) and any(r.get("error") == "rate_limit" for r in read_events(logs[-1]))
    return "usage-limit" if limited else None


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
        return True, _launch_cause(run_dir, issue) or "unknown", mark
    return True, MARKS[mark["event"]], mark
