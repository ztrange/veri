"""veri/queued_merge.py joining a run to the stack branch (PRD 034.1c), in-process: merge-lock.sh, detect-test-command.sh,
prose-owed.sh, sh and git faked as processes; the pull request's state read through queued_merge._pull, spied in-process."""
import os

import pytest
from veri import queued_merge

from process_fakes import HANGS

PR = "https://github.com/o/r/pull/7"
BRANCH = "tdd/7-slug"
PID = str(os.getpid())
ORIGIN_SHA = "1111111"
STACK_SHA = "5555555"
MOVED_SHA = "6666666"
REBASED = "abc1234"
REBASED_AGAIN = "abc5678"
CLONE = "/clone"
FOREIGN = "fffffff"
FAST_COMMIT = "ccccccc"
TREE = "7777777"


class World:
    """The join's world: origin's stack and run branch, what each call answers, and every call made."""

    def __init__(self, tmp_path, ledger="- [x] a step ⟦criterion 1⟧\n- [ ] the full suite ⟦full-suite⟧ ⟦criterion 2⟧\n",
                 rebase=0, fast=0, owed=0, stack_pushes=(0,), reads=({"merged": True},), lock=0, stopped=True, extra=None,
                 stack_line="veri: stack branch: stack\n", base="stack", foreign=False, pr_default="trunk", first=None):
        self.wt = str(tmp_path / "wt")
        os.makedirs(self.wt + "/.tdd")
        with open(self.wt + "/CLAUDE.md", "w") as f:
            f.write(stack_line)
        with open(self.wt + "/.tdd/issue-7.md", "w") as f:
            f.write("# Plan for #7\n\n" + ledger)
        self.stack = [STACK_SHA]
        self.rebased = []
        self.rebase, self.fast, self.owed, self.lock = rebase, fast, owed, lock
        self.stopped_dir = str(tmp_path / "rebase-merge") if rebase and stopped else ""
        if self.stopped_dir:
            os.makedirs(self.stopped_dir)
        self.extra = extra or {}
        self.base = base
        self.fast_commits = self.fast_dirties = self.fast_ran = False
        self.foreign = foreign
        self.pr_default = pr_default
        self.first = first
        self.stack_pushes = list(stack_pushes)
        self.reads = list(reads)
        self.pulls = []

    def install(self, fake_processes, monkeypatch):
        first = {"state": "open", "merged": False, "head": {"ref": BRANCH, "sha": ORIGIN_SHA},
                 "base": {"ref": self.base, "repo": {"default_branch": self.pr_default}}}
        first = self.first if self.first is not None else first

        def pull(repo, pr):
            self.pulls.append((repo, pr))
            if len(self.pulls) == 1:
                return None if first == "none" else first
            return self.reads.pop(0) if self.reads else None

        monkeypatch.setattr(queued_merge, "_pull", pull)
        self.fake = fake_processes.answers({}, default=self.answer)
        return self

    def answer(self, line, **_):
        wt = "git -C %s " % self.wt
        for prefix, answer in self.extra.items():
            if line.startswith(prefix.replace("<wt>", self.wt)):
                if isinstance(answer, BaseException):
                    raise answer
                return answer
        if line == wt + "rev-parse --git-path rebase-merge":
            return 0, self.stopped_dir + "\n", ""
        if line.startswith(wt + "reset --hard "):
            self.rebased = []
            return 0, "", ""
        if " merge-tree --write-tree " in line:
            return 0, TREE + "\n", ""
        if line.endswith("rev-parse --verify HEAD^{tree}"):
            return 0, TREE + "\n", ""
        if line.endswith("ls-remote --symref origin HEAD"):
            return 0, "ref: refs/heads/trunk\tHEAD\n", ""
        if line.startswith("stack-red.sh"):
            return 3, "", "stack-red: CI's latest answer on origin/stack is success, not red\n"
        if line.startswith("merge-lock.sh take"):
            return self.lock, "", ""
        if line.startswith("merge-lock.sh"):
            return 0, "", ""
        if line == wt + "rev-parse --verify refs/remotes/origin/stack":
            return (0, self.stack[0] + "\n", "") if self.stack[0] else (128, "", "fatal: Needed a single revision\n")
        if line == wt + "rev-parse --verify refs/remotes/origin/" + BRANCH:
            return 0, (self.rebased[-1] if self.rebased else FOREIGN if self.foreign else ORIGIN_SHA) + "\n", ""
        if line == wt + "rev-parse --verify HEAD":
            return 0, (self.rebased[-1] if self.rebased else ORIGIN_SHA) + "\n", ""
        if line.startswith(wt + "merge-base --is-ancestor " + FOREIGN):
            return 1, "", ""
        if line.startswith(wt + "merge-base --is-ancestor"):
            return 0, "", ""
        if line.startswith(wt + "rebase ") and "--abort" not in line:
            if self.rebase:
                return self.rebase, "", "CONFLICT (content): Merge conflict in a.py\n"
            self.rebased.append(REBASED if self.stack[0] == STACK_SHA else REBASED_AGAIN)
            return 0, "", ""
        if line.startswith("detect-test-command.sh --tier fast"):
            return 0, "make unit\n", ""
        if line == "sh -c make unit":
            self.fast_ran = True
            if self.fast_commits:
                self.rebased.append(FAST_COMMIT)
            return self.fast, "", ""
        if line == wt + "status --porcelain":
            return 0, (" M r.txt\n" if self.fast_dirties and self.fast_ran else ""), ""
        if line.startswith("prose-owed.sh"):
            return self.owed, "", ""
        if line.startswith(wt + "push ") and line.endswith(":refs/heads/stack"):
            code = self.stack_pushes.pop(0) if self.stack_pushes else 0
            if code:
                self.stack[0] = MOVED_SHA
                return 1, "", " ! [rejected] (fetch first)\n"
            self.stack[0] = line.split()[-1].split(":")[0]
            return 0, "", ""
        if line.endswith("--git-common-dir"):
            return 0, CLONE + "/.git\n", ""
        return 0, "", ""

    @property
    def calls(self):
        return self.fake.calls

    def stack_pushed(self):
        return [c for c in self.calls if c.endswith(":refs/heads/stack")]


ENV = {"VERI_MERGE_SETTLE_READS": "3", "VERI_MERGE_SETTLE_SLEEP": "0"}


def join(run_cli, world):
    return run_cli(queued_merge, [PR, world.wt, BRANCH, "the capability"], env=ENV)


def test_joins_a_pull_request_whose_base_is_the_stack_rebasing_checking_and_pushing_the_tip_to_the_stack(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    wt = "git -C %s " % world.wt
    order = [c for c in world.calls if c.startswith(("merge-lock.sh take", wt + "fetch", wt + "rebase", wt + "push",
                                                     "sh -c", "prose-owed.sh"))]
    assert (code, order[:7]) == (0, [
        "merge-lock.sh take --pid %s" % PID,
        wt + "fetch --prune origin",
        wt + "rebase origin/stack",
        wt + "push --force-with-lease=%s:%s origin %s:refs/heads/%s" % (BRANCH, ORIGIN_SHA, REBASED, BRANCH),
        "sh -c make unit",
        "prose-owed.sh " + world.wt,
        wt + "push --force-with-lease=stack:%s origin %s:refs/heads/stack" % (STACK_SHA, REBASED)]), err


def spy_tracking(monkeypatch, world, answer=(0, "")):
    """queued_merge._track swapped for an in-process spy: each call records the worktree it was given, whether the
    stack had been pushed and how many pull request reads had been made by then."""
    tracked = []

    def track(worktree):
        tracked.append((worktree, bool(world.stack_pushed()), len(world.pulls)))
        return answer

    monkeypatch.setattr(queued_merge, "_track", track)
    return tracked


@pytest.mark.parametrize("stack_line", ["veri: stack branch: stack\n", "# no stack named\n"])
def test_a_join_calls_stack_pr_once_after_its_stack_push_and_merged_read_and_a_merge_with_no_stack_never_4172(
        tmp_path, fake_processes, monkeypatch, run_cli, stack_line):
    unmerged = {"state": "open", "merged": False, "head": {"sha": "9999999"}}
    stacked = stack_line.startswith("veri")
    world = World(tmp_path, stack_line=stack_line, **({} if stacked else dict(reads=(unmerged,) * 20, extra={
        "git -C <wt> merge-base --is-ancestor 9999999 origin/main": (1, "", "")}))).install(fake_processes, monkeypatch)
    tracked = spy_tracking(monkeypatch, world)

    code, _, err = join(run_cli, world)

    assert tracked == ([(world.wt, True, 2)] if stacked else []), err
    assert code == 0 or not stacked


@pytest.mark.parametrize("answer", [(2, "stack-pr: HTTP 502 from api.github.com; nothing opened\n"), (3, ""), (1, "a\nb\n")])
def test_a_failed_stack_pr_call_prints_one_stderr_line_naming_it_and_the_confirmed_join_still_exits_0_4172(
        tmp_path, fake_processes, monkeypatch, run_cli, answer):
    clean = World(tmp_path / "clean").install(fake_processes, monkeypatch)
    spy_tracking(monkeypatch, clean)
    _, _, quiet = join(run_cli, clean)
    world = World(tmp_path).install(fake_processes, monkeypatch)
    spy_tracking(monkeypatch, world, answer)

    code, _, err = join(run_cli, world)
    added = [line for line in err.splitlines() if line not in quiet.splitlines()]

    assert (code, len(added), "stack-pr.sh" in "".join(added), "exit %d" % answer[0] in "".join(added)) == (0, 1, True, True), err


def test_a_stack_pr_exit_3_after_a_join_is_said_plainly_as_the_stack_not_ahead_never_as_a_failure_4172(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path).install(fake_processes, monkeypatch)
    spy_tracking(monkeypatch, world, (3, "stack-pr: origin/stack is not ahead of origin/trunk; nothing opened\n"))

    code, _, err = join(run_cli, world)
    said = [line for line in err.splitlines() if "stack-pr.sh" in line]

    assert (code, len(said), "failed" in said[0], "not ahead" in said[0]) == (0, 1, False, True), err


def test_the_stack_pr_call_has_a_bound_of_its_own_a_hung_child_killed_and_answered_2_naming_the_limit_4172(
        tmp_path, fake_processes, monkeypatch):
    fake = fake_processes.answers({"stack-pr.sh": HANGS})
    monkeypatch.setattr(os, "killpg", lambda group, sig: [c.send_signal(sig) for c in fake.popens if c.pid == group])
    monkeypatch.setenv("VERI_GIT_NETWORK_TIMEOUT", "1")

    code, said = queued_merge._track(str(tmp_path))

    assert (code, "VERI_GIT_NETWORK_TIMEOUT" in said, [p.signals != [] for p in fake.popens]) == (2, True, [True])


def test_a_stack_push_refused_because_the_stack_moved_starts_again_from_the_fetch_and_never_forces(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, stack_pushes=(1, 0)).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    wt = "git -C %s " % world.wt
    rebases = [c for c in world.calls if c.startswith(wt + "rebase ")]
    forced = [c for c in world.stack_pushed() if " --force " in c or " -f " in c or " +" in c]
    assert (code, rebases, world.stack_pushed(), forced, world.stack[0]) == (0, [
        wt + "rebase origin/stack", wt + "rebase origin/stack"], [
        wt + "push --force-with-lease=stack:%s origin %s:refs/heads/stack" % (STACK_SHA, REBASED),
        wt + "push --force-with-lease=stack:%s origin %s:refs/heads/stack" % (MOVED_SHA, REBASED_AGAIN)],
        [], REBASED_AGAIN), err


def test_a_join_makes_no_ci_wait_and_no_merge_call_cuts_no_tag_and_closes_no_issue(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    forbidden = [c for c in world.calls if "wait-ci.sh" in c or "pr merge" in c or "/merge" in c or " tag" in c
                 or "issue close" in c or "issues/7" in c or "refs/tags/" in c]
    assert (code, forbidden) == (0, []), err


OPEN = {"state": "open", "merged": False}


def test_the_join_re_reads_the_pull_request_over_the_settle_window_and_exits_0_on_a_later_merged_read_2_naming_the_last_state(
        tmp_path, fake_processes, monkeypatch, run_cli):
    later = World(tmp_path / "later", reads=(OPEN, None, {"state": "closed", "merged": True})).install(fake_processes, monkeypatch)
    landed = join(run_cli, later)[0], len(later.pulls)
    never = World(tmp_path / "never", reads=(OPEN, OPEN, {"state": "weird\nstate", "merged": "true"})).install(
        fake_processes, monkeypatch)
    code, _, err = join(run_cli, never)

    assert (landed, code, len(never.pulls), "weird" in err, never.stack[0], never.stack_pushed()[-1:]) == (
        (0, 4), 2, 4, True, REBASED, ["git -C %s push --force-with-lease=stack:%s origin %s:refs/heads/stack" % (never.wt, STACK_SHA, REBASED)])


def released(world):
    return [c for c in world.calls if c.startswith("merge-lock.sh release")]


def pushed(world):
    return [c for c in world.calls if " push " in c]


def test_an_unticked_full_suite_line_does_not_block_a_join_and_any_other_unticked_line_exits_1_before_any_push(
        tmp_path, fake_processes, monkeypatch, run_cli):
    only_full = World(tmp_path / "full").install(fake_processes, monkeypatch)
    joined = join(run_cli, only_full)[0]
    other = World(tmp_path / "other", ledger="- [ ] a step ⟦criterion 1⟧\n- [ ] the full suite ⟦full-suite⟧\n").install(
        fake_processes, monkeypatch)
    code, _, err = join(run_cli, other)

    assert (joined, code, pushed(other), len(released(other)), "a step" in err) == (0, 1, [], 1, True)


def test_a_rebase_conflict_exits_1_aborting_the_rebase_pushing_nothing_and_releasing_the_lock(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, rebase=1).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    aborted = "git -C %s rebase --abort" % world.wt in world.calls
    assert (code, pushed(world), aborted, len(released(world))) == (1, [], True, 1), err


def test_a_red_fast_tier_on_the_rebased_tip_exits_1_pushing_nothing_to_the_stack_and_releasing_the_lock(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, fast=1).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, world.stack_pushed(), world.stack[0], len(released(world))) == (1, [], STACK_SHA, 1), err


def test_a_unit_owing_a_grade_on_the_rebased_tip_exits_1_pushing_nothing_to_the_stack_and_releasing_the_lock(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, owed=1).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, world.stack_pushed(), world.stack[0], len(released(world))) == (1, [], STACK_SHA, 1), err


@pytest.mark.parametrize("kind, world", [
    ("no fast tier", dict(extra={"detect-test-command.sh": (3, "", "")})),
    ("rebase refused without a conflict", dict(rebase=1, stopped=False)),
    ("an error raised mid-join", dict(extra={"git -C <wt> rev-parse --verify refs/remotes/origin/stack": OSError(5, "I/O error")})),
])
def test_a_join_that_gets_no_answer_exits_2_pushing_nothing_to_the_stack_and_releasing_the_lock(
        tmp_path, fake_processes, monkeypatch, run_cli, kind, world):
    world = World(tmp_path, **world).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, world.stack_pushed(), len(released(world))) == (2, [], 1), err


def test_a_stack_line_that_cannot_be_a_stack_exits_2_naming_it_before_the_lock_is_taken(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, stack_line="veri: stack branch:\n").install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    taken = [c for c in world.calls if c.startswith("merge-lock.sh")]
    assert (code, taken, "veri: stack branch:" in err) == (2, [], True), err


def test_after_a_joins_exit_0_the_runs_remote_branch_is_deleted_and_its_worktree_removed_the_main_clone_not_moved(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    wt = "git -C %s " % world.wt
    cleanup = [c for c in world.calls if "--delete" in c or "worktree remove" in c or "branch -D" in c]
    moved = [c for c in world.calls if "pull" in c or "merge --ff-only" in c or "reset" in c or "checkout" in c]
    after_release = world.calls.index(released(world)[0]) < world.calls.index(cleanup[0]) if cleanup else None
    assert (code, cleanup, moved, after_release) == (0, [
        wt + "push origin --delete %s --force-with-lease=%s:%s" % (BRANCH, BRANCH, REBASED),
        wt + "push origin --delete refs/veri/runs/7", wt + "worktree remove " + world.wt,
        "git -C %s branch -D %s" % (CLONE, BRANCH)], [], True), err


@pytest.mark.parametrize("stack_line, base", [("# no stack named\n", "stack"), ("veri: stack branch: stack\n", "trunk")])
def test_with_no_stack_named_or_a_pull_request_based_elsewhere_queued_merge_waits_on_ci_and_makes_the_merge_call_as_before(
        tmp_path, fake_processes, monkeypatch, run_cli, stack_line, base):
    unmerged = {"state": "open", "merged": False, "head": {"sha": "9999999"}}
    world = World(tmp_path, stack_line=stack_line, base=base, reads=(unmerged,) * 20,
                  extra={"git -C <wt> merge-base --is-ancestor 9999999 origin/main": (1, "", "")}).install(fake_processes, monkeypatch)

    join(run_cli, world)

    asked = [c for c in world.calls if "wait-ci.sh" in c or "pulls/7/merge" in c or "pr merge" in c]
    assert (bool(asked), world.stack_pushed()) == (True, [])


def test_a_commit_pushed_to_origins_run_branch_before_the_join_is_never_force_pushed_away_exit_2_nothing_pushed(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, foreign=True).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, pushed(world), world.rebased, len(released(world))) == (2, [], [], 1), err


def test_the_lease_is_pinned_once_to_the_run_branchs_pre_rebase_sha_even_when_the_join_starts_again(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, stack_pushes=(1, 0)).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    leases = [c.split()[4] for c in world.calls if "--force-with-lease=" + BRANCH in c and "--delete" not in c]
    assert (code, leases) == (0, ["--force-with-lease=%s:%s" % (BRANCH, ORIGIN_SHA),
                                  "--force-with-lease=%s:%s" % (BRANCH, REBASED)]), err


def test_a_stack_that_is_the_pull_requests_default_branch_as_github_reports_it_is_exit_2_before_the_lock_4171(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, pr_default="stack").install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, [c for c in world.calls if c.startswith("merge-lock.sh")], pushed(world)) == (2, [], []), err


@pytest.mark.parametrize("first", ["none", {"state": "open", "merged": False}, {"base": "stack"}, {"base": {"ref": 7}}])
def test_where_a_stack_is_named_an_unreadable_pull_request_base_is_exit_2_before_the_lock_never_the_merge_path(
        tmp_path, fake_processes, monkeypatch, run_cli, first):
    world = World(tmp_path, first=first).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, [c for c in world.calls if c.startswith("merge-lock.sh") or "wait-ci.sh" in c]) == (2, []), err


@pytest.mark.parametrize("state, merged, expected", [("closed", True, 3), ("closed", False, 2)])
def test_a_pull_request_already_merged_is_exit_3_and_one_closed_unmerged_exit_2_both_before_the_lock(
        tmp_path, fake_processes, monkeypatch, run_cli, state, merged, expected):
    first = {"state": state, "merged": merged, "head": {"sha": "9999999"},
             "base": {"ref": "stack", "repo": {"default_branch": "trunk"}}}
    world = World(tmp_path, first=first).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, [c for c in world.calls if c.startswith("merge-lock.sh")], pushed(world)) == (expected, [], []), err


def test_a_run_branch_delete_refused_under_its_lease_is_exit_2_naming_it_the_stack_left_as_pushed(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, extra={"git -C <wt> push origin --delete tdd/7-slug": (1, "", " ! [rejected] (stale info)\n"),
                                   "git -C <wt> ls-remote --heads origin refs/heads/tdd/7-slug":
                                       (0, "9999999\trefs/heads/tdd/7-slug\n", "")}).install(
        fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, "branch delete" in err, world.stack[0]) == (2, True, REBASED), err


@pytest.mark.parametrize("head", [{"ref": "tdd/8-y", "sha": ORIGIN_SHA}, {"ref": BRANCH, "sha": "2222222"}, {"ref": BRANCH},
                                  None])
def test_a_pull_request_whose_head_is_not_the_branch_and_tip_being_joined_is_exit_2_before_the_lock(
        tmp_path, fake_processes, monkeypatch, run_cli, head):
    first = {"state": "open", "merged": False, "head": head, "base": {"ref": "stack", "repo": {"default_branch": "trunk"}}}
    world = World(tmp_path, first=first).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, [c for c in world.calls if c.startswith("merge-lock.sh")], pushed(world)) == (2, [], []), err


def test_a_stack_deleted_on_origin_at_join_time_is_exit_2_and_never_recreated(tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path).install(fake_processes, monkeypatch)
    world.stack[0] = ""

    code, _, err = join(run_cli, world)

    assert (code, world.stack_pushed(), len(released(world))) == (2, [], 1), err


def test_a_stack_rewound_during_the_join_is_refused_by_the_lease_and_the_restart_rebases_onto_what_origin_holds_now(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, stack_pushes=(1, 0)).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    leases = [c.split()[4] for c in world.stack_pushed()]
    assert (code, leases) == (0, ["--force-with-lease=stack:" + STACK_SHA, "--force-with-lease=stack:" + MOVED_SHA]), err


def test_a_rebased_tip_that_does_not_descend_from_the_fetched_stack_is_never_pushed_to_it(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, extra={"git -C <wt> merge-base --is-ancestor " + STACK_SHA: (1, "", "")}).install(
        fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, world.stack_pushed()) == (2, []), err


@pytest.mark.parametrize("stack_line", ["# the stack line removed\n", "veri: stack branch: another\n"])
def test_a_run_whose_cut_recorded_a_stack_but_whose_claude_md_names_none_or_another_is_exit_2_before_the_lock(
        tmp_path, fake_processes, monkeypatch, run_cli, stack_line):
    world = World(tmp_path, stack_line=stack_line, base="trunk").install(fake_processes, monkeypatch)
    with open(world.wt + "/.tdd/issue-7-base", "w") as f:
        f.write("stack\n")

    code, _, err = join(run_cli, world)

    touched = [c for c in world.calls if c.startswith("merge-lock.sh") or "wait-ci.sh" in c or " push " in c]
    assert (code, touched, "stack" in err) == (2, [], True), err


@pytest.mark.parametrize("answer, expected", [((0, "", ""), 0), ((1, "", "error: remote ref does not exist\n"), 0),
                                              ((1, "", "fatal: unreachable\n"), 2)])
def test_a_joins_cleanup_deletes_origins_run_records_ref_a_missing_one_counting_as_deleted(
        tmp_path, fake_processes, monkeypatch, run_cli, answer, expected):
    world = World(tmp_path, extra={"git -C <wt> push origin --delete refs/veri/runs/7": answer}).install(
        fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    asked = "git -C %s push origin --delete refs/veri/runs/7" % world.wt in world.calls
    assert (code, asked, ("run records delete" in err) == (expected == 2)) == (expected, True, True), err


GONE = (1, "", "error: unable to delete 'tdd/7-slug': remote ref does not exist\n")


@pytest.mark.parametrize("listed, expected", [((0, "", ""), 0), ((0, "9999999\trefs/heads/tdd/7-slug\n", ""), 2),
                                              ((128, "", "fatal: unreachable\n"), 2)])
def test_a_run_branch_origin_already_lacks_counts_as_deleted_and_one_still_there_is_exit_2(
        tmp_path, fake_processes, monkeypatch, run_cli, listed, expected):
    world = World(tmp_path, extra={"git -C <wt> push origin --delete tdd/7-slug": GONE,
                                   "git -C <wt> ls-remote --heads origin refs/heads/tdd/7-slug": listed}).install(
        fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, ("branch delete" in err) == (expected == 2)) == (expected, True), err



def resets(world):
    return [c for c in world.calls if " reset --hard " in c]


def test_a_run_range_holding_a_merge_commit_is_exit_2_before_the_rebase_nothing_pushed(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, extra={"git -C <wt> rev-list --merges": (0, "abcdef0\n", "")}).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    rebased = [c for c in world.calls if " rebase " in c]
    assert (code, rebased, pushed(world), "merge commit" in err, "linear" in err) == (2, [], [], True, True), err


def test_a_rebased_tip_whose_tree_is_not_the_merge_of_the_run_and_the_stack_is_exit_2_naming_the_path_and_reset(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, extra={"git -C <wt> rev-parse --verify HEAD^{tree}": (0, "8888888\n", ""),
                                   "git -C <wt> diff --name-only": (0, "evil.txt\n", "")}).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, pushed(world), "evil.txt" in err, resets(world)) == (
        2, [], True, ["git -C %s reset --hard %s" % (world.wt, ORIGIN_SHA)]), err


@pytest.mark.parametrize("answer, said", [((128, "", "error: unknown option `write-tree'\n"), "merge-tree"),
                                          ((1, "7777777\nCONFLICT (content): a.py\n", ""), "conflict")])
def test_a_merge_tree_that_fails_or_reports_conflicts_is_exit_2_naming_it_never_would_lose(
        tmp_path, fake_processes, monkeypatch, run_cli, answer, said):
    world = World(tmp_path, extra={"git -C <wt> merge-tree --write-tree": answer}).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, pushed(world), said in err, "would lose" in err, len(resets(world))) == (2, [], True, False, 1), err


def test_a_reset_that_fails_after_a_refusal_names_the_exact_command_to_run(tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, extra={"git -C <wt> rev-parse --verify HEAD^{tree}": (0, "8888888\n", ""),
                                   "git -C <wt> reset --hard": (128, "", "fatal: unable to write\n")}).install(
        fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, "git -C %s reset --hard %s" % (world.wt, ORIGIN_SHA) in err) == (2, True), err



def test_after_a_refusal_past_the_rebase_head_is_the_pre_rebase_tip_and_a_second_join_meets_the_same_refusal(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, reads=(), extra={"git -C <wt> rev-parse --verify HEAD^{tree}": (0, "8888888\n", ""),
                                             "git -C <wt> diff --name-only": (0, "evil.txt\n", "")})
    world.first = {"state": "open", "merged": False, "head": {"ref": BRANCH, "sha": ORIGIN_SHA},
                   "base": {"ref": "stack", "repo": {"default_branch": "trunk"}}}
    world.install(fake_processes, monkeypatch)

    first = join(run_cli, world)
    head = world.answer("git -C %s rev-parse --verify HEAD" % world.wt)[1].strip()
    world.pulls.clear()
    second = join(run_cli, world)

    assert (first[0], head, second[0], "evil.txt" in second[2], "head reads" in second[2]) == (2, ORIGIN_SHA, 2, True, False)



@pytest.mark.parametrize("knob, named", [("fast_commits", FAST_COMMIT), ("fast_dirties", "r.txt")])
def test_a_fast_tier_that_commits_or_leaves_the_tree_dirty_is_exit_2_nothing_pushed_to_the_stack(
        tmp_path, fake_processes, monkeypatch, run_cli, knob, named):
    world = World(tmp_path)
    setattr(world, knob, True)
    world.install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, world.stack_pushed(), world.stack[0], named in err, REBASED in err) == (2, [], STACK_SHA, True, True), err


def test_the_clean_path_pushes_to_the_stack_the_sha_saved_right_after_the_content_check(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, [c.rsplit(" ", 1)[1] for c in world.stack_pushed()]) == (0, [REBASED + ":refs/heads/stack"]), err


def test_the_merge_commit_refusal_says_what_to_do(tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, extra={"git -C <wt> rev-list --merges": (0, "abcdef0\n", "")}).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    line = next(line for line in err.splitlines() if "merge commit" in line)
    assert (code, "must be linear" in line, "Rebase the run's branch onto origin/stack" in line, "join again" in line) == (
        2, True, True, True), err


def test_a_run_whose_cut_recorded_a_base_sha_rebases_onto_origin_stack_from_it_and_the_file_then_names_the_stack_it_rebased_onto(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path).install(fake_processes, monkeypatch)
    recorded = world.wt + "/.tdd/issue-7-base-sha"
    with open(recorded, "w") as f:
        f.write("4444444\n")

    code, _, err = join(run_cli, world)

    wt = "git -C %s " % world.wt
    rebases = [c for c in world.calls if c.startswith(wt + "rebase ")]
    checks = [c for c in world.calls if " merge-tree " in c]
    with open(recorded) as f:
        assert (code, rebases, checks, f.read()) == (0, [wt + "rebase --onto origin/stack 4444444"], [
            wt + "merge-tree --write-tree --merge-base=4444444 %s %s" % (ORIGIN_SHA, STACK_SHA)], STACK_SHA + "\n"), err


@pytest.mark.parametrize("text", ["", "not a sha\n", "4444444\n5555555\n"])
def test_a_base_sha_file_that_holds_no_one_sha_is_exit_2_naming_it_nothing_rebased_or_pushed_the_lock_freed(
        tmp_path, fake_processes, monkeypatch, run_cli, text):
    world = World(tmp_path).install(fake_processes, monkeypatch)
    with open(world.wt + "/.tdd/issue-7-base-sha", "w") as f:
        f.write(text)

    code, _, err = join(run_cli, world)

    rebases = [c for c in world.calls if c.startswith("git -C %s rebase " % world.wt)]
    assert (code, "issue-7-base-sha" in err, rebases, pushed(world), len(released(world))) == (2, True, [], [], 1), err
