"""dispatch.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import os
import subprocess
import sys
import time
from datetime import datetime

import dispatch_reads
import event_log
import full_run_lock
import github
import paths
import pid_file
import restart_marker
import run_dir as layout
from role_state import state_path
import role_state
import test_budget
import tunables
import watch_runs

USAGE = "usage: dispatch.sh [--target <N>]  (N a whole number >= 0; --target 0 holds dispatch: keeps watching and reporting exits, launches nothing; with no --target, N and the launch order come from .tdd/role-dev.state in the main working tree (.tdd/role-dev-<lane>.state under a VERI_LABEL of ready-for-agent:<lane>): its last n= line, overridden by an unexpired timed-n line, and each override line pulls the issue it names to the front; exit 2 if that file is unreadable, has no n= line, or has a malformed n=, timed-n or override line)"


solvable_issues = watch_runs.solvable_issues
wait = watch_runs.wait
live_conductors = watch_runs.live_conductors


clock = time.time


# The overlap reads one dispatch process has made, emptied as main() starts: issue bodies per issue,
# PR diffs per (PR url, head sha), and the open run draft PRs with the time they were listed.
_reads = {}


# The names a test patches here (last_comment, clock, _reads, ...) are looked up in this namespace by the moved reads.
dispatch_reads.bind(globals())
from dispatch_reads import (RateLimitPersists, comment_bodies, last_comment, target_repo, owner_repo, PR_URL,
                            queued_merges, pr_state, issue_states, TRANSIENT_RETRY_BOUND, transient, answered,
                            overlap_poll, issue_paths, parked_issues, head_issue, run_prs, run_pr_paths, overlap,
                            launchable, exit_line)


def stall_window():
    return tunables.get("VERI_DISPATCH_STALL")


def restart_pending(issue):
    """True while a restart is in flight: the marker holds the restarter's pid; a dead pid is a
    stale marker, so the exit is reported. A marker that cannot say (restart-conductor.sh
    mid-write, empty, unreadable) counts as in flight: SCRIPTS.md's dispatch entry."""
    return restart_marker.in_flight(run_dir(issue), unreadable=True)


def now():
    return datetime.now().isoformat(timespec="seconds")


def run_dir(issue):
    return layout.worktree(layout.main_tree(missing=""), issue)


def launch(issue):
    scripts = paths.scripts_of(__file__)
    for script, log_name in (("run-conductor.sh", f"conductor-{issue}.log"), ("restart-conductor.sh", f"restart-{issue}.log")):
        with open(layout.main_file(layout.main_tree(missing=""), log_name), "ab") as out:
            subprocess.Popen([os.path.join(scripts, "detach-leaf.sh"), os.path.join(scripts, script), issue],
                             stdin=subprocess.DEVNULL, stdout=out, stderr=out)


def say(text):
    sys.stdout.write(text)
    sys.stdout.flush()


def parse_args(argv):
    if (
        not argv
        or not stall_window().isdigit()
        or not overlap_poll().isdigit()
        or len(argv) != 2
        or argv[0] != "--target"
        or not argv[1].isdigit()
    ):
        return None
    return int(argv[1])


def prioritize(free, lines):
    named_before = set()
    for named in role_state.State(lines).override_numbers():
        if named in free and named not in named_before:
            named_before.add(named)
            free.remove(named)
            free.insert(0, named)
    return free


def lane():
    return tunables.lane_of(tunables.get("VERI_LABEL", unless_empty=True))


def state_file():
    return state_path(layout.main_tree(missing=""), "dev", lane())


def _leg():
    """The pytest leg's module, whose registry rule (registered_legs) the waiter entries share; it lives in tests/leg/,
    loaded by test_budget.leg."""
    return test_budget.leg()


class World:
    """Everything dispatch's loop asks of the outside, the real adapter: the runs, the queued merges, the queue,
    the role state file, launching, output, the clock and the wait. Each method looks its helper up on this module
    when called, so a patch of the module's name (`dispatch.wait`, `dispatch.launch`, ...) still takes effect.
    tests/py/dispatch_world.py holds the other adapter, a scripted FakeWorld."""

    # the runs
    def live_runs(self):
        return live_conductors()

    def has_worktree(self, issue):
        return os.path.isdir(run_dir(issue))

    def conductor_alive(self, issue):
        return issue in pid_file.conductor_processes()

    def restarting(self, issue):
        return restart_pending(issue)

    def run_worktrees(self):
        """The names under the main tree's worktrees directory, [] when it is absent."""
        wt = layout.worktrees(layout.main_tree(missing=""))
        return os.listdir(wt) if os.path.isdir(wt) else []

    def has_ledger(self, issue):
        return os.path.exists(layout.ledger(run_dir(issue), issue))

    def closing_line(self, issue):
        return exit_line(issue)

    def last_activity(self, issue):
        """The last write time of the run's journal, outputs, logs and conductor.pid; None with no journal."""
        run = run_dir(issue)
        events = event_log.path(run)
        if not os.path.exists(events):
            return None
        return max(os.path.getmtime(f)
                   for f in (events, *glob.glob(layout.run_file(run, "*.out")),
                             *glob.glob(layout.run_file(run, "*.log")),
                             layout.run_file(run, "conductor.pid"))
                   if os.path.exists(f))

    def issue_states(self, issues):
        return answered("issue states", issue_states, issues)

    # the queued merges
    def queued_merges(self):
        return queued_merges()

    def merge_state(self, pr_url):
        return pr_state(pr_url)

    # the queue
    def solvable(self):
        return solvable_issues()

    def run_pr_paths(self):
        return run_pr_paths()

    def overlap(self, issue, changed):
        return overlap(issue, changed)

    def rate_limit_reset(self):
        return github.rate_limit_reset(subprocess.run)

    # the role state file
    def unreadable_role_state(self):
        """The role state file's path when it is missing or unreadable, else None."""
        state = state_file()
        return None if os.path.isfile(state) and os.access(state, os.R_OK) else state

    def role_state(self):
        return role_state.read_lines("dev", lane()) or []

    def role_state_file(self):
        return state_file()

    # the test queue
    def waiting(self):
        """The live waiter entries under VERI_PYTEST_WAITERS: legs waiting for T, alive under their recorded start time."""
        return len(_leg().registered_legs(full_run_lock.waiters_dir()))

    def test_budget(self):
        """(T, the workers live registered legs hold)."""
        leg = _leg()
        return leg.budget()[0], leg.registered_workers(full_run_lock.legs_dir())

    def stretches(self, issue):
        """(tier, seconds, idle) of each `test-stretch` event in <issue>'s run journal, in journal order; [] with none."""
        return [(e.get("tier", ""), e.get("seconds", ""), e.get("idle", ""))
                for e in event_log.events(run_dir(issue), "test-stretch", skip_unreadable=True)]

    def write_test_budget(self, need):
        """Replaces this lane's entry under VERI_TEST_BUDGET_DIR (test_budget.write) with <need>; nothing when no main
        working tree can be named."""
        main = layout.main_tree(missing="")
        if main:
            test_budget.write(main, lane() or "main", need)

    def notified(self):
        """The lines of the main working tree's .tdd/dispatch-notified, what dispatch.sh keeps across restarts; [] when
        it is absent or unreadable, or no main working tree can be named."""
        main = layout.main_tree(missing="")
        if not main:
            return []
        try:
            with open(layout.main_file(main, "dispatch-notified")) as f:
                return f.read().splitlines()
        except OSError:
            return []

    def lowering(self):
        """(time, old T, new T, cases) of the lowering on record in VERI_TEST_LOAD_FILE (PRD 036.7), read for the
        t-lowered notice and never acted on; None when the file is absent, unreadable or holds less than those four."""
        _leg()
        import load_timeouts
        try:
            with open(load_timeouts.load_path()) as f:
                lines = f.read().splitlines()
        except (OSError, UnicodeDecodeError):
            return None
        if len(lines) < 4 or not all(line.isascii() and line.isdigit() for line in lines[:3]) or not lines[3]:
            return None
        return int(lines[1]), int(lines[2]), int(lines[0]), lines[3]

    def record_notified(self, lines):
        """Replaces .tdd/dispatch-notified whole through a temporary file; nothing when no main working tree can be
        named, so a relative .tdd/ under whatever the current directory is never gets one."""
        main = layout.main_tree(missing="")
        if not main:
            return
        path = layout.main_file(main, "dispatch-notified")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        temporary = "%s.%d" % (path, os.getpid())
        with open(temporary, "w") as f:
            f.write("".join(line + "\n" for line in lines))
        os.replace(temporary, path)

    def launched_runs(self):
        """The issues of dispatch.log's `launched <n> <time>` lines, in order; a blank or malformed line is skipped, and
        [] when the log is absent or unreadable, or no main working tree can be named."""
        main = layout.main_tree(missing="")
        if not main:
            return []
        try:
            with open(layout.main_file(main, "dispatch.log")) as log:
                words = [line.split() for line in log]
        except (OSError, UnicodeDecodeError):
            return []
        return [w[1] for w in words if len(w) >= 2 and w[0] == "launched" and w[1].isascii() and w[1].isdigit()]

    # acting
    def launch(self, issue):
        """Launch <issue>'s run and append its `launched <n> <time>` line to dispatch.log."""
        launch(issue)
        with open(layout.main_file(layout.main_tree(missing=""), "dispatch.log"), "a") as log:
            log.write(f"launched {issue} {now()}\n")

    def say(self, text):
        say(text)

    def complain(self, text):
        sys.stderr.write(text)

    def clock(self):
        return clock()

    def wait(self):
        """Wait one poll; True: keep watching (the real world never says stop)."""
        wait()
        return True


class State:
    """What one poll hands the next: the target, the last launch, the runs under watch and why, the queued merges,
    the rate-limit pause, the skips already printed, when each silent exit was first seen, and when the queue was
    last found with nothing launchable."""

    def __init__(self, target, follows_role_state=False):
        self.target = target
        self.follows_role_state = follows_role_state  # re-read the target from the role state file each poll
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
    """The target from the role state file: its last n= line, unless an unexpired timed-n line overrides it."""
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
    state.target = target
    return None


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
    state.held_at = world.clock() if not free and (queue or live) else None
    if queue and not free and not live:
        line = BLOCKED_LINE + " ".join(sorted({world.overlap(issue, changed)[1] for issue in queue}))
        lines = world.notified()
        if line not in lines:
            world.record_notified([kept for kept in lines if not kept.startswith(BLOCKED_LINE)] + [line])
            world.say(line + "\n")
            return 0
    if free:
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
    world.record_notified([line for line in lines if not line.startswith(LOWERED_LINE)] + [LOWERED_LINE + str(at)])
    world.say(f"t-lowered {old} {new} {cases}\n")


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
        world.write_test_budget(max(state.target, len(live)) * int(tunables.get("VERI_CONDUCTOR_TEST_WORKERS")))
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
