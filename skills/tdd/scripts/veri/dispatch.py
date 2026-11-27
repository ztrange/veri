"""dispatch.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
# os, subprocess, event_log, github, paths, layout and budget_entries are test seams: tests reach them through dispatch
# (dispatch.layout, dispatch.github, ...) though the code reading them lives in dispatch_reads and dispatch_live.
import os
import subprocess
import sys
import time

import budget_entries
import dispatch_reads
import event_log
import github
import paths
import role_state
import run_dir as layout
import tunables
import watch_runs
from dispatch_live import World, lane, launch, now, restart_pending, run_dir, state_file
from dispatch_reads import (
    PR_URL,
    TRANSIENT_RETRY_BOUND,
    RateLimitPersists,
    answered,
    comment_bodies,
    exit_line,
    head_issue,
    issue_paths,
    issue_states,
    last_comment,
    launchable,
    overlap,
    overlap_poll,
    owner_repo,
    parked_issues,
    parse_args,
    pr_state,
    prioritize,
    queued_merges,
    run_pr_paths,
    run_prs,
    say,
    target_repo,
    transient,
)

USAGE = "usage: dispatch.sh [--target <N>]  (N a whole number >= 0; --target 0 holds dispatch: keeps watching and reporting exits, launches nothing; with no --target, N and the launch order come from .tdd/role-dev.state in the main working tree (.tdd/role-dev-<lane>.state under a VERI_LABEL of ready-for-agent:<lane>): its last n= line (a whole number, or auto: floor((T - W_other)/d), at least 1, at most live + the launchable queue), overridden by an unexpired timed-n line, and each override line pulls the issue it names to the front; exit 2 if that file is unreadable, has no n= line, or has a malformed n=, timed-n or override line)"


solvable_issues = watch_runs.solvable_issues
wait = watch_runs.wait
live_conductors = watch_runs.live_conductors


clock = time.time


# The overlap reads one dispatch process has made, emptied as main() starts: issue bodies per issue,
# PR diffs per (PR url, head sha), and the open run draft PRs with the time they were listed.
_reads = {}


# The names a test patches here (last_comment, clock, _reads, ...) are looked up in this namespace by the moved reads.
dispatch_reads.bind(globals())


def stall_window():
    return tunables.get("VERI_DISPATCH_STALL")


class State:
    """What one poll hands the next: the target, the last launch, the runs under watch and why, the queued merges,
    the rate-limit pause, the skips already printed, when each silent exit was first seen, and when the queue was
    last found with nothing launchable."""

    def __init__(self, target, follows_role_state=False):
        self.target = target
        self.follows_role_state = follows_role_state  # re-read the target from the role state file each poll
        self.auto = False  # the role state's N is `auto`: the target follows what T has left (PRD 036.6)
        self.previous = None  # the last issue launched
        self.logged = None  # the runs dispatch.log names after the mark, folded into seen at the first poll
        self.seen = []  # the runs under watch: live, absent or pending
        self.absent = []  # gone with no worktree and no conductor process, for one poll so far
        self.pending = []  # gone but not yet reportable: in preflight, restarting, or a silent exit under 30 s
        self.merges = []  # the PR urls of the queued merges running at the last poll
        self.resume_at = 0  # no queue read before this clock() time: a rate limit's reset
        self.reported = set()  # the (issue, path, PR url) skips already printed
        self.missing = {}  # issue: the clock() time its silent exit was first seen
        self.holding = []  # the runs this poll holds for a silent-exit decision: never called stalled meanwhile
        self.held_at = None  # the clock() time the queue last had nothing launchable


def _merge_failed(state, world):
    """merge-failed <url> for a queued merge that ended with its PR neither merged nor unresolved."""
    running = world.queued_merges()
    for pr_url in state.merges:
        if pr_url not in running and world.merge_state(pr_url) not in ("MERGED", "UNRESOLVED"):
            world.say(f"merge-failed {pr_url}\n")
            return 0
    state.merges = running
    return None


EXITED = "exited "
# The .tdd/dispatch-notified line that bounds the runs read back from dispatch.log: how many of its launched lines
# came before the first call that kept it. Only the launches after the mark are watched, so an upgrade never reports
# (or calls vanished) a run launched, and maybe already reported, before the record of reported exits existed.
LOGGED_LINE = "logged "


def _logged_runs(world):
    """The runs dispatch.log names after the mark, each once; with no mark yet, records one at the log's current
    length and answers []."""
    runs = world.launched_runs()
    lines = world.notified()
    marks = [int(word) for line in lines if line.startswith(LOGGED_LINE)
             for word in line.split()[1:2] if word.isdigit()]
    if not marks:
        world.record_notified(lines + [f"{LOGGED_LINE}{len(runs)}"])
        return []
    return list(dict.fromkeys(runs[marks[0]:]))


def _reported(issue, world):
    """True when an earlier call printed <issue>'s exit and dispatch.log names no launch of it since: its
    `exited <n> <k>` line, <k> the log's launched-line count when the exit was printed. A relaunch supersedes it."""
    runs = world.launched_runs()
    return any(issue not in runs[int(words[2]):] for words in map(str.split, world.notified())
               if len(words) == 3 and f"{words[0]} " == EXITED and words[1] == issue and words[2].isdigit())


def _exits(state, world, live):
    """The vanish, restart, silent-exit and closing-line rules for each seen run no longer live."""
    state.holding = []
    for issue in state.seen:
        if issue in live:
            continue
        if issue in state.logged and not world.has_worktree(issue):
            continue  # read back from dispatch.log, never seen live by this call: released, cleaned or merged
        if not world.has_worktree(issue):
            if world.conductor_alive(issue):
                if issue in state.absent:
                    state.absent.remove(issue)
                if issue not in state.pending:
                    state.pending.append(issue)
                continue
            state.pending = [p for p in state.pending if p != issue]
            if issue in state.absent:
                world.wait()
                if world.has_worktree(issue):
                    state.absent.remove(issue)
                    state.pending.append(issue)
                    continue
                world.complain(f"run {issue} vanished: no worktree left behind\n")
                return 2
            state.absent.append(issue)
            continue
        if world.restarting(issue):
            if issue not in state.pending:
                state.pending.append(issue)
            continue
        line = world.closing_line(issue)
        if line.startswith("silent-exit") and world.clock() - state.missing.setdefault(issue, world.clock()) < 30:
            if issue not in state.pending:
                state.pending.append(issue)
            state.holding.append(issue)
            continue
        kept = [line for line in world.notified() if not line.startswith(f"{EXITED}{issue} ")]
        world.record_notified(kept + [f"{EXITED}{issue} {len(world.launched_runs())}"])
        world.say(line + "\n")
        return 0
    return None


def _role_state_target(state, world):
    """The target from the role state file: its last n= line, unless an unexpired timed-n line overrides it; an n=auto
    line leaves state.auto set, the target then set by step from T (auto_target)."""
    lines = role_state.State(world.role_state())
    try:
        target = lines.last_n()
        for value, expiry in lines.timed_ns():
            if world.clock() < expiry:
                target = value
    except role_state.Malformed as why:
        said = {"n-missing": "no n= line", "n": f"malformed n line: {why.line}"}.get(why.kind, f"malformed {why.kind} line: {why.line}")
        world.complain(f"dispatch.sh: {said} in {world.role_state_file()}\n")
        return 2
    state.auto = target == role_state.AUTO_N
    if not state.auto:
        state.target = target
    return None


def auto_target(t, w_other, d, cap=None):
    """An `auto` lane's target (PRD 036.6 D20): floor((T - W_other) / d), at most <cap> (live + the launchable queue)
    when one is given, and at least 1 either way, since a target of 0 would hold dispatch."""
    target = (t - w_other) // d
    return max(1, target if cap is None else min(target, cap))


def _stalled(state, world):
    """stalled <n> for the first seen run silent for the stall window whose issue is not closed, save a run held for
    a silent-exit decision: its exit is the answer, and a stalled line would end the call before the hold does."""
    stall = int(stall_window())
    states = None
    for issue in state.seen:
        if issue in state.holding:
            continue
        last = world.last_activity(issue)
        if last is not None and world.clock() - last >= stall:
            if states is None:
                try:
                    states = world.issue_states(state.seen)
                except watch_runs.QueueUnreadable as failure:
                    world.complain(str(failure))
                    return 2
            if states.get(issue) == "CLOSED":
                continue
            world.say(f"stalled {issue}\n")
            return 0
    return None


# The .tdd/dispatch-notified line the queue-blocked rule owns: the last line it printed, so a restarted dispatch.sh
# prints it again only for a different set of blocking PRs. A new line is a closing line: it ends the watch (exit 0),
# since vdev reads advice only when a closing line ends it, and a fully blocked queue with no live run ends no other way.
BLOCKED_LINE = "queue-blocked "


def _launch_into_a_free_slot(state, world, live):
    """Launch the first launchable issue while fewer than the target runs hold a slot and nothing pauses launching."""
    ledger = state.previous and world.has_ledger(state.previous)
    held = len(live) + len(state.pending)
    if held < state.target:
        held = len(live) + len(set(state.pending) | {
            i for i in world.run_worktrees()
            if i not in live and world.restarting(i)})
    if not (held < state.target and (state.previous is None or ledger)
            and world.clock() >= state.resume_at
            and (state.held_at is None or world.clock() - state.held_at >= int(overlap_poll()))):
        return None
    try:
        queue = world.solvable()
        changed = world.run_pr_paths()
        free = [issue for issue in queue if launchable(issue, changed, state.reported, world)]
        free = prioritize(free, world.role_state())
    except role_state.Malformed as why:
        world.complain(f"dispatch.sh: malformed override line in {world.role_state_file()}: {why.line}\n")
        return 2
    except watch_runs.QueueUnreadable as failure:
        if failure.kind == "rate-limit" and not isinstance(failure, RateLimitPersists):
            reset = world.rate_limit_reset()
            if reset is None:
                pause = int(overlap_poll())
                world.complain(f"dispatch.sh: the queue read is rate-limited and its reset time could not be read; "
                               f"reading the queue again in {pause} seconds\n")
                reset = world.clock() + pause
            state.resume_at = reset
        elif str(failure):
            world.complain(str(failure))
            return 2
        elif not live:
            world.say("queue-empty\n")
            return 3
        return None
    if state.auto:
        state.target = max(1, min(state.target, len(live) + len(free)))
    state.held_at = world.clock() if not free and (queue or live) else None
    if queue and not free and not live:
        line = BLOCKED_LINE + " ".join(sorted({world.overlap(issue, changed)[1] for issue in queue}))
        lines = world.notified()
        if line not in lines:
            world.record_notified([kept for kept in lines if not kept.startswith(BLOCKED_LINE)] + [line])
            world.say(line + "\n")
            return 0
    if free and held < state.target:
        state.previous = free[0]
        world.launch(state.previous)
    return None


# The .tdd/dispatch-notified lines this rule owns: the live waiter entries counted at the last polls, oldest first, and
# the mark that the queueing line was printed for the queue those counts track. Every other line is another notice's.
QUEUE_LINE = "queue "
QUEUE_NOTIFIED = "queue-notified"


def queue_polls():
    """VERI_QUEUE_POLLS: how many polls' waiter counts the queueing rule reads; main refuses a bad one before any poll."""
    return int(tunables.get("VERI_QUEUE_POLLS", unless_empty=True))


def _queueing(state, world):
    """queueing <k> waiting for T=<t>, <w> workers in use: ... when the last polls' waiter counts are each above 0 and
    the newest exceeds the oldest (PRD 036.9), once per queue: not again until a poll counts no waiter. Advice only:
    it runs after the poll's launch decision and changes nothing that decision used."""
    waiting = world.waiting()
    polls = queue_polls()
    lines = world.notified()
    kept = next((line for line in lines if line.startswith(QUEUE_LINE)), "")
    counts = ([int(word) for word in kept.split()[1:] if word.isdigit()] + [waiting])[-polls:]
    notified = QUEUE_NOTIFIED in lines and waiting > 0
    growing = len(counts) == polls and min(counts) > 0 and counts[-1] > counts[0]
    others = [line for line in lines if not line.startswith(QUEUE_LINE) and line != QUEUE_NOTIFIED]
    queue = [QUEUE_LINE + " ".join(str(count) for count in counts)]
    world.record_notified(others + queue + ([QUEUE_NOTIFIED] if notified or growing else []))
    if growing and not notified:
        total, in_use = world.test_budget()
        world.say(f"queueing {waiting} waiting for T={total}, {in_use} workers in use: a lower N would shorten the wait\n")


STRETCHED = "stretched "


def _stretched(state, world, live):
    """stretched <issue> <tier> <seconds>s, idle <idle>s for the first `test-stretch` event of a live run whose run and
    tier .tdd/dispatch-notified does not hold yet, which it then holds (PRD 036.10): one warning per run and tier, not
    per test run. Advice only, like _queueing: it runs after the poll's launch decision and changes nothing."""
    lines = world.notified()
    for issue in live:
        for tier, seconds, idle in world.stretches(issue):
            key = f"{STRETCHED}{issue} {tier}"
            if key not in lines:
                world.record_notified(lines + [key])
                world.say(f"{key} {seconds}s, idle {idle}s\n")
                return


# The .tdd/dispatch-notified line the t-lowered rule owns: the time of the last lowering it reported.
LOWERED_LINE = "t-lowered "


def _lowered(state, world):
    """t-lowered <old> <new> <cases> when the lowering on record is newer than the last reported (PRD 036.7 LO8),
    recording its time so a restarted dispatch.sh never prints it again. Advice only, like _queueing."""
    lowering = world.lowering()
    if lowering is None:
        return
    at, old, new, cases = lowering
    lines = world.notified()
    reported = [int(word) for line in lines if line.startswith(LOWERED_LINE)
                for word in line.split()[1:2] if word.isdigit()]
    if reported and reported[0] >= at:
        return
    lowered = None
    if old == FLOOR_T and state.follows_role_state and not state.auto:
        try:
            lowered = _lower_n(state, world, cases)
        except role_state.Malformed:
            return  # the next poll's role state read refuses the same line, exit 2: nothing is recorded meanwhile
    world.record_notified([line for line in lines if not line.startswith(LOWERED_LINE)] + [LOWERED_LINE + str(at)])
    world.say(f"t-lowered {old} {new} {cases}\n")
    if lowered is not None:
        world.say(f"n-lowered {lowered[0]} {lowered[1]} {cases}\n")


# T's floor (load_timeouts.py): a lowering from it changes nothing, so dispatch lowers N instead (PRD 036.8 D22).
FLOOR_T = 2


def _lower_n(state, world, cases):
    """Lowers the role state's numeric N by 1, never below 1 (PRD 036.8): writes n=, drops every unexpired timed-n
    line so no earlier one takes over or raises N back, and adds a `veri (load)` message; (old, new), or None when N is
    already at most 1. Never raised back: only the human raises N."""
    old = state.target
    new = max(1, old - 1)
    if new >= old:
        return None
    lines = world.role_state()
    parsed = role_state.State(lines)
    unexpired = [line for line, (_, expiry) in zip(parsed.items("timed-n"), parsed.timed_ns(), strict=True)
               if world.clock() < expiry]
    kept = [line for line in lines if line not in unexpired]
    stamp = time.strftime(role_state.STAMP, time.localtime(world.clock()))
    text = f"veri (load) lowered N from {old} to {new} after {cases} timed out with T at its floor of {FLOOR_T}"
    world.write_role_state(kept + [f"n={new}", role_state.item_line(kept, "message", text, stamp)])
    return old, new


def step(state, world):
    """One poll: (state, exit code), the code None while dispatch keeps watching. Each line is printed through
    world.say or world.complain as it is decided, so a later failure in the same poll never swallows it."""
    live = world.live_runs()
    if state.logged is None:
        # a run an earlier call already reported is neither watched nor called stalled
        state.logged = [issue for issue in _logged_runs(world) if issue not in state.seen and not _reported(issue, world)]
        state.seen += state.logged
    state.logged = [issue for issue in state.logged if issue not in live]
    code = _merge_failed(state, world)
    if code is None:
        code = _exits(state, world, live)
    if code is None and state.follows_role_state:
        code = _role_state_target(state, world)
    if code is None:
        d = int(tunables.get("VERI_CONDUCTOR_TEST_WORKERS"))
        # an auto lane's need is C: a need of N x d would make T = N x d, and N, read back from T, would never grow
        world.write_test_budget(world.capacity() if state.auto else max(state.target, len(live)) * d)
        if state.auto:
            state.target = auto_target(world.test_budget()[0], world.other_workers(), d)
    if code is None:
        code = _stalled(state, world)
    if code is not None:
        return state, code
    for issue in live:
        state.missing.pop(issue, None)
    state.absent = [issue for issue in state.absent if issue not in live]
    state.pending = [issue for issue in state.pending if issue not in live and issue not in state.absent]
    state.seen = live + state.absent + state.pending
    code = _launch_into_a_free_slot(state, world, live)
    if code is None:
        _queueing(state, world)
        _stretched(state, world, live)
        _lowered(state, world)
    return state, code


def main(argv, world=None):
    """dispatch.sh: watch, decide and launch until a closing line or exit code; None when <world> says stop."""
    world = World() if world is None else world
    if not argv:
        path = world.unreadable_role_state()
        if path is not None:
            world.complain(f"dispatch.sh: cannot read {path}\n")
            return 2
    target = parse_args(argv) if argv else 0
    if target is None:
        world.complain(USAGE + "\n")
        return 2
    if not tunables.parses("VERI_DISPATCH_RETRY_SLEEP", tunables.get("VERI_DISPATCH_RETRY_SLEEP")):
        world.complain("dispatch.sh: VERI_DISPATCH_RETRY_SLEEP must be a whole number of seconds\n")
        return 2
    if not tunables.parses("VERI_QUEUE_POLLS", tunables.get("VERI_QUEUE_POLLS", unless_empty=True)):
        world.complain("dispatch.sh: VERI_QUEUE_POLLS must be a whole number of at least 2\n")
        return 2
    if not tunables.parses("VERI_CONDUCTOR_TEST_WORKERS", tunables.get("VERI_CONDUCTOR_TEST_WORKERS")):
        world.complain("dispatch.sh: VERI_CONDUCTOR_TEST_WORKERS must be a whole number of at least 1\n")
        return 2
    state = State(target, follows_role_state=not argv)
    _reads.clear()
    while True:
        state, code = step(state, world)
        if code is not None:
            return code
        if not world.wait():
            return None

if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
