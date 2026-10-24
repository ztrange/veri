"""In-process cases for veri/merge_lock.py, the module merge-lock.sh is a shim over."""
import importlib
import os
import socket
import subprocess
import sys

import pytest


@pytest.fixture
def merge_lock():
    return importlib.import_module("veri.merge_lock")


def scratch_git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
                   capture_output=True, text=True, check=True)


@pytest.mark.process("git init and git worktree add on a scratch repository, holder run from both trees")
def test_holder_exits_3_with_nothing_on_stdout_when_no_lock_exists_in_the_main_tree_also_from_a_linked_worktree(
        tmp_path, merge_lock, run_cli):
    repo = tmp_path / "repo"
    repo.mkdir()
    scratch_git(repo, "init", "-q", "-b", "main")
    scratch_git(repo, "commit", "-q", "--allow-empty", "-m", "initial")
    linked = tmp_path / "linked"
    scratch_git(repo, "worktree", "add", "-q", "-b", "side", str(linked), "main")

    from_main = run_cli(merge_lock, ["holder"], cwd=repo)
    from_linked = run_cli(merge_lock, ["holder"], cwd=linked)

    assert (from_main[:2], from_linked[:2]) == ((3, ""), (3, ""))


@pytest.mark.process("git init and git worktree add on a scratch repository, take and holder run from the linked tree")
def test_take_from_a_linked_worktree_creates_the_lock_directory_in_the_main_tree_and_holder_names_the_live_pid_and_host(
        tmp_path, merge_lock, run_cli):
    repo = tmp_path / "repo"
    repo.mkdir()
    scratch_git(repo, "init", "-q", "-b", "main")
    scratch_git(repo, "commit", "-q", "--allow-empty", "-m", "initial")
    linked = tmp_path / "linked"
    scratch_git(repo, "worktree", "add", "-q", "-b", "side", str(linked), "main")
    pid = str(os.getpid())

    taken = run_cli(merge_lock, ["take", "--pid", pid], cwd=linked)
    held = run_cli(merge_lock, ["holder"], cwd=linked)

    assert (taken[0], (repo / ".tdd" / "merge.lock").is_dir(), held[0],
            pid in held[1].split(), socket.gethostname() in held[1]) == (0, True, 0, True, True)


@pytest.mark.process("git init on a scratch repository, take and holder run from it")
def test_take_without_pid_records_the_parent_process_of_the_caller_and_holder_prints_it(
        tmp_path, merge_lock, run_cli):
    scratch_git(tmp_path, "init", "-q", "-b", "main")
    parent = str(os.getppid())

    taken = run_cli(merge_lock, ["take"], cwd=tmp_path)
    held = run_cli(merge_lock, ["holder"], cwd=tmp_path)

    assert (taken[0], held[0], held[1].split()[:1]) == (0, 0, [parent])


@pytest.mark.process("git init on a scratch repository, and a child process started and reaped for a dead pid")
def test_holder_exits_1_and_prints_the_record_marked_stale_when_the_recorded_pid_is_dead_on_this_host(
        tmp_path, merge_lock, run_cli):
    scratch_git(tmp_path, "init", "-q", "-b", "main")
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    dead = str(child.pid)
    run_cli(merge_lock, ["take", "--pid", dead], cwd=tmp_path)

    held = run_cli(merge_lock, ["holder"], cwd=tmp_path)

    assert (held[0], dead in held[1].split(), socket.gethostname() in held[1], "stale" in held[1].lower()) == (
        1, True, True, True)
