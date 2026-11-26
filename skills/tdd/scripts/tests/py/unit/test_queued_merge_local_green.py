"""veri/queued_merge.py's --local-green (PRD 033.2b, OL20), in-process: run in an outage's main working tree, git,
merge-lock.sh, detect-test-command.sh and sh faked as processes."""
import inspect
import os
import re

import pytest
from veri import queued_merge

PID = str(os.getpid())
TIP = "3333333"


class LocalGreen:
    """A main working tree whose CLAUDE.md names the stack, `.tdd/github-outage` and `.tdd/stack-local-red` present as
    asked, the local stack at TIP, and every call made."""

    def __init__(self, tmp_path, outage=True, red=True, named=True, full=0, all_tier="make test\n", fail=(), take=0, release=0):
        self.clone = str(tmp_path / "clone")
        os.makedirs(os.path.join(self.clone, ".git"))
        os.makedirs(os.path.join(self.clone, ".tdd"))
        with open(os.path.join(self.clone, "CLAUDE.md"), "w") as f:
            f.write("veri: stack branch: stack\n" if named else "# no stack\n")
        if outage:
            open(os.path.join(self.clone, ".tdd", "github-outage"), "w").close()
        self.red = os.path.join(self.clone, ".tdd", "stack-local-red")
        if red:
            with open(self.red, "w") as f:
                f.write("abc1234\ntests/a.py::one\n")
        self.wt = os.path.join(self.clone, ".tdd", "local-green-%s" % PID)
        self.full, self.all_tier, self.fail, self.take, self.release = full, all_tier, fail, take, release

    def install(self, fake_processes):
        self.fake = fake_processes.answers({}, default=self.answer)
        return self

    def answer(self, line, **_):
        git = "git -C %s " % self.clone
        if any(line.startswith(git + failing) for failing in self.fail):
            return 128, "", "fatal: injected\n"
        if line == "git symbolic-ref --quiet --short refs/remotes/origin/HEAD":
            return 0, "origin/trunk\n", ""
        if line == git + "rev-parse --verify refs/heads/stack":
            return 0, TIP + "\n", ""
        if line.startswith("detect-test-command.sh --tier all"):
            return (0, self.all_tier, "") if self.all_tier else (3, "", "")
        if line == "sh -c make test":
            return self.full, "", ""
        if line.startswith("merge-lock.sh take"):
            return self.take, "", ""
        if line.startswith("merge-lock.sh release"):
            return self.release, "", ""
        return 0, "", ""

    @property
    def calls(self):
        return self.fake.calls

    def released(self):
        return [c for c in self.calls if c.startswith("merge-lock.sh")][-1:] == ["merge-lock.sh release --pid %s" % PID]


def green(run_cli, world, *argv):
    return run_cli(queued_merge, ["--local-green", *argv], cwd=world.clone)


def test_outside_an_outage_local_green_is_exit_2_with_no_call(tmp_path, fake_processes, run_cli):
    world = LocalGreen(tmp_path, outage=False).install(fake_processes)

    code, _, err = green(run_cli, world)

    assert (code, world.calls, os.path.exists(world.red)) == (2, [], True), err
    assert err.startswith("queued-merge: ") and "outage" in err, err


def test_local_green_with_no_stack_local_red_is_exit_3_taking_no_lock_and_running_nothing(tmp_path, fake_processes, run_cli):
    world = LocalGreen(tmp_path, red=False).install(fake_processes)

    code, _, err = green(run_cli, world)

    ran = [c for c in world.calls if c.startswith(("merge-lock.sh", "sh -c", "git -C"))]
    assert (code, ran, err.count("\n")) == (3, [], 1), err


def test_a_green_full_run_on_the_stacks_tip_removes_stack_local_red_and_exits_0(tmp_path, fake_processes, run_cli):
    world = LocalGreen(tmp_path).install(fake_processes)

    code, _, err = green(run_cli, world)

    git = "git -C %s " % world.clone
    seen = [c for c in world.calls if c.startswith(("merge-lock.sh", "sh -c", git + "worktree"))]
    assert (code, os.path.exists(world.red)) == (0, False), err
    assert seen == ["merge-lock.sh take --pid %s" % PID, git + "worktree add --detach %s %s" % (world.wt, TIP),
                    "sh -c make test", git + "worktree remove --force %s" % world.wt,
                    "merge-lock.sh release --pid %s" % PID], err


def test_a_red_full_run_keeps_stack_local_red_and_exits_1_the_worktree_removed_and_the_lock_freed(
        tmp_path, fake_processes, run_cli):
    world = LocalGreen(tmp_path, full=1).install(fake_processes)

    code, _, err = green(run_cli, world)

    removed = "git -C %s worktree remove --force %s" % (world.clone, world.wt) in world.calls
    assert (code, os.path.exists(world.red), removed, world.released()) == (1, True, True, True), err


@pytest.mark.parametrize("kind", ["argument", "unnamed", "add", "no command", "remove", "tip"])
def test_local_green_that_cannot_get_an_answer_is_exit_2_keeping_stack_local_red(tmp_path, fake_processes, run_cli, kind):
    world = LocalGreen(tmp_path, named=kind != "unnamed", all_tier="" if kind == "no command" else "make test\n",
                       fail={"add": ("worktree add",), "remove": ("worktree remove",),
                             "tip": ("rev-parse --verify refs/heads/stack",)}.get(kind, ())).install(fake_processes)

    code, _, err = green(run_cli, world, *(["stack"] if kind == "argument" else []))

    ran = [c for c in world.calls if c == "sh -c make test"]
    assert (code, os.path.exists(world.red) or kind == "remove", ran == [] or kind == "remove") == (2, True, True), err
    locked = [c for c in world.calls if c.startswith("merge-lock.sh")]
    assert (locked == []) if kind in ("argument", "unnamed") else world.released(), err


def test_a_failed_lock_take_exits_with_its_code_running_nothing(tmp_path, fake_processes, run_cli):
    world = LocalGreen(tmp_path, take=2).install(fake_processes)

    code, _, err = green(run_cli, world)

    ran = [c for c in world.calls if c.startswith(("sh -c", "git -C"))]
    assert (code, ran, os.path.exists(world.red)) == (2, [], True), err


def test_a_green_run_whose_lock_release_fails_is_exit_2(tmp_path, fake_processes, run_cli):
    world = LocalGreen(tmp_path, release=1).install(fake_processes)

    code, _, err = green(run_cli, world)

    assert (code, "releasing the merge lock failed" in err) == (2, True), err


def test_a_green_run_whose_freeze_file_cannot_be_removed_is_exit_2_naming_it(tmp_path, fake_processes, monkeypatch, run_cli):
    world = LocalGreen(tmp_path).install(fake_processes)

    def refuse(path):
        raise PermissionError(13, "Permission denied", path)

    monkeypatch.setattr(queued_merge.os, "remove", refuse)

    code, _, err = green(run_cli, world)

    assert (code, os.path.exists(world.red), world.released(), "stack-local-red" in err) == (2, True, True, True), err


NAMED = re.compile(r"ztrange|mario|ferreira|github\.com/\w|#[0-9]+|[\"'/](main|master)\b|[\"']stack[\"']"
                   r"|ready-for-agent|refactor-owed|author-read|[\"'](priority|bug|legacy|refactor)[\"']|gates",
                   re.IGNORECASE)


def test_the_skip_freeze_and_local_green_code_and_stack_red_name_no_repository_issue_branch_label_or_person():
    from veri import stack_red

    sources = {name: inspect.getsource(getattr(queued_merge, name)) for name in (
        "_skip_suite", "_freeze", "_failed_cases", "_local_green", "_green_tip", "_green_run")}
    for module in (stack_red,):
        with open(module.__file__, encoding="utf-8") as f:
            sources[os.path.basename(module.__file__)] = f.read()
    shims = os.path.dirname(os.path.dirname(queued_merge.__file__))
    with open(os.path.join(shims, "stack-red.sh"), encoding="utf-8") as f:
        sources["stack-red.sh"] = f.read()
    with open(os.path.join(shims, "queued-merge.sh"), encoding="utf-8") as f:
        # The shim's online-merge lines predate this and name the default branch; only the lines of this change count.
        sources["queued-merge.sh"] = "\n".join(line for line in f.read().splitlines() if re.search(
            r"skip-suite|local-green|Veri-Suite|stack-local-red|outage", line))

    named = ["%s:%d: %s" % (where, n, line) for where, text in sources.items()
             for n, line in enumerate(text.splitlines(), 1) if NAMED.search(line)]
    assert named == []


def test_an_error_raised_mid_suite_still_removes_the_worktree_it_added_and_frees_the_lock(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = LocalGreen(tmp_path).install(fake_processes)

    def boom(*args):
        raise RuntimeError("interrupted mid-suite")

    monkeypatch.setattr(queued_merge, "_green_run", boom)

    code, _, err = green(run_cli, world)

    removed = [c for c in world.calls if " worktree remove " in c]
    assert (code, removed, world.released(), os.path.exists(world.red)) == (
        2, ["git -C %s worktree remove --force %s" % (world.clone, world.wt)], True, True), err
