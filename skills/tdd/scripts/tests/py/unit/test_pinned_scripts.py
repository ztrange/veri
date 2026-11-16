"""In-process cases for veri/pinned_scripts.py: the skill snapshot's tree on disk."""
import os

import pytest

import pinned_scripts

ROOT_IGNORES_WRITE_BITS = pytest.mark.skipif(os.geteuid() == 0, reason="uid 0 writes through missing write bits")


def skill_tree(top):
    (top / "scripts").mkdir(parents=True)
    (top / "SKILL.md").write_text("# skill\n")
    (top / "scripts" / "status.sh").write_text("echo status\n")
    return top


@ROOT_IGNORES_WRITE_BITS
def test_make_read_only_makes_a_write_into_a_file_of_the_tree_fail_with_a_permission_error_3963(tmp_path):
    tree = skill_tree(tmp_path / "veri-snapshot-x")

    pinned_scripts.make_read_only(str(tree))

    with pytest.raises(PermissionError):
        (tree / "scripts" / "status.sh").write_text("edited\n")


def test_make_read_only_leaves_the_write_bits_of_a_file_a_symlink_in_the_tree_names_outside_it_3963(tmp_path):
    outside = tmp_path / "outside.txt"
    outside.write_text("not the skill's\n")
    before = outside.stat().st_mode
    tree = skill_tree(tmp_path / "veri-snapshot-x")
    (tree / "scripts" / "link").symlink_to(outside)
    (tree / "dirlink").symlink_to(tmp_path)

    pinned_scripts.make_read_only(str(tree))

    assert (outside.stat().st_mode, tmp_path.stat().st_mode & 0o200) == (before, 0o200)


def test_snapshot_digest_changes_with_one_files_content_and_not_with_the_marker_3964(tmp_path):
    tree = skill_tree(tmp_path / "veri-snapshot-x")
    (tree / ".veri-snapshot").write_text("/one/worktree\n")
    before = pinned_scripts.snapshot_digest(str(tree))

    (tree / ".veri-snapshot").write_text("/another/worktree\n")
    marker_only = pinned_scripts.snapshot_digest(str(tree))
    (tree / "scripts" / "status.sh").write_text("echo edited\n")
    edited = pinned_scripts.snapshot_digest(str(tree))

    assert (marker_only == before, edited == before, "scripts/status.sh" in before) == (True, False, True)
