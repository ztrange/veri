"""Cases for veri/full_tier_time.py that start a real process: git worktrees."""
import importlib
import subprocess

import pytest


@pytest.mark.process("a real git repository and a linked worktree under tmp_path")
def test_record_from_a_linked_worktree_lands_in_the_main_working_trees_tdd_dir_and_reads_back_from_the_main_tree(
        tmp_path, run_cli):
    full_tier_time = importlib.import_module("veri.full_tier_time")
    main, linked = tmp_path / "main", tmp_path / "linked"
    main.mkdir()

    def git(*args, cwd=main):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True,
                       capture_output=True)

    git("init", "-q")
    git("commit", "-q", "--allow-empty", "-m", "base")
    git("worktree", "add", "-q", "--detach", str(linked))

    recorded = run_cli(full_tier_time, ["--record", "42", "make test"], cwd=linked)
    read = run_cli(full_tier_time, ["make test"], cwd=main)

    assert (recorded[0], read) == (0, (0, "42\n", ""))


@pytest.mark.process("a real git repository and a linked worktree under tmp_path")
def test_record_from_a_subdirectory_of_the_main_tree_reads_back_from_a_subdirectory_of_a_linked_worktree(
        tmp_path, run_cli):
    full_tier_time = importlib.import_module("veri.full_tier_time")
    main, linked = tmp_path / "main", tmp_path / "linked"
    main.mkdir()

    def git(*args, cwd=main):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True,
                       capture_output=True)

    git("init", "-q")
    git("commit", "-q", "--allow-empty", "-m", "base")
    git("worktree", "add", "-q", "--detach", str(linked))
    main_sub, linked_sub = main / "a" / "b", linked / "c" / "d"
    main_sub.mkdir(parents=True)
    linked_sub.mkdir(parents=True)

    recorded = run_cli(full_tier_time, ["--record", "17", "make test"], cwd=main_sub)
    read = run_cli(full_tier_time, ["make test"], cwd=linked_sub)

    assert (recorded[0], read) == (0, (0, "17\n", ""))
