"""FakeWorld: a scripted, in-memory adapter for dispatch's world (the second adapter beside `dispatch.World`).

It answers from a script of ticks, one dict per poll; `wait()` moves to the next tick and, once the script is spent,
answers False, which ends `dispatch.main` quietly (it returns None). A spent world keeps answering its last tick.
Keys a tick may carry, each with the default an empty world would answer:

    live          issues whose conductor is live                     []
    merges        PR urls of running queued merges                   []
    merge_states  {pr url: MERGED | OPEN | CLOSED | UNRESOLVED}      {}
    no_worktree   issues whose .tdd/wt/<n> is absent                 []
    alive         issues whose conductor process is alive            []
    restarting    issues whose restart is in flight                  []
    worktrees     names under .tdd/wt                                []
    closing       {issue: its exit line, e.g. "done 7 <url>"}        silent-exit <n>
    activity      {issue: last write time of its run files}          no events file
    issue_states  {issue: OPEN | CLOSED}, or an exception to raise   every issue OPEN
    queue         solvable issues, or an exception to raise          []
    pr_paths      {pr url: changed paths}                            {}
    overlaps      {issue: (path, pr url)}                            {}
    no_ledger     issues whose ledger does not exist yet             []
    role_state    the role state file's lines                        the constructor's
    clock         seconds                                            the tick's index * 60
    reset         the rate-limit reset epoch                         0
    waiters       live waiter entries under VERI_PYTEST_WAITERS      0
    budget        (T, the workers live registered legs hold)         (8, 0)
    stretches     {issue: [(tier, seconds, idle) of each test-stretch]} {}
    lowering      (time, old T, new T, cases) of the load file       None

What it records: `said` (stdout text), `complained` (stderr text), `launched` (issues), `waits` (their count),
`launched_at_wait` (the launches made so far, one list per wait, taken as the wait is called),
`reads` ((tick key, tick index) of every answer asked for, in order), `notified_lines` (.tdd/dispatch-notified's
lines as last recorded; the constructor's `notified` until then), `budget_written` (the lane need of every
test-budget write, in order), `logged` (dispatch.log's launched issues: the constructor's `logged`, then each
launch appended).
"""


class FakeWorld:
    def __init__(self, *ticks, role_state=(), role_state_file="/main/.tdd/role-dev.state", unreadable=False, notified=(),
                 logged=()):
        self.ticks = list(ticks) or [{}]
        self.index = 0
        self.role_state_lines = list(role_state)
        self.role_state_path = role_state_file
        self.unreadable = unreadable
        self.said = []
        self.complained = []
        self.launched = []
        self.waits = 0
        self.launched_at_wait = []
        self.reads = []
        self.notified_lines = list(notified)
        self.logged = list(logged)
        self.budget_written = []

    def _tick(self):
        return self.ticks[min(self.index, len(self.ticks) - 1)]

    def _answer(self, key, default):
        self.reads.append((key, self.index))
        value = self._tick().get(key, default)
        if isinstance(value, BaseException):
            raise value
        return value

    # runs
    def live_runs(self):
        return list(self._answer("live", []))

    def has_worktree(self, issue):
        return issue not in self._answer("no_worktree", [])

    def conductor_alive(self, issue):
        return issue in self._answer("alive", [])

    def restarting(self, issue):
        return issue in self._answer("restarting", [])

    def run_worktrees(self):
        return list(self._answer("worktrees", []))

    def has_ledger(self, issue):
        return issue not in self._answer("no_ledger", [])

    def closing_line(self, issue):
        return self._answer("closing", {}).get(issue, f"silent-exit {issue}")

    def last_activity(self, issue):
        return self._answer("activity", {}).get(issue)

    def issue_states(self, issues):
        states = self._answer("issue_states", None)
        return {issue: "OPEN" for issue in issues} if states is None else states

    # merges
    def queued_merges(self):
        return list(self._answer("merges", []))

    def merge_state(self, pr_url):
        return self._answer("merge_states", {}).get(pr_url, "MERGED")

    # the queue
    def solvable(self):
        return list(self._answer("queue", []))

    def run_pr_paths(self):
        return dict(self._answer("pr_paths", {}))

    def overlap(self, issue, changed):
        return self._answer("overlaps", {}).get(issue)

    def rate_limit_reset(self):
        return self._answer("reset", 0)

    # the role state
    def unreadable_role_state(self):
        return self.role_state_path if self.unreadable else None

    def role_state(self):
        return list(self._answer("role_state", self.role_state_lines))

    def role_state_file(self):
        return self.role_state_path

    # the test queue
    def waiting(self):
        return self._answer("waiters", 0)

    def test_budget(self):
        return self._answer("budget", (8, 0))

    def stretches(self, issue):
        return list(self._answer("stretches", {}).get(issue, []))

    def lowering(self):
        return self._answer("lowering", None)

    def write_test_budget(self, need):
        self.budget_written.append(need)

    def notified(self):
        return list(self.notified_lines)

    def record_notified(self, lines):
        self.notified_lines = list(lines)

    def launched_runs(self):
        return list(self.logged)

    # acting
    def launch(self, issue):
        self.launched.append(issue)
        self.logged.append(issue)

    def say(self, text):
        self.said.append(text)

    def complain(self, text):
        self.complained.append(text)

    def clock(self):
        return self._answer("clock", self.index * 60)

    def wait(self):
        self.waits += 1
        self.launched_at_wait.append(list(self.launched))
        self.index += 1
        return self.index < len(self.ticks)
