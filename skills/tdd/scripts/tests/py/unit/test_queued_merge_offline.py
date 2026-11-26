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
                 owed=0, full=0, all_tier="make test\n", checked_out=None, default="trunk", ancestor=True, amend=0,
                 gate_commits=False, move=0, fail=(), step="- [x] a step ⟦criterion 1⟧", rebased=REBASED, trailers="",
                 descends=True, merges="", differs=False, red=(3, ""), suites="", full_out=""):
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
            f.write("# Plan for #7\n\n%s\n" % step)
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
        self.gate_commits, self.move, self.fail = gate_commits, move, fail
        self.rebased, self.trailers, self.descends, self.merges, self.differs = (
            rebased, trailers, descends, merges, differs)
        self.head = [RUN_TIP]
        self.pulls = []
        self.red, self.reds = red, []
        self.suites, self.full_out = suites, full_out

    def install(self, fake_processes, monkeypatch):
        def pull(repo, pr):
            self.pulls.append(pr)
            return None

        def stack_red(worktree):
            self.reds.append((worktree, len(self.fake.calls)))
            return self.red

        monkeypatch.setattr(queued_merge, "_pull", pull)
        monkeypatch.setattr(queued_merge, "_stack_red", stack_red)
        self.fake = fake_processes.answers({}, default=self.answer)
        return self

    def answer(self, line, **_):
        wt = "git -C %s " % self.wt
        if any(line.startswith(wt + failing) for failing in self.fail):
            return 128, "", "fatal: injected\n"
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
        if line == wt + "merge-base --is-ancestor %s %s" % (LOCAL_STACK, AMENDED):
            return (0 if self.descends else 1), "", ""
        if line.startswith(wt + "merge-base --is-ancestor"):
            return 0, "", ""
        if line.startswith(wt + "rev-list --merges"):
            return 0, self.merges, ""
        if line.startswith(wt + "show -s --format=%(trailers:key=Veri-Joined"):
            return 0, self.trailers, ""
        if line.startswith(wt + "reset --hard "):
            self.head.append(line.split()[-1])
            return 0, "", ""
        if line == wt + "rev-parse --git-path rebase-merge":
            return 0, (str(self.wt) + "/stopped\n" if self.rebase else ""), ""
        if line.startswith(wt + "rebase ") and "--abort" not in line:
            if self.rebase:
                os.makedirs(self.wt + "/stopped", exist_ok=True)
                return 1, "", "CONFLICT (content): Merge conflict in a.py\n"
            self.head.append(self.rebased)
            return 0, "", ""
        if line.endswith("rev-parse --verify HEAD^{tree}") and self.differs:
            return 0, "8888888\n", ""
        if " merge-tree --write-tree " in line or line.endswith("rev-parse --verify HEAD^{tree}"):
            return 0, TREE + "\n", ""
        if line == wt + "rev-parse --verify HEAD":
            return 0, self.head[-1] + "\n", ""
        if line == wt + "status --porcelain":
            return 0, "", ""
        if line.startswith("detect-test-command.sh --tier fast"):
            return 0, "make unit\n", ""
        if line.startswith("detect-test-command.sh --tier all"):
            if isinstance(self.all_tier, int):
                return self.all_tier, "", "detect-test-command: no answer\n"
            return (0, self.all_tier, "") if self.all_tier else (3, "", "")
        if line == "sh -c make unit":
            return self.fast, "", ""
        if line == "sh -c make test":
            if self.gate_commits:
                self.head.append("9999999")
            return self.full, self.full_out, ""
        if line.startswith(wt + "log "):
            return (0, self.suites, "") if isinstance(self.suites, str) else (self.suites, "", "fatal: injected\n")
        if line.startswith("prose-owed.sh"):
            return self.owed, "", ""
        if line.startswith(wt + "commit --amend"):
            if self.amend:
                return self.amend, "", "fatal: amend refused\n"
            self.head.append(AMENDED)
            return 0, "", ""
        if line.startswith(wt + "update-ref refs/heads/stack "):
            if self.move:
                return self.move, "", "fatal: cannot lock ref 'refs/heads/stack'\n"
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


@pytest.mark.parametrize("full", [0, 1])
def test_the_all_tier_command_gates_the_rebased_tip_before_the_stack_moves_and_a_red_one_is_exit_1_stack_unmoved(
        tmp_path, fake_processes, monkeypatch, run_cli, full):
    world = Offline(tmp_path, full=full).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    wt = "git -C %s " % world.wt
    seen = [c for c in world.calls if c.startswith((wt + "rebase", "sh -c make test", wt + "update-ref"))]
    assert (code, seen[:2], world.local == LOCAL_STACK) == (full, [wt + "rebase stack", "sh -c make test"], bool(full)), err
    assert [c for c in world.calls if c.startswith("merge-lock.sh")][-1] == "merge-lock.sh release --pid %s" % PID, err


def test_with_no_all_tier_command_the_offline_join_is_not_gated_and_says_so_in_one_stderr_line(
        tmp_path, fake_processes, monkeypatch, run_cli):
    quiet = Offline(tmp_path / "gated").install(fake_processes, monkeypatch)
    _, _, said = join(run_cli, quiet)
    world = Offline(tmp_path, all_tier="").install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    added = [line for line in err.splitlines() if line not in said.splitlines()]
    gated = [c for c in world.calls if c.startswith("sh -c") and c != "sh -c make unit"]
    assert (code, gated, world.local == world.head[-1], len(added)) == (0, [], True, 1), err
    assert "not gated" in added[0], err


def test_an_all_tier_command_that_cannot_be_read_is_exit_2_with_the_stack_unmoved(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, all_tier=2).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, world.local) == (2, LOCAL_STACK), err


def test_the_offline_cleanup_removes_the_worktree_and_local_branch_and_leaves_the_remote_branch_and_run_records(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    cleaned = [c for c in world.calls if " worktree remove " in c or " branch -D " in c or "--delete" in c]
    assert (code, cleaned) == (0, ["git -C %s worktree remove %s" % (world.wt, world.wt),
                                   "git -C %s branch -D %s" % (world.clone, BRANCH)]), err


def test_the_rebased_tip_is_amended_with_one_veri_joined_trailer_before_the_stack_moves_and_exit_0_prints_the_amended_sha(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path).install(fake_processes, monkeypatch)

    code, out, err = join(run_cli, world)

    wt = "git -C %s " % world.wt
    amended = [argv for argv in world.fake.argvs if argv[3:5] == ["commit", "--amend"]]
    moved = [c for c in world.calls if c.startswith(wt + "update-ref")]
    assert (code, out, world.local) == (0, "joined offline, no tag %s\n" % AMENDED, AMENDED), err
    assert amended == [["git", "-C", world.wt, "commit", "--amend", "--no-edit", "--no-verify", "--allow-empty",
                        "--trailer", "Veri-Joined: %s %s" % (PR, BRANCH), "--trailer", "Veri-Suite: passed"]], err
    assert moved == [wt + "update-ref refs/heads/stack %s %s" % (AMENDED, LOCAL_STACK)], err


def test_an_amend_git_refuses_is_exit_2_with_the_stack_unmoved(tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, amend=128).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, world.local) == (2, LOCAL_STACK), err


def test_a_suite_that_commits_on_the_rebased_tip_is_exit_2_with_nothing_amended_and_the_stack_unmoved(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, gate_commits=True).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    amended = [c for c in world.calls if " commit --amend " in c]
    assert (code, amended, world.local) == (2, [], LOCAL_STACK), err


def test_a_stack_move_git_refuses_is_exit_2_and_prints_no_joined_line(tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, move=1).install(fake_processes, monkeypatch)

    code, out, err = join(run_cli, world)

    assert (code, out, world.local) == (2, "", LOCAL_STACK), err


@pytest.mark.parametrize("failing, local, base_sha", [
    ("worktree list", LOCAL_STACK, None),
    ("rev-parse --verify refs/remotes/origin/stack", LOCAL_STACK, None),
    ("rev-parse --verify refs/remotes/origin/stack", None, None),
    ("branch stack", None, None),
    ("rev-parse --verify HEAD", LOCAL_STACK, None),
    ("never", LOCAL_STACK, "not a sha"),
])
def test_a_git_call_the_offline_join_needs_that_fails_is_exit_2_with_nothing_joined(
        tmp_path, fake_processes, monkeypatch, run_cli, failing, local, base_sha):
    world = Offline(tmp_path, local=local, base_sha=base_sha, fail=(failing,)).install(fake_processes, monkeypatch)

    code, out, err = join(run_cli, world)

    moved = [c for c in world.calls if " update-ref " in c]
    assert (code, out, moved, err.startswith("queued-merge: ")) == (2, "", [], True), err
    assert [c for c in world.calls if c.startswith("merge-lock.sh")][-1] == "merge-lock.sh release --pid %s" % PID, err


def test_with_the_outage_file_and_a_recorded_base_naming_another_branch_nothing_joins_offline_and_the_join_refuses_as_before(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, base="trunk\n").install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    rebased = [c for c in world.calls if " rebase " in c]
    assert (code, rebased, world.local, "records the base" in err) == (2, [], LOCAL_STACK, True), err


def moves(world):
    return [c for c in world.calls if " commit --amend " in c or " update-ref " in c]


def test_a_retry_whose_rebased_tip_is_the_local_stacks_tip_carrying_this_runs_trailer_is_exit_3_with_nothing_amended(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, rebased=LOCAL_STACK, trailers="%s %s\n" % (PR, BRANCH)).install(fake_processes, monkeypatch)

    code, out, err = join(run_cli, world)

    assert (code, out, moves(world), world.local) == (3, "", [], LOCAL_STACK), err
    assert "already" in err and [c for c in world.calls if c.startswith("merge-lock.sh")][-1] == (
        "merge-lock.sh release --pid %s" % PID), err


@pytest.mark.parametrize("trailers", ["", "%s tdd/8-other\n" % PR])
def test_a_rebased_tip_that_is_the_local_stacks_tip_without_this_runs_trailer_is_exit_2_branch_put_back_nothing_amended(
        tmp_path, fake_processes, monkeypatch, run_cli, trailers):
    world = Offline(tmp_path, rebased=LOCAL_STACK, trailers=trailers).install(fake_processes, monkeypatch)

    code, out, err = join(run_cli, world)

    assert (code, out, moves(world), world.local, world.head[-1]) == (2, "", [], LOCAL_STACK, RUN_TIP), err


def test_an_amended_tip_that_does_not_descend_from_the_local_stack_is_exit_2_with_the_stack_unmoved(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, descends=False).install(fake_processes, monkeypatch)

    code, out, err = join(run_cli, world)

    moved = [c for c in world.calls if " update-ref " in c]
    assert (code, out, moved, world.local) == (2, "", [], LOCAL_STACK), err
    assert AMENDED in err and LOCAL_STACK in err, err


def test_an_offline_join_whose_ledger_has_an_unchecked_step_is_exit_1_with_nothing_rebased(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, step="- [ ] a step ⟦criterion 1⟧").install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    rebased = [c for c in world.calls if " rebase " in c]
    assert (code, rebased, world.local, "unchecked step" in err) == (1, [], LOCAL_STACK, True), err


def test_an_offline_join_whose_worktree_head_does_not_resolve_is_exit_2_with_nothing_rebased(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, fail=("rev-parse --verify HEAD",)).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    rebased = [c for c in world.calls if " rebase " in c]
    assert (code, rebased, world.local, "HEAD does not resolve" in err) == (2, [], LOCAL_STACK, True), err


def test_an_offline_join_whose_history_holds_a_merge_commit_is_exit_2_with_nothing_rebased(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, merges="abcdef0\n").install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    rebased = [c for c in world.calls if " rebase " in c]
    assert (code, rebased, world.local, "merge commit (abcdef0)" in err) == (2, [], LOCAL_STACK, True), err


def test_an_offline_rebased_tip_whose_content_is_not_the_merge_is_exit_2_branch_put_back_stack_unmoved(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, differs=True).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    gated = [c for c in world.calls if c.startswith("sh -c")]
    assert (code, moves(world), gated, world.local, world.head[-1]) == (2, [], [], LOCAL_STACK, RUN_TIP), err
    assert "not the merge" in err, err


def skip(run_cli, world, model="claude-opus-5-5", reason="the hardware is slow"):
    return run_cli(queued_merge, ["--skip-suite", model, reason, PR, world.wt, BRANCH, "-"])


@pytest.mark.parametrize("model, reason", [
    ("claude-sonnet-4-6", "the hardware is slow"),
    ("claude-haiku-4-5", "the hardware is slow"),
    ("", "the hardware is slow"),
    ("claude-opus-5-5", ""),
    ("claude-fable-1", "  "),
])
def test_skip_suite_with_an_id_naming_neither_opus_nor_fable_or_no_reason_is_exit_2_before_any_call(
        tmp_path, fake_processes, monkeypatch, run_cli, model, reason):
    world = Offline(tmp_path).install(fake_processes, monkeypatch)

    code, out, err = skip(run_cli, world, model, reason)

    assert (code, out, world.calls, world.pulls, world.local) == (2, "", [], [], LOCAL_STACK), err
    assert err.startswith("queued-merge: ") and "--skip-suite" in err, err


def test_skip_suite_missing_its_reason_and_the_run_arguments_is_exit_2_with_the_usage_before_any_call(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path).install(fake_processes, monkeypatch)

    code, _, err = run_cli(queued_merge, ["--skip-suite", "claude-opus-5-5", PR, world.wt, BRANCH, "-"])

    assert (code, world.calls, "usage:" in err) == (2, [], True), err


@pytest.mark.parametrize("outage, base", [(False, "stack\n"), (True, None), (True, "trunk\n")])
def test_skip_suite_outside_an_outage_or_on_a_join_that_is_not_offline_is_exit_2_with_no_lock_and_no_pr_read(
        tmp_path, fake_processes, monkeypatch, run_cli, outage, base):
    world = Offline(tmp_path, outage=outage, base=base).install(fake_processes, monkeypatch)

    code, out, err = skip(run_cli, world)

    locks = [c for c in world.calls if c.startswith("merge-lock.sh")]
    assert (code, out, locks, world.pulls, world.local) == (2, "", [], [], LOCAL_STACK), err
    assert "--skip-suite" in err and "offline" in err, err


def trailers(world):
    """The --trailer values of the offline join's one amend."""
    amended = [argv for argv in world.fake.argvs if argv[3:5] == ["commit", "--amend"]]
    assert len(amended) == 1, amended
    return [value for flag, value in zip(amended[0], amended[0][1:], strict=False) if flag == "--trailer"]


def test_with_no_all_tier_command_the_amend_writes_veri_suite_not_gated(tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, all_tier="").install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, trailers(world)) == (0, ["Veri-Joined: %s %s" % (PR, BRANCH), "Veri-Suite: not gated"]), err


@pytest.mark.parametrize("model", ["claude-opus-5-5", "Claude-Fable-1"])
def test_skip_suite_on_an_offline_join_runs_no_gate_and_the_amend_writes_veri_suite_skipped_with_the_id_and_reason(
        tmp_path, fake_processes, monkeypatch, run_cli, model):
    world = Offline(tmp_path, full=1).install(fake_processes, monkeypatch)

    code, out, err = skip(run_cli, world, model, "the  hardware\nis slow")

    gated = [c for c in world.calls if c.startswith(("sh -c", "detect-test-command.sh --tier all"))]
    assert (code, out, gated, world.local) == (0, "joined offline, no tag %s\n" % AMENDED, ["sh -c make unit"], AMENDED), err
    assert trailers(world) == ["Veri-Joined: %s %s" % (PR, BRANCH), "Veri-Suite: skipped %s the hardware is slow" % model], err


def test_the_offline_join_runs_stack_red_sh_in_the_worktree_before_its_rebase(tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    rebase = world.calls.index("git -C %s rebase stack" % world.wt)
    assert (code, [(wt, at < rebase) for wt, at in world.reds]) == (0, [(world.wt, True)]), err


def test_an_offline_join_while_stack_red_sh_exits_0_is_exit_1_naming_the_file_with_nothing_rebased_and_the_lock_freed(
        tmp_path, fake_processes, monkeypatch, run_cli):
    said = "abc1234 /clone/.tdd/stack-local-red local\n"
    world = Offline(tmp_path, red=(0, said)).install(fake_processes, monkeypatch)

    code, out, err = join(run_cli, world)

    rebased = [c for c in world.calls if " rebase " in c]
    assert (code, out, rebased, world.local) == (1, "", [], LOCAL_STACK), err
    assert "/clone/.tdd/stack-local-red" in err and "abc1234" in err and "--local-green" in err, err
    assert [c for c in world.calls if c.startswith("merge-lock.sh")][-1] == "merge-lock.sh release --pid %s" % PID, err


@pytest.mark.parametrize("red", [2, 1, 127])
def test_an_offline_join_while_stack_red_sh_exits_neither_0_nor_3_is_exit_2_with_nothing_rebased(
        tmp_path, fake_processes, monkeypatch, run_cli, red):
    world = Offline(tmp_path, red=(red, "")).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    rebased = [c for c in world.calls if " rebase " in c]
    assert (code, rebased, world.local, "stack-red.sh exited %d" % red in err) == (2, [], LOCAL_STACK, True), err


def local_red(world):
    path = os.path.join(world.clone, ".tdd", "stack-local-red")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return f.read()


SKIPPED = "passed\nskipped claude-opus-5-5 the hardware is slow\nnot gated\n"
FAILED = "....F.F\nFAILED tests/a.py::one - assert 1 == 2\nERROR tests/b.py::two\n2 failed, 5 passed in 3.1s\n"


def test_a_red_gate_while_a_skipped_join_sits_above_origins_stack_writes_stack_local_red_with_the_gated_sha_and_cases(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, full=1, suites=SKIPPED, full_out=FAILED).install(fake_processes, monkeypatch)

    code, out, err = join(run_cli, world)

    logged = [argv for argv in world.fake.argvs if argv[3:4] == ["log"]]
    assert (code, world.local, local_red(world)) == (1, LOCAL_STACK, "%s\ntests/a.py::one\ntests/b.py::two\n" % REBASED), err
    assert logged == [["git", "-C", world.wt, "log", "--format=%(trailers:key=Veri-Suite,valueonly,unfold)",
                       "refs/remotes/origin/stack..refs/heads/stack"]], err
    assert ".tdd/stack-local-red" in err and FAILED in out, err


@pytest.mark.parametrize("suites", ["", "passed\nnot gated\n\n"])
def test_a_red_gate_with_no_skipped_join_above_origins_stack_writes_nothing_and_is_exit_1(
        tmp_path, fake_processes, monkeypatch, run_cli, suites):
    world = Offline(tmp_path, full=1, suites=suites, full_out=FAILED).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, world.local, local_red(world)) == (1, LOCAL_STACK, None), err


def test_a_red_gate_whose_output_names_no_failed_case_writes_the_gated_sha_and_the_suites_exit(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, full=2, suites=SKIPPED, full_out="make: *** [test] Error 2\n").install(
        fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, local_red(world).splitlines()[0], "exit 2" in local_red(world)) == (1, REBASED, True), err


def test_a_red_gate_whose_range_read_fails_is_exit_2_writing_nothing(tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, full=1, suites=128, full_out=FAILED).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    assert (code, world.local, local_red(world), "Veri-Suite" in err) == (2, LOCAL_STACK, None, True), err


def test_a_green_gate_reads_no_range_and_writes_nothing(tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, suites=SKIPPED).install(fake_processes, monkeypatch)

    code, _, err = join(run_cli, world)

    logged = [c for c in world.calls if c.startswith("git -C %s log " % world.wt)]
    assert (code, logged, local_red(world)) == (0, [], None), err


def test_a_freeze_that_cannot_be_written_is_exit_2_naming_the_file(tmp_path, fake_processes, monkeypatch, run_cli):
    world = Offline(tmp_path, full=1, suites=SKIPPED, full_out=FAILED).install(fake_processes, monkeypatch)
    os.makedirs(os.path.join(world.clone, ".tdd", "stack-local-red"))

    code, _, err = join(run_cli, world)

    assert (code, world.local, "stack-local-red" in err and "nothing frozen" in err) == (2, LOCAL_STACK, True), err
