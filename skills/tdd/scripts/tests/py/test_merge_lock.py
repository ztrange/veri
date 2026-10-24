"""In-process cases for veri/merge_lock.py, the module merge-lock.sh is a shim over."""
import importlib
import os
import shutil
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
def test_take_with_pid_records_that_pid_and_holder_prints_it(
        tmp_path, merge_lock, run_cli):
    scratch_git(tmp_path, "init", "-q", "-b", "main")
    pid = str(os.getpid())

    taken = run_cli(merge_lock, ["take", "--pid", pid], cwd=tmp_path)
    held = run_cli(merge_lock, ["holder"], cwd=tmp_path)

    assert (taken[0], held[0], held[1].split()[:1]) == (0, 0, [pid])


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


@pytest.mark.process("git init on a scratch repository, holder run against a lock directory with no record")
def test_holder_exits_2_when_the_lock_directory_exists_but_its_record_is_missing(
        tmp_path, merge_lock, run_cli):
    scratch_git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / ".tdd" / "merge.lock").mkdir(parents=True)

    held = run_cli(merge_lock, ["holder"], cwd=tmp_path)

    assert (held[0], held[1]) == (2, "")


@pytest.mark.process("git init on a scratch repository, take and release run from it")
def test_release_removes_the_lock_only_for_the_recorded_holder_and_release_force_removes_it_whoever_holds_it(
        tmp_path, merge_lock, run_cli):
    scratch_git(tmp_path, "init", "-q", "-b", "main")
    lock = tmp_path / ".tdd" / "merge.lock"
    run_cli(merge_lock, ["take", "--pid", "1"], cwd=tmp_path)

    stranger = run_cli(merge_lock, ["release", "--pid", "2"], cwd=tmp_path)
    kept = lock.is_dir()
    holder = run_cli(merge_lock, ["release", "--pid", "1"], cwd=tmp_path)
    removed = not lock.exists()
    shutil.rmtree(lock, ignore_errors=True)
    run_cli(merge_lock, ["take", "--pid", "1"], cwd=tmp_path)
    forced = run_cli(merge_lock, ["release", "--force", "--pid", "2"], cwd=tmp_path)

    assert (stranger[0], kept, holder[0], removed, forced[0], not lock.exists()) == (1, True, 0, True, 0, True)


@pytest.mark.process("git init on a scratch repository, release run against a lock with a missing or empty record")
def test_release_exits_2_and_leaves_the_lock_in_place_when_the_lock_exists_but_its_record_is_missing_or_empty(
        tmp_path, merge_lock, run_cli):
    scratch_git(tmp_path, "init", "-q", "-b", "main")
    lock = tmp_path / ".tdd" / "merge.lock"
    lock.mkdir(parents=True)

    missing = run_cli(merge_lock, ["release", "--pid", "1"], cwd=tmp_path)
    kept_missing = lock.is_dir()
    (lock / "holder").write_text("")
    empty = run_cli(merge_lock, ["release", "--pid", "1"], cwd=tmp_path)
    kept_empty = lock.is_dir()

    assert (missing[0], kept_missing, empty[0], kept_empty) == (2, True, 2, True)


@pytest.mark.process("git init on a scratch repository, take run without --pid")
def test_take_without_pid_exits_2_naming_pid_and_creates_no_lock(tmp_path, merge_lock, run_cli):
    scratch_git(tmp_path, "init", "-q", "-b", "main")

    bare = run_cli(merge_lock, ["take"], cwd=tmp_path)

    assert (bare[0], "--pid" in bare[2], (tmp_path / ".tdd" / "merge.lock").exists()) == (2, True, False)


@pytest.mark.process("git init on a scratch repository, take with --pid then release run without --pid or --force")
def test_release_without_pid_or_force_exits_2_naming_pid_and_removes_no_lock(tmp_path, merge_lock, run_cli):
    scratch_git(tmp_path, "init", "-q", "-b", "main")
    run_cli(merge_lock, ["take", "--pid", str(os.getpid())], cwd=tmp_path)

    bare = run_cli(merge_lock, ["release"], cwd=tmp_path)

    assert (bare[0], "--pid" in bare[2], (tmp_path / ".tdd" / "merge.lock").is_dir()) == (2, True, True)


@pytest.mark.process("git init on a scratch repository, take and holder run from it")
def test_holder_exits_1_and_prints_the_record_marked_stale_when_the_recorded_pid_is_alive_but_its_recorded_start_time_differs(
        tmp_path, merge_lock, run_cli):
    scratch_git(tmp_path, "init", "-q", "-b", "main")
    pid = str(os.getpid())
    run_cli(merge_lock, ["take", "--pid", pid], cwd=tmp_path)
    record = tmp_path / ".tdd" / "merge.lock" / "holder"
    host = socket.gethostname()
    shifted = [t if t in (pid, host) else "".join(str((int(c) + 1) % 10) if c.isdigit() else c for c in t)
               for t in record.read_text().split()]
    record.write_text(" ".join(shifted) + "\n")

    held = run_cli(merge_lock, ["holder"], cwd=tmp_path)

    assert (held[0], pid in held[1].split(), "stale" in held[1].lower()) == (1, True, True)


@pytest.mark.skipif(os.geteuid() == 0, reason="root owns pid 1, so it is not another user's")
@pytest.mark.process("git init on a scratch repository, take and holder run from it, ps reading pid 1's start time")
def test_holder_exits_0_and_prints_the_record_when_the_recorded_live_pid_belongs_to_another_user(
        tmp_path, merge_lock, run_cli):
    scratch_git(tmp_path, "init", "-q", "-b", "main")
    taken = run_cli(merge_lock, ["take", "--pid", "1"], cwd=tmp_path)

    held = run_cli(merge_lock, ["holder"], cwd=tmp_path)

    assert (taken[0], held[0], held[1].split()[:1], "stale" in held[1].lower(), held[2]) == (0, 0, ["1"], False, "")


@pytest.mark.process("git init on a scratch repository, take run from it with directory creation and renames observed")
def test_take_makes_the_lock_directory_visible_only_with_its_holder_record_complete(
        tmp_path, merge_lock, run_cli, monkeypatch):
    scratch_git(tmp_path, "init", "-q", "-b", "main")
    lock = tmp_path / ".tdd" / "merge.lock"
    seen = []

    def observing(real):
        def wrapper(*args, **kwargs):
            result = real(*args, **kwargs)
            if lock.is_dir():
                record = lock / "holder"
                seen.append(record.is_file() and len(record.read_text().split()) >= 3)
            return result
        return wrapper

    for name in ("mkdir", "rename", "replace"):
        monkeypatch.setattr(os, name, observing(getattr(os, name)))

    taken = run_cli(merge_lock, ["take", "--pid", str(os.getpid())], cwd=tmp_path)

    assert (taken[0], bool(seen), all(seen)) == (0, True, True)
