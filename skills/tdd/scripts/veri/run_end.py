"""One rule for whether a run has ended."""
import os
import re

import event_log
from event_log import read_events
from pid_file import live_conductor
from run_dir import run_file

USAGE_LIMIT = re.compile(r"Claude usage limit|You(?:'ve| have) hit your (?:[\w-]+ )?limit")
OUTAGE = ("Can't reach the API server", "ENOTFOUND")
MARKS = {"done": "done", "bail": "bailed", "stop": "stopped",
         "preflight-refused": "refused"}


def conductor_log(run_dir, issue):
    own = run_file(run_dir, "conductor-%s.log" % issue)
    if os.path.isfile(own):
        return own
    return run_file("", "conductor-%s.log" % issue)


def latest_result(path):
    """(launched, the latest launch's result record or None) for the conductor log at path."""
    result = None
    launched = False
    for r in read_events(path, skip_unreadable=True):
        if r.get("type") == "system" and r.get("subtype") == "init":
            result = None
            launched = True
        elif r.get("type") == "result":
            result = r
    return launched, result


def _launch_cause(run_dir, issue):
    tdd = run_file(run_dir, "")
    path = conductor_log(run_dir, issue)
    if not os.path.isfile(path):
        return None
    launched, result = latest_result(path)
    if result is None:
        return "killed" if launched else None
    if USAGE_LIMIT.match(result.get("result", "")):
        return "usage-limit"
    if any(marker in result.get("result", "") for marker in OUTAGE):
        return "outage"
    logs = sorted((os.path.join(tdd, n) for n in os.listdir(tdd) if n.endswith(".log")),
                  key=os.path.getmtime)
    limited = bool(logs) and any(r.get("error") == "rate_limit" for r in read_events(logs[-1], skip_unreadable=True))
    return "usage-limit" if limited else None


def standing_mark(events, ends=MARKS):
    """The mark that ended the run, the last event named in <ends> (by default done, bail, stop or preflight-refused)
    no resume or step-added followed; {} when none stands."""
    mark = {}
    for event in events:
        if event.get("event") in ends:
            mark = event
        elif event.get("event") in ("resume", "step-added"):
            mark = {}
    return mark


def _reposted_done(events):
    """The first done event when a kind=done comment stands after the last resume (a re-posted Done); {} otherwise."""
    without_other_comments = [e for e in events if e.get("event") != "comment" or e.get("kind") == "done"]
    if not standing_mark(without_other_comments, ("comment",)):
        return {}
    return next((e for e in events if e.get("event") == "done"), {})


def run_end(run_dir):
    """(ended, cause, standing mark) for the run at run_dir."""
    events = read_events(event_log.path(run_dir))
    mark = standing_mark(events)
    if not mark:
        issue = next((str(e["issue"]) for e in reversed(events) if "issue" in e), "")
        if live_conductor(os.fspath(run_dir)):
            return False, None, mark
        mark = _reposted_done(events)
        if not mark:
            return True, _launch_cause(run_dir, issue) or "unknown", mark
    return True, MARKS[mark["event"]], mark
