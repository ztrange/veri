"""Cases for the shared scratch tree: one committed tree prepared once, copied per case."""
import subprocess

import pytest


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


@pytest.mark.process("git rev-parse reading the HEAD of a copied scratch tree")
def test_a_case_copy_of_the_scratch_tree_is_a_repository_at_the_prepared_commit_and_writes_to_one_copy_reach_no_other(
        scratch_tree, scratch_copy):
    first, second = scratch_copy(), scratch_copy()

    (first / "only-in-first.txt").write_text("written\n")

    assert [git(first, "rev-parse", "HEAD") == git(scratch_tree, "rev-parse", "HEAD"),
            git(second, "rev-parse", "HEAD") == git(scratch_tree, "rev-parse", "HEAD"),
            (second / "only-in-first.txt").exists(), (scratch_tree / "only-in-first.txt").exists()] \
        == [True, True, False, False]
