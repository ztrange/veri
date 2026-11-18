"""veri/queued_merge.py joining a run to the local stack branch while `.tdd/github-outage` exists (PRD 033.2a), in-process:
git, merge-lock.sh, detect-test-command.sh, prose-owed.sh and sh faked as processes; the pull request read through
queued_merge._pull, spied in-process, so a read of it shows."""
import os

import pytest

from veri import queued_merge

PR = "https://github.com/o/r/pull/7"
BRANCH = "tdd/7-slug"
PID = str(os.getpid())
RUN_TIP = "1111111"
ORIGIN_STACK = "2222222"
LOCAL_STACK = "3333333"
REBASED = "4444444"
AMENDED = "5555555"
BASE_SHA = "6666666"
TREE = "7777777"
NETWORK = ("fetch", "push", "ls-remote", "pull", "remote")


class Offline:
    """An outage's world: the main clone holding `.tdd/github-outage`, a run's worktree under it whose CLAUDE.md names the
    stack and whose cut recorded it, origin's stack as last fetched and the local stack, and every call made."""

    def __init__(self, tmp_path, outage=True, base="stack\n", base_sha=None, local=LOCAL_STACK, rebase=0, fast=0,
                 owed=0, full=0, all_tier="make test\n", checked_out=None, default="trunk", ancestor=True, amend=0):
        self.clone = str(tmp_path / "clone")
        self.wt = os.path.join(self.clone, ".tdd", "wt", "7")
        admin = os.path.join(self.clone, ".git", "worktrees", "7")
        os.makedirs(admin)
        os.makedirs(self.wt + "/.tdd")
        with open(os.path.join(admin, "commondir"), "w") as f:
            f.write("../..\n")
        with open(self.wt + "/.git", "w") as f:
            f.write("gitdir: %s\n" % admin)
        with open(self.wt + "/CLAUDE.md", "w") as f:
            f.write("veri: stack branch: stack\n")
        with open(self.wt + "/.tdd/issue-7.md", "w") as f:
            f.write("# Plan for #7\n\n- [x] a step ⟦criterion 1⟧\n")
        if base is not None:
            with open(self.wt + "/.tdd/issue-7-base", "w") as f:
                f.write(base)
        if base_sha is not None:
            with open(self.wt + "/.tdd/issue-7-base-sha", "w") as f:
                f.write(base_sha + "\n")
        if outage:
            with open(os.path.join(self.clone, ".tdd", "github-outage"), "w") as f:
                f.write("")
        self.local, self.rebase, self.fast, self.owed, self.full = local, rebase, fast, owed, full
        self.all_tier, self.checked_out, self.default, self.ancestor, self.amend = (
            all_tier, checked_out, default, ancestor, amend)
        self.head = [RUN_TIP]
        self.pulls = []

    def install(self, fake_processes, monkeypatch):
        def pull(repo, pr):
            self.pulls.append(pr)
            return None

        monkeypatch.setattr(queued_merge, "_pull", pull)
        self.fake = fake_processes.answers({}, default=self.answer)
        return self

    def answer(self, line, **_):
        wt = "git -C %s " % self.wt
        if line == "git symbolic-ref --quiet --short refs/remotes/origin/HEAD":
            return (0, "origin/%s\n" % self.default, "") if self.default else (1, "", "")
        if line.startswith("git check-ref-format"):
            return 0, "", ""
        if line == wt + "rev-parse --verify refs/remotes/origin/stack":
            return 0, ORIGIN_STACK + "\n", ""
        if line == wt + "rev-parse --verify refs/heads/stack":
            return (0, self.local + "\n", "") if self.local else (128, "", "fatal: Needed a single revision\n")
        if line.startswith(wt + "branch stack "):
            self.local = line.split()[-1]
            return 0, "", ""
        if line == wt + "worktree list --porcelain":
            listed = "worktree %s\nHEAD %s\nbranch refs/heads/main\n\nworktree %s\nHEAD %s\nbranch refs/heads/%s\n" % (
                self.clone, "8" * 7, self.wt, self.head[-1], BRANCH)
            if self.checked_out:
                listed += "\nworktree %s\nHEAD %s\nbranch refs/heads/stack\n" % (self.checked_out, self.local)
            return 0, listed, ""
        if line.startswith(wt + "merge-base --is-ancestor %s " % ORIGIN_STACK):
            return (0 if self.ancestor else 1), "", ""
        if line.startswith(wt + "merge-base --is-ancestor"):
            return 0, "", ""
        if line.startswith(wt + "rev-list --merges"):
            return 0, "", ""
        if line == wt + "rev-parse --git-path rebase-merge":
            return 0, (str(self.wt) + "/stopped\n" if self.rebase else ""), ""
        if line.startswith(wt + "rebase ") and "--abort" not in line:
            if self.rebase:
                os.makedirs(self.wt + "/stopped", exist_ok=True)
                return 1, "", "CONFLICT (content): Merge conflict in a.py\n"
            self.head.append(REBASED)
            return 0, "", ""
        if " merge-tree --write-tree " in line or line.endswith("rev-parse --verify HEAD^{tree}"):
            return 0, TREE + "\n", ""
        if line == wt + "rev-parse --verify HEAD":
            return 0, self.head[-1] + "\n", ""
        if line == wt + "status --porcelain":
            return 0, "", ""
        if line.startswith("detect-test-command.sh --tier fast"):
            return 0, "make unit\n", ""
        if line.startswith("detect-test-command.sh --tier all"):
            return (0, self.all_tier, "") if self.all_tier else (3, "", "")
        if line == "sh -c make unit":
            return self.fast, "", ""
        if line == "sh -c make test":
            return self.full, "", ""
        if line.startswith("prose-owed.sh"):
            return self.owed, "", ""
        if line.startswith(wt + "commit --amend"):
            if self.amend:
                return self.amend, "", "fatal: amend refused\n"
            self.head.append(AMENDED)
            return 0, "", ""
        if line.startswith(wt + "update-ref refs/heads/stack "):
            self.local = line.split()[-2]
            return 0, "", ""
        if line.startswith("merge-lock.sh"):
            return 0, "", ""
        if line.endswith("--git-common-dir"):
            return 0, self.clone + "/.git\n", ""
        return 0, "", ""

    @property
    def calls(self):
        return self.fake.calls

    def networked(self):
        """Every call that talks to GitHub: a git network verb, gh, curl, stack-pr.sh or stack-red.sh."""
        return [c for c in self.calls if (c.startswith("git ") and set(c.split()[1:4]) & set(NETWORK))
                or c.startswith(("gh ", "curl ", "stack-pr.sh", "stack-red.sh"))]


def join(run_cli, world):
    return run_cli(queued_merge, [PR, world.wt, BRANCH, "-"])


def test_while_the_outage_file_exists_a_stacked_run_joins_the_local_stack_with_no_network_call_and_no_pr_read(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    wt = "git -C %s " % world.wt
    order = [c for c in world.calls if c.startswith(("merge-lock.sh", wt + "rebase", "sh -c", "prose-owed.sh",
                                                     wt + "update-ref"))]
    assert (code, world.networked(), world.pulls) == (0, [], []), err
    assert order[:4] == ["merge-lock.sh take --pid %s" % PID, wt + "rebase stack", "sh -c make unit",
                         "prose-owed.sh " + world.wt], err
    assert (world.local, order[-2:]) == (world.head[-1], [
        wt + "update-ref refs/heads/stack %s %s" % (world.head[-1], LOCAL_STACK), "merge-lock.sh release --pid %s" % PID]), err


def test_an_offline_join_whose_cut_recorded_the_stack_sha_replays_only_the_runs_commits_onto_the_local_stack(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, base_sha=BASE_SHA).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    rebases = [c for c in world.calls if c.startswith("git -C %s rebase" % world.wt)]
    assert (code, rebases) == (0, ["git -C %s rebase --onto stack %s" % (world.wt, BASE_SHA)]), err


def test_with_the_outage_file_but_no_recorded_base_the_join_reads_the_pull_request_as_before_and_joins_nothing_offline(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, base=None).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, world.pulls, world.local) == (2, [PR], LOCAL_STACK), err


def test_an_absent_local_stack_is_created_at_origins_stack_as_last_fetched_and_the_join_lands_on_it(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, local=None).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    wt = "git -C %s " % world.wt
    made = [c for c in world.calls if c.startswith((wt + "branch ", wt + "update-ref"))]
    assert (code, made) == (0, [wt + "branch stack " + ORIGIN_STACK,
                                wt + "update-ref refs/heads/stack %s %s" % (world.head[-1], ORIGIN_STACK)]), err


def test_a_local_stack_origins_stack_is_not_an_ancestor_of_is_exit_2_naming_both_shas_with_nothing_rebased(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, ancestor=False).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    rebased = [c for c in world.calls if " rebase " in c]
    assert (code, rebased, world.local) == (2, [], LOCAL_STACK), err
    assert ORIGIN_STACK in err and LOCAL_STACK in err, err


def test_a_local_stack_checked_out_in_a_worktree_is_exit_2_naming_that_worktree_with_nothing_rebased(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, checked_out="/elsewhere/tree").install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    rebased = [c for c in world.calls if " rebase " in c]
    assert (code, rebased, world.local, "/elsewhere/tree" in err) == (2, [], LOCAL_STACK, True), err


def test_a_stack_the_last_fetched_origin_head_names_as_the_default_branch_is_exit_2_asking_origin_nothing(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, default="stack").install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    rebased = [c for c in world.calls if " rebase " in c]
    assert (code, rebased, world.networked(), world.pulls) == (2, [], [], []), err
    assert err.startswith("queued-merge: ") and "default branch" in err, err


@pytest.mark.parametrize("kind", ["rebase", "fast", "owed"])
def test_a_rebase_conflict_a_red_fast_tier_or_a_unit_owing_a_grade_is_exit_1_with_the_stack_unmoved_and_the_lock_freed(
        tmp_path, fake_processes, monkeypatch, run_cli, kind):
    world = Offline(tmp_path, **{kind: 1}).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    wt = "git -C %s " % world.wt
    aborted = wt + "rebase --abort" in world.calls
    moved = [c for c in world.calls if c.startswith(wt + "update-ref")]
    assert (code, world.local, moved, aborted) == (1, LOCAL_STACK, [], kind == "rebase"), err
    assert [c for c in world.calls if c.startswith("merge-lock.sh")][-1] == "merge-lock.sh release --pid %s" % PID, err
