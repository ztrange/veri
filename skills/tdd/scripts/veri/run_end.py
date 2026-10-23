"""One rule for whether a run has ended."""
import os
import re
import subprocess

from event_log import read_events

MARKS = {"done": "done", "bail": "bailed", "stop": "stopped"}


def command_line(pid):
    out = subprocess.run(["ps", "-o", "command=", "-p", str(pid)],
                         capture_output=True, text=True)
    return out.stdout.strip()


def parent_pid(pid):
    out = subprocess.run(["ps", "-o", "ppid=", "-p", str(pid)],
                         capture_output=True, text=True)
    return int(out.stdout.strip() or 0)


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
        return True, "unknown", mark
    return True, MARKS[mark["event"]], mark
