"""In-process cases for veri/stack_carry.py, the module stack-carry.sh is a shim over (PRD 034.4b): the stack branch
stack-branch.sh names (stack_branch.named), git (git.git, git.network, git.default_branch) and the sibling scripts it runs
(stack_fix.script) are injected in-process, so no case starts a process."""
import importlib
import os
import subprocess

import pytest

TIP, CUT, NEW = "a" * 40, "c" * 40, "e" * 40
DEFAULT_TREE, NEW_TREE = "d" * 40, "f" * 40
LINE = "CLAUDE.md: the line 'veri: stack branch:' names no branch"


@pytest.fixture
def stack_carry():
    return importlib.import_module("veri.stack_carry")


class World:
    """A clone whose stack branch is <named> (an exception is raised by stack_branch.named) and whose default branch is
    `trunk`. Each git call (git.git, its cwd kept) is answered by the first key of <answers> found as a contiguous run of
    its arguments, (exit code, stdout, stderr); by default the happy carry-over: origin/stack is TIP, the old cut CUT is
    an ancestor of it and landed on origin/trunk (merging it there gives DEFAULT_TREE, origin/trunk's tree), the rebase
    in its worktree gives NEW with the tree NEW_TREE, and the KL21 merge-tree prints NEW_TREE. git.network answers 0
    unless <network> maps a first argument to (exit code, stdout, stderr). Sibling scripts answer <scripts>[name], else
    (0, ""). Every call is kept, in order, in <log>: ("git", cwd, *args), ("net", *args) and (script, *args)."""

    def __init__(self, monkeypatch, tmp_path, named="stack", answers=None, network=None, scripts=None):
        self.log, self.top = [], str(tmp_path)
        self.answers = dict({
            ("rev-parse", "--show-toplevel"): (0, self.top + "\n", ""),
            ("refs/remotes/origin/stack^{commit}",): (0, TIP + "\n", ""),
            ("cut^{commit}",): (0, CUT + "\n", ""),
            ("merge-base", "--is-ancestor"): (0, "", ""),
            ("merge-tree", "--write-tree", "origin/trunk", CUT): (0, DEFAULT_TREE + "\n", ""),
            ("origin/trunk^{tree}",): (0, DEFAULT_TREE + "\n", ""),
            ("rev-parse", "HEAD", "HEAD^{tree}"): (0, NEW + "\n" + NEW_TREE + "\n", ""),
            ("merge-tree", "--write-tree", "--merge-base=" + CUT): (0, NEW_TREE + "\n", ""),
        })
        self.answers.update(answers or {})
        network, scripts = network or {}, scripts or {}
        git = importlib.import_module("veri.git")

        def run_git(*args, cwd=None, **kwargs):
            self.log.append(("git", cwd) + args)
            for key, said in self.answers.items():
                if any(args[i:i + len(key)] == key for i in range(len(args) - len(key) + 1)):
                    return subprocess.CompletedProcess(["git", *args], *said)
            return subprocess.CompletedProcess(["git", *args], 0, "", "")

        def run_network(*args, cwd=None, limit_name=None):
            self.log.append(("net",) + args)
            return subprocess.CompletedProcess(["git", *args], *network.get(args[0], (0, "", "")))

        def answer(root):
            if isinstance(named, BaseException):
                raise named
            return named

        def script(name, *args, limit=None):
            self.log.append((name,) + args)
            return scripts.get(name, (0, ""))

        monkeypatch.setattr(git, "git", run_git)
        monkeypatch.setattr(git, "network", run_network)
        monkeypatch.setattr(git, "default_branch", lambda cwd=None, remote=True: "trunk")
        monkeypatch.setattr(importlib.import_module("veri.stack_branch"), "named", answer)
        monkeypatch.setattr(importlib.import_module("veri.stack_fix"), "script", script)

    def calls(self, first):
        return [call for call in self.log if call[0] == first]


@pytest.mark.parametrize("named, said", [
    (None, "stack-branch.sh exits 3: the repository's CLAUDE.md names no stack branch"),
    ("refused", "stack-branch.sh exits 2: " + LINE),
])
def test_exits_2_naming_stack_branch_sh_exit_and_its_line_when_it_does_not_exit_0_taking_no_lock(
        monkeypatch, tmp_path, run_cli, stack_carry, named, said):
    refused = importlib.import_module("veri.stack_branch").Refused(LINE) if named == "refused" else named
    world = World(monkeypatch, tmp_path, named=refused)

    code, out, err = run_cli(stack_carry, ["cut"])

    assert (code, out, said in err, world.calls("merge-lock.sh")) == (2, "", True, []), err


@pytest.mark.parametrize("argv", [[], ["cut", "more"], ["--now"]])
def test_any_argument_list_but_one_commit_exits_2_with_the_usage_line_taking_no_lock(
        monkeypatch, tmp_path, run_cli, stack_carry, argv):
    world = World(monkeypatch, tmp_path)

    code, out, err = run_cli(stack_carry, argv)

    assert (code, out, "usage: stack-carry.sh <old-cut>" in err, world.log) == (2, "", True, []), err


def released(world):
    return world.calls("merge-lock.sh")[-1:] == [("merge-lock.sh", "release", "--pid", str(os.getpid()))]


def test_a_failed_merge_lock_take_exits_2_with_nothing_fetched(monkeypatch, tmp_path, run_cli, stack_carry):
    world = World(monkeypatch, tmp_path, scripts={"merge-lock.sh": (2, "")})

    code, out, err = run_cli(stack_carry, ["cut"])

    assert (code, out, "merge-lock.sh take exits 2" in err, world.calls("net")) == (2, "", True, []), err


def test_a_failed_fetch_after_the_take_exits_2_and_frees_the_lock(monkeypatch, tmp_path, run_cli, stack_carry):
    world = World(monkeypatch, tmp_path, network={"fetch": (128, "", "fatal: unable to access origin\n")})

    code, out, err = run_cli(stack_carry, ["cut"])

    assert (code, out, "unable to access origin" in err, released(world)) == (2, "", True, True), err
    assert not [call for call in world.log if call[0] == "net" and call[1] != "fetch"], world.log


def worktrees(world):
    return [call for call in world.calls("git") if "worktree" in call]


@pytest.mark.parametrize("answers, said", [
    ({("merge-base", "--is-ancestor"): (1, "", "")}, "%s is not an ancestor of origin/stack at %s" % (CUT, TIP)),
    ({("merge-base", "--is-ancestor"): (128, "", "fatal: bad object\n")}, "fatal: bad object"),
    ({("refs/remotes/origin/stack^{commit}",): (1, "", "")}, "origin/stack does not resolve"),
    ({("refs/remotes/origin/stack^{commit}",): (128, "", "fatal: not a git repository\n")}, "not a git repository"),
    ({("cut^{commit}",): (1, "", "")}, "cut does not resolve"),
])
def test_an_old_cut_off_the_old_tip_or_a_git_read_with_no_answer_exits_2_rebasing_nothing_and_freeing_the_lock(
        monkeypatch, tmp_path, run_cli, stack_carry, answers, said):
    world = World(monkeypatch, tmp_path, answers=answers)

    code, out, err = run_cli(stack_carry, ["cut"])

    assert (code, out, said in err, released(world), worktrees(world)) == (2, "", True, True, []), err


@pytest.mark.parametrize("answers, said", [
    ({("merge-tree", "--write-tree", "origin/trunk", CUT): (0, "b" * 40 + "\n", "")},
     "origin/trunk has not landed the old cut %s" % CUT),
    ({("merge-tree", "--write-tree", "origin/trunk", CUT): (1, "b" * 40 + "\n", "")},
     "origin/trunk has not landed the old cut %s" % CUT),
    ({("merge-tree", "--write-tree", "origin/trunk", CUT): (128, "", "fatal: merge-tree broke\n")},
     "merge-tree broke"),
    ({("origin/trunk^{tree}",): (128, "", "fatal: no tree read\n")}, "no tree read"),
])
def test_an_old_cut_origin_default_has_not_landed_exits_2_rebasing_nothing_and_freeing_the_lock(
        monkeypatch, tmp_path, run_cli, stack_carry, answers, said):
    world = World(monkeypatch, tmp_path, answers=answers)

    code, out, err = run_cli(stack_carry, ["cut"])

    assert (code, out, said in err, released(world), worktrees(world)) == (2, "", True, True, []), err


def test_an_old_cut_that_is_the_old_tip_exits_3_nothing_to_carry_rebasing_nothing_and_freeing_the_lock(
        monkeypatch, tmp_path, run_cli, stack_carry):
    world = World(monkeypatch, tmp_path, answers={("refs/remotes/origin/stack^{commit}",): (0, CUT + "\n", "")})

    code, out, err = run_cli(stack_carry, ["cut"])

    assert (code, out, "nothing to carry" in err, released(world), worktrees(world)) == (3, "", True, True, []), err


def rebases(world):
    return [call for call in world.calls("git") if "rebase" in call]


def pushes(world):
    return [call for call in world.calls("net") if call[1] == "push"]


def test_carries_the_stack_by_rebase_onto_in_a_detached_worktree_under_tdd_removed_after_pushing_under_a_pinned_lease(
        monkeypatch, tmp_path, run_cli, stack_carry):
    world = World(monkeypatch, tmp_path)

    code, out, err = run_cli(stack_carry, ["cut"])

    added = [call for call in worktrees(world) if "add" in call]
    tree = added[0][-2] if added else ""
    assert (code, out.split(), released(world)) == (0, [NEW], True), err
    assert (added, os.path.dirname(os.path.dirname(tree)), os.path.exists(tree)) == (
        [("git", ".", "worktree", "add", "--detach", tree, TIP)], os.path.join(str(tmp_path), ".tdd"), False)
    assert rebases(world) == [("git", tree, "rebase", "--onto", "origin/trunk", CUT, TIP)]
    assert ("git", ".", "worktree", "remove", "--force", tree) in world.log
    assert pushes(world) == [("net", "push", "--force-with-lease=stack:" + TIP, "origin", NEW + ":refs/heads/stack")]


def test_a_rebase_conflict_exits_1_naming_the_file_the_rebase_aborted_its_worktree_removed_nothing_pushed(
        monkeypatch, tmp_path, run_cli, stack_carry):
    world = World(monkeypatch, tmp_path, answers={
        ("rebase", "--onto"): (1, "", "CONFLICT (content): Merge conflict in lib/a.txt\n"),
        ("diff", "--name-only", "--diff-filter=U"): (0, "lib/a.txt\n", "")})

    code, out, err = run_cli(stack_carry, ["cut"])

    tree = [call for call in worktrees(world) if "add" in call][0][-2]
    assert (code, out, "conflict" in err, "lib/a.txt" in err, released(world)) == (1, "", True, True, True), err
    assert (rebases(world)[-1], pushes(world), os.path.exists(tree)) == (("git", tree, "rebase", "--abort"), [], False)
    assert ("git", ".", "worktree", "remove", "--force", tree) in world.log


@pytest.mark.parametrize("said, code", [((0, "b" * 40 + "\n", ""), 1), ((1, "b" * 40 + "\n", ""), 1),
                                        ((128, "", "fatal: merge-tree broke\n"), 2)])
def test_nothing_is_pushed_unless_merge_tree_with_the_old_cut_as_base_prints_the_new_tips_tree(
        monkeypatch, tmp_path, run_cli, stack_carry, said, code):
    world = World(monkeypatch, tmp_path, answers={("merge-tree", "--write-tree", "--merge-base=" + CUT): said})

    exit_code, out, err = run_cli(stack_carry, ["cut"])

    named = ("b" * 40 in err and NEW_TREE in err) if code == 1 else "merge-tree broke" in err
    checked = ("git", ".", "merge-tree", "--write-tree", "--merge-base=" + CUT, "origin/trunk", TIP)
    assert (exit_code, out, named, checked in world.log, pushes(world), released(world)) == (
        code, "", True, True, [], True), err


@pytest.mark.parametrize("listed, code, said", [
    ((0, "b" * 40 + "\trefs/heads/stack\n", ""), 1, "origin's stack moved since the fetch, to " + "b" * 40),
    ((0, TIP + "\trefs/heads/stack\n", ""), 2, "stale info"),
    ((128, "", "fatal: no route\n"), 2, "no route"),
])
def test_a_leased_push_refused_because_origin_moved_exits_1_and_one_with_no_answer_exits_2_freeing_the_lock(
        monkeypatch, tmp_path, run_cli, stack_carry, listed, code, said):
    world = World(monkeypatch, tmp_path, network={"push": (1, "", "! [rejected] (stale info)\n"), "ls-remote": listed})

    exit_code, out, err = run_cli(stack_carry, ["cut"])

    assert (exit_code, out, said in err, len(pushes(world)), released(world)) == (code, "", True, 1, True), err
