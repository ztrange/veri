"""Whether a run is live, stuck or ended, and what it is doing, read from its journal, pid and end mark.

Interface (plain values, no formatting, no JSON text):
- `activity(run, closed=False)`: an `Activity` for the run directory `run`.
- `state(run)`: just its state word, `activity(run).state`.

An `Activity` carries `state` (one word), `detail` (the state with its qualifier, the text `status` shows),
`phase`, `actor`, `leaf` (the latest launch's, else the end mark's, else the newest event's), `elapsed_seconds`
(since that event), `attempts` (launches of the latest launch's step), `dollars`, `tokens`, `pr`,
`bail_phase`, `classification`, `stop_mode` (from the end mark, "" when none) and `cause` ("" when none).

States:
- `running`: no end mark, or an end mark of bail, stop or preflight-refused with a live conductor (it relaunched).
- `done`: ended with a PR (`detail` "done <pr>").
- `stopped`: a stop mark (`detail` "stopped <mode>").
- `bailed`: a bail mark (`detail` "bailed <phase> <classification>").
- `refused`: a preflight-refused mark (`detail` "refused <check>").
- `stale`: journaled, no end mark and no live conductor: it died; `cause` says why.
- `closed`: only with `closed=True`, the issue is closed whatever the journal says.

Errors: a run with no journal reads as `running` with zero attempts and cost, and an `elapsed_seconds` of 0; a dead
pid with no end mark is `stale`; an unreadable journal line is skipped by `event_log`, so it counts for nothing.
"""
import os
import time
from dataclasses import dataclass

import event_log
import run_end
from event_log import usage_totals
from pid_file import live_conductor


@dataclass(frozen=True)
class Activity:
    state: str
    detail: str
    phase: str
    actor: str
    leaf: str
    elapsed_seconds: int
    attempts: int
    dollars: float
    tokens: int
    pr: str
    bail_phase: str
    classification: str
    stop_mode: str
    cause: str


def _detail(end, ended):
    if end.get("event") == "done":
        return "done %s" % end.get("pr", "")
    if end.get("event") == "stop":
        return "stopped %s" % end.get("mode", "")
    if end.get("event") == "bail":
        return "bailed %s %s" % (end.get("phase", ""), end.get("classification", ""))
    if end.get("event") == "preflight-refused":
        return "refused %s" % end.get("check", "")
    return "stale" if ended else "running"


def activity(run, closed=False):
    """The Activity of the run at `run`; `closed` marks its issue closed."""
    last, attempts = None, 0
    newest = None
    events_path_exists = os.path.isfile(event_log.path(run))
    events = event_log.events(run)
    dollars, tokens = usage_totals(events)
    ended, cause, end = run_end.run_end(run) if events_path_exists else (False, None, {})
    if end.get("event") in ("preflight-refused", "bail", "stop") and live_conductor(os.fspath(run)):
        ended, end = False, {}
    for line in events:
        newest = line
        if line.get("event") == "launch":
            if line.get("step") != (last or {}).get("step"):
                attempts = 0
            last = line
            attempts += 1

    now = int(time.time())
    detail = "closed" if closed else _detail(end, ended)
    last = last or end or newest or {"ts": now}
    return Activity(
        state=detail.split(" ")[0], detail=detail,
        phase=last.get("phase", ""), actor=last.get("actor", ""), leaf=last.get("name", ""),
        elapsed_seconds=now - int(last["ts"]), attempts=attempts, dollars=dollars, tokens=tokens,
        pr=end.get("pr", ""), bail_phase=end.get("phase", ""), classification=end.get("classification", ""),
        stop_mode=end.get("mode", ""), cause=cause or "")


def state(run):
    """The state word of the run at `run`."""
    return activity(run).state
