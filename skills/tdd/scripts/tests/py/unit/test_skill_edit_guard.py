"""skill_edit_guard.offending answers which paths an author changed beyond the unit it may edit."""
import pytest

import skill_edit_guard

DIFF = "git diff --name-only --no-renames base1"
UNTRACKED = "git ls-files --others --exclude-standard"


def repo(changed="", untracked=""):
    return {"git rev-parse": (0, "", ""), "git cat-file": (0, "", ""),
            DIFF: (0, changed, ""), UNTRACKED: (0, untracked, "")}


def test_offending_lists_changed_and_untracked_paths_beyond_the_unit_its_requirements_pins_and_ledgers(fake_processes, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake_processes.answers(repo(changed="skills/foo/FOO.md\nskills/foo/REQUIREMENTS.md\nkeep.py\nstray.py\n.tdd/issue-9.md\n",
                                untracked="pin.md\nnew.py\n"))

    assert skill_edit_guard.offending("skills/foo/FOO.md", "base1", ["pin.md", "keep.py"]) == ["stray.py", "new.py"]


def test_offending_is_empty_when_only_allowed_paths_changed(fake_processes, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake_processes.answers(repo(changed="skills/foo/FOO.md\n"))

    assert skill_edit_guard.offending("skills/foo/FOO.md", "base1", []) == []


def test_offending_refuses_a_base_that_is_not_a_commit_with_the_message_main_prints(fake_processes, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake_processes.answers({"git rev-parse": (1, "", "")})

    with pytest.raises(skill_edit_guard.Refusal, match="^skill-edit-guard.sh: base1 is not a commit$"):
        skill_edit_guard.offending("skills/foo/FOO.md", "base1", [])


def test_offending_takes_a_heading_unit_as_its_file_allowing_edits_to_the_file_and_naming_none_4210(fake_processes, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake = fake_processes.answers(repo(changed="skills/foo/FOO.md\nskills/foo/REQUIREMENTS.md\nstray.py\n"))

    assert skill_edit_guard.offending("skills/foo/FOO.md#Part A", "base1", []) == ["stray.py"]
    assert ["git", "cat-file", "-e", "base1:skills/foo/FOO.md"] in fake.argvs, fake.argvs


def test_main_takes_a_heading_unit_as_its_file_printing_only_the_stray_path_4210(fake_processes, run_cli, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake_processes.answers(repo(changed="skills/foo/FOO.md\nskills/foo/REQUIREMENTS.md\nstray.py\n"))

    assert run_cli(skill_edit_guard, ["skills/foo/FOO.md#Part A", "base1"]) == (1, "stray.py\n", "")
