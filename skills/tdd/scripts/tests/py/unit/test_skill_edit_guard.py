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
