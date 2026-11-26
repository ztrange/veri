"""dispatch.sh's real World, the adapter its loop asks of the outside, with the helpers only it uses. It never imports
dispatch: each method looks its helper up in the namespace dispatch.py hands dispatch_reads (via), so a patch of the
name on dispatch (`dispatch.wait`, `dispatch.launch`, ...) still takes effect."""
import glob
import os
import subprocess
import sys
from datetime import datetime

import event_log
import full_run_lock
import github
import paths
import pid_file
import restart_marker
import role_state
import run_dir as layout
import test_budget
import tunables
from dispatch_reads import via
from role_state import state_path


def restart_pending(issue):
    """True while a restart is in flight: the marker holds the restarter's pid; a dead pid is a
    stale marker, so the exit is reported. A marker that cannot say (restart-conductor.sh
    mid-write, empty, unreadable) counts as in flight: SCRIPTS.md's dispatch entry."""
    return restart_marker.in_flight(via("run_dir")(issue), unreadable=True)


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


def lane():
    return tunables.lane_of(tunables.get("VERI_LABEL", unless_empty=True))


def state_file():
    return state_path(layout.main_tree(missing=""), "dev", via("lane")())


def _leg():
    """The pytest leg's module, whose registry rule (registered_legs) the waiter entries share; it lives in tests/leg/,
    loaded by test_budget.leg."""
    return test_budget.leg()


class World:
    """Everything dispatch's loop asks of the outside, the real adapter: the runs, the queued merges, the queue,
    the role state file, launching, output, the clock and the wait. Each method looks its helper up in dispatch.py's
    namespace when called (via), so a patch of the module's name (`dispatch.wait`, `dispatch.launch`, ...) still takes
    effect. tests/py/dispatch_world.py holds the other adapter, a scripted FakeWorld."""

    # the runs
    def live_runs(self):
        return via("live_conductors")()

    def has_worktree(self, issue):
        return os.path.isdir(via("run_dir")(issue))

    def conductor_alive(self, issue):
        return issue in pid_file.conductor_processes()

    def restarting(self, issue):
        return via("restart_pending")(issue)

    def run_worktrees(self):
        """The names under the main tree's worktrees directory, [] when it is absent."""
        wt = layout.worktrees(layout.main_tree(missing=""))
        if not os.path.isdir(wt):
            return []
        return [name for name in os.listdir(wt) if os.path.isdir(os.path.join(wt, name))]

    def has_ledger(self, issue):
        return os.path.exists(layout.ledger(via("run_dir")(issue), issue))

    def closing_line(self, issue):
        return via("exit_line")(issue)

    def last_activity(self, issue):
        """The last write time of the run's journal, outputs, logs and conductor.pid; None with no journal."""
        run = via("run_dir")(issue)
        events = event_log.path(run)
        if not os.path.exists(events):
            return None
        return max(os.path.getmtime(f)
                   for f in (events, *glob.glob(layout.run_file(run, "*.out")),
                             *glob.glob(layout.run_file(run, "*.log")),
                             layout.run_file(run, "conductor.pid"))
                   if os.path.exists(f))

    def issue_states(self, issues):
        return via("answered")("issue states", via("issue_states"), issues)

    # the queued merges
    def queued_merges(self):
        return via("queued_merges")()

    def merge_state(self, pr_url):
        return via("pr_state")(pr_url)

    # the queue
    def solvable(self):
        return via("solvable_issues")()

    def run_pr_paths(self):
        return via("run_pr_paths")()

    def overlap(self, issue, changed):
        return via("overlap")(issue, changed)

    def rate_limit_reset(self):
        return github.rate_limit_reset(subprocess.run)

    # the role state file
    def unreadable_role_state(self):
        """The role state file's path when it is missing or unreadable, else None."""
        state = via("state_file")()
        return None if os.path.isfile(state) and os.access(state, os.R_OK) else state

    def role_state(self):
        return role_state.read_lines("dev", via("lane")()) or []

    def role_state_file(self):
        return via("state_file")()

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
                for e in event_log.events(via("run_dir")(issue), "test-stretch", skip_unreadable=True)]

    def write_test_budget(self, need):
        """Replaces this lane's entry under VERI_TEST_BUDGET_DIR (test_budget.write) with <need>; nothing when no main
        working tree can be named."""
        main = layout.main_tree(missing="")
        if main:
            test_budget.write(main, via("lane")() or "main", need)

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
        via("launch")(issue)
        with open(layout.main_file(layout.main_tree(missing=""), "dispatch.log"), "a") as log:
            log.write(f"launched {issue} {via('now')()}\n")

    def say(self, text):
        via("say")(text)

    def complain(self, text):
        sys.stderr.write(text)

    def clock(self):
        return via("clock")()

    def wait(self):
        """Wait one poll; True: keep watching (the real world never says stop)."""
        via("wait")()
        return True
