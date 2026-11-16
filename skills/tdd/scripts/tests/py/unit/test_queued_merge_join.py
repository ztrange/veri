"""veri/queued_merge.py joining a run to the stack branch (PRD 034.1c), in-process: merge-lock.sh, detect-test-command.sh,
prose-owed.sh, sh and git faked as processes; the pull request's state read through queued_merge._pull, spied in-process."""
import os

import pytest

from veri import queued_merge

PR = "https://github.com/o/r/pull/7"
BRANCH = "tdd/7-slug"
PID = str(os.getpid())
ORIGIN_SHA = "1111111"
STACK_SHA = "5555555"
MOVED_SHA = "6666666"
REBASED = "abc1234"
REBASED_AGAIN = "abc5678"
CLONE = "/clone"


class World:
    """The join's world: origin's stack and run branch, what each call answers, and every call made."""

    def __init__(self, tmp_path, ledger="- [x] a step ⟦criterion 1⟧\n- [ ] the full suite ⟦full-suite⟧ ⟦criterion 2⟧\n",
                 rebase=0, fast=0, owed=0, stack_pushes=(0,), reads=({"merged": True},), lock=0):
        self.wt = str(tmp_path / "wt")
        os.makedirs(self.wt + "/.tdd")
        with open(self.wt + "/CLAUDE.md", "w") as f:
            f.write("veri: stack branch: stack\n")
        with open(self.wt + "/.tdd/issue-7.md", "w") as f:
            f.write("# Plan for #7\n\n" + ledger)
        self.stack = [STACK_SHA]
        self.rebased = []
        self.rebase, self.fast, self.owed, self.lock = rebase, fast, owed, lock
        self.stack_pushes = list(stack_pushes)
        self.reads = list(reads)
        self.pulls = []

    def install(self, fake_processes, monkeypatch):
        first = {"state": "open", "merged": False, "base": {"ref": "stack"}, "head": {"sha": "9999999"}}

        def pull(repo, pr):
            self.pulls.append((repo, pr))
            if len(self.pulls) == 1:
                return first
            return self.reads.pop(0) if self.reads else None

        monkeypatch.setattr(queued_merge, "_pull", pull)
        self.fake = fake_processes.answers({}, default=self.answer)
        return self

    def answer(self, line, **_):
        wt = "git -C %s " % self.wt
        if line.startswith("merge-lock.sh take"):
            return self.lock, "", ""
        if line.startswith("merge-lock.sh"):
            return 0, "", ""
        if line == wt + "rev-parse --verify refs/remotes/origin/stack":
            return 0, self.stack[0] + "\n", ""
        if line == wt + "rev-parse --verify refs/remotes/origin/" + BRANCH:
            return 0, (self.rebased[-1] if self.rebased else ORIGIN_SHA) + "\n", ""
        if line == wt + "rev-parse --verify HEAD":
            return 0, (self.rebased[-1] if self.rebased else "0000000") + "\n", ""
        if line.startswith(wt + "merge-base --is-ancestor"):
            return 0, "", ""
        if line.startswith(wt + "rebase ") and "--abort" not in line:
            if self.rebase:
                return self.rebase, "", "CONFLICT (content): Merge conflict in a.py\n"
            self.rebased.append(REBASED if line.endswith(STACK_SHA) else REBASED_AGAIN)
            return 0, "", ""
        if line.startswith("detect-test-command.sh --tier fast"):
            return 0, "make unit\n", ""
        if line == "sh -c make unit":
            return self.fast, "", ""
        if line.startswith("prose-owed.sh"):
            return self.owed, "", ""
        if line.startswith(wt + "push origin ") and line.endswith(":refs/heads/stack"):
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
        wt + "fetch origin",
        wt + "rebase " + STACK_SHA,
        wt + "push --force-with-lease=%s:%s origin HEAD:refs/heads/%s" % (BRANCH, ORIGIN_SHA, BRANCH),
        "sh -c make unit",
        "prose-owed.sh " + world.wt,
        wt + "push origin %s:refs/heads/stack" % REBASED]), err


def test_a_stack_push_refused_because_the_stack_moved_starts_again_from_the_fetch_and_never_forces(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path, stack_pushes=(1, 0)).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    wt = "git -C %s " % world.wt
    rebases = [c for c in world.calls if c.startswith(wt + "rebase ")]
    forced = [c for c in world.stack_pushed() if "--force" in c or " +" in c]
    assert (code, rebases, world.stack_pushed(), forced, world.stack[0]) == (0, [
        wt + "rebase " + STACK_SHA, wt + "rebase " + MOVED_SHA], [
        wt + "push origin %s:refs/heads/stack" % REBASED, wt + "push origin %s:refs/heads/stack" % REBASED_AGAIN],
        [], REBASED_AGAIN), err


def test_a_join_makes_no_ci_wait_and_no_merge_call_cuts_no_tag_and_closes_no_issue(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    forbidden = [c for c in world.calls if "wait-ci.sh" in c or "pr merge" in c or "/merge" in c or " tag" in c
                 or "issue close" in c or "issues/7" in c or "refs/tags/" in c]
    assert (code, forbidden) == (0, []), err
