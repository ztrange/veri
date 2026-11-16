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


def test_snapshot_digest_changes_with_one_files_content_and_with_the_marker_3964(tmp_path):
    tree = skill_tree(tmp_path / "veri-snapshot-x")
    (tree / ".veri-snapshot").write_text("/one/worktree\n")
    before = pinned_scripts.snapshot_digest(str(tree))

    (tree / ".veri-snapshot").write_text("/another/worktree\n")
    marker_only = pinned_scripts.snapshot_digest(str(tree))
    (tree / "scripts" / "status.sh").write_text("echo edited\n")
    edited = pinned_scripts.snapshot_digest(str(tree))

    assert (marker_only == before, edited == marker_only, "scripts/status.sh" in dict(before)) == (False, False, True)


def test_remove_tree_refuses_a_symlinked_tree_leaving_the_modes_under_its_target_as_they_were_3963(tmp_path):
    outside = skill_tree(tmp_path / "outside")
    pinned_scripts.take_bits(str(outside / "scripts"), 0o222)
    before = (outside / "scripts").stat().st_mode
    link = tmp_path / "pinned-scripts"
    link.symlink_to(outside)

    with pytest.raises(OSError):
        pinned_scripts.remove_tree(str(link))

    assert ((outside / "scripts").stat().st_mode, link.is_symlink()) == (before, True)


def test_make_read_only_leaves_the_mode_of_a_file_hard_linked_from_outside_the_tree_3963(tmp_path):
    outside = tmp_path / "outside.txt"
    outside.write_text("not the skill's\n")
    before = outside.stat().st_mode
    tree = skill_tree(tmp_path / "veri-snapshot-x")
    os.link(outside, tree / "scripts" / "linked.txt")

    pinned_scripts.make_read_only(str(tree))

    assert outside.stat().st_mode == before


@pytest.mark.parametrize("flip", ["plus-x-on-a-plain-file", "minus-x-on-a-script"])
def test_snapshot_digest_changes_with_a_files_executable_bit_3964(tmp_path, flip):
    tree = skill_tree(tmp_path / "veri-snapshot-x")
    script = tree / "scripts" / "status.sh"
    if flip == "minus-x-on-a-script":
        pinned_scripts.change_mode(str(script), lambda mode: mode | 0o111)
    before = pinned_scripts.snapshot_digest(str(tree))

    pinned_scripts.change_mode(str(script), lambda mode: mode ^ 0o111)

    assert pinned_scripts.snapshot_digest(str(tree)) != before


@pytest.mark.parametrize("change", ["added", "removed"])
def test_snapshot_digest_changes_when_an_empty_directory_is_added_or_removed_3964(tmp_path, change):
    tree = skill_tree(tmp_path / "veri-snapshot-x")
    if change == "removed":
        (tree / "empty").mkdir()
    before = pinned_scripts.snapshot_digest(str(tree))

    (tree / "empty").mkdir() if change == "added" else (tree / "empty").rmdir()

    assert pinned_scripts.snapshot_digest(str(tree)) != before


@pytest.mark.timeout(10)
@pytest.mark.parametrize("reader", ["snapshot_digest", "make_read_only"])
def test_a_fifo_in_the_tree_is_refused_without_being_opened_3964(tmp_path, reader):
    tree = skill_tree(tmp_path / "veri-snapshot-x")
    os.mkfifo(tree / "scripts" / "pipe")

    with pytest.raises(OSError):
        getattr(pinned_scripts, reader)(str(tree))


def test_snapshot_digest_refuses_a_file_with_a_second_hard_link_3964(tmp_path):
    outside = tmp_path / "outside.txt"
    outside.write_text("not the skill's\n")
    tree = skill_tree(tmp_path / "veri-snapshot-x")
    os.link(outside, tree / "scripts" / "linked.txt")

    with pytest.raises(OSError):
        pinned_scripts.snapshot_digest(str(tree))


def token_of(digest, path):
    """The token <digest> records for <path>, whichever form the digest takes."""
    entries = digest if isinstance(digest, list) else [tuple(reversed(line.split(" ", 1))) for line in digest.splitlines()]
    return dict(entries)[path]


def caught(recorded, tree):
    """Whether first_change reports <tree> changed against <recorded>: a path, or an OSError (fail closed)."""
    try:
        return pinned_scripts.first_change(recorded, str(tree)) is not None
    except OSError:
        return True


def injected_edit_of_a_script(tree, before):
    (tree / "scripts" / "status.sh").write_text("echo edited\n")
    (tree / ("scripts/sub\n%s scripts" % token_of(before, "scripts/status.sh"))).mkdir()
    (tree / ("scripts/sub\n%s scripts" % token_of(before, "scripts/status.sh")) / "status.sh\ndirectory scripts").mkdir()


def injected_edit_of_a_top_level_md(tree, before):
    (tree / "SKILL.md").write_text("# edited\n")
    (tree / ("scripts\n%s SKILL.md" % token_of(before, "SKILL.md"))).mkdir()


def injected_marker_rewrite(tree, before):
    (tree / ".veri-snapshot").write_text("/another/worktree\n")
    (tree / ("Z\n%s .veri-snapshot" % token_of(before, ".veri-snapshot"))).write_text("z\n")
    (tree / "Z").write_text("z\n")


@pytest.mark.parametrize("attack", [injected_edit_of_a_script, injected_edit_of_a_top_level_md, injected_marker_rewrite])
def test_an_edit_hidden_behind_a_name_holding_a_newline_is_still_a_change_3964(tmp_path, attack):
    tree = skill_tree(tmp_path / "veri-snapshot-x")
    (tree / ".veri-snapshot").write_text("/one/worktree\n")
    (tree / "Z").write_text("z\n")
    (tree / "scripts" / "sub").mkdir()
    before = pinned_scripts.snapshot_digest(str(tree))

    attack(tree, before)

    assert caught(before, tree)


def test_a_recorded_digest_naming_one_path_twice_is_a_change_3964(tmp_path):
    tree = skill_tree(tmp_path / "veri-snapshot-x")
    recorded = pinned_scripts.snapshot_digest(str(tree))

    assert caught([("SKILL.md", "0" * 64)] + recorded, tree)


def test_the_digest_file_form_reads_back_as_the_same_entries_and_refuses_any_other_text_3964(tmp_path):
    entries = pinned_scripts.snapshot_digest(str(skill_tree(tmp_path / "veri-snapshot-x")))

    with pytest.raises(ValueError):
        pinned_scripts.parse_digest("directory scripts\n")
    assert pinned_scripts.parse_digest(pinned_scripts.digest_text(entries)) == entries


def test_snapshot_digest_refuses_a_name_holding_a_newline_3964(tmp_path):
    tree = skill_tree(tmp_path / "veri-snapshot-x")
    (tree / "scripts" / "we\nird").write_text("q\n")

    with pytest.raises(OSError):
        pinned_scripts.snapshot_digest(str(tree))
