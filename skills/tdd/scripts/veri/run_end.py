"""One rule for whether a run has ended."""
import os

from event_log import read_events

MARKS = {"done": "done", "bail": "bailed", "stop": "stopped"}


def run_end(run_dir):
    """(ended, cause, standing mark) for the run at run_dir."""
    mark = {}
    events = read_events(os.path.join(run_dir, ".tdd", "events.jsonl"))
    for event in events:
        if event.get("event") in MARKS:
            mark = event
        elif event.get("event") in ("resume", "step-added"):
            mark = {}
    return True, MARKS[mark["event"]], mark
