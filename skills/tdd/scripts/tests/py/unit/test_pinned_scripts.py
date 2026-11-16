"""In-process cases for veri/pinned_scripts.py: the skill snapshot's tree on disk."""
import os

import pytest

import pinned_scripts

ROOT_IGNORES_WRITE_BITS = pytest.mark.skipif(os.geteuid() == 0, reason="uid 0 writes through missing write bits")


def skill_tree(top):
    (top / "scripts").mkdir(parents=True)
    (top / "SKILL.md").write_text("# skill\n")
    (top / "scripts" / "status.sh").write_text("#!/bin/sh\n")
    return top


@ROOT_IGNORES_WRITE_BITS
def test_make_read_only_makes_a_write_into_a_file_of_the_tree_fail_with_a_permission_error_3963(tmp_path):
    tree = skill_tree(tmp_path / "veri-snapshot-x")

    pinned_scripts.make_read_only(str(tree))

    with pytest.raises(PermissionError):
        (tree / "scripts" / "status.sh").write_text("edited\n")
