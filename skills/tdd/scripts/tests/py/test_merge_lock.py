"""In-process cases for veri/merge_lock.py, the module merge-lock.sh is a shim over."""
import importlib
import subprocess

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
