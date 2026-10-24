"""Cases for skill-edit-guard.sh that start the real entry point against a real git repository."""
import subprocess

import pytest

from conftest import SCRIPTS

GUARD = SCRIPTS / "skill-edit-guard.sh"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def guard(repo, unit, base):
    ran = subprocess.run([str(GUARD), unit, base], cwd=repo, capture_output=True, text=True)
    return ran.returncode, ran.stdout + ran.stderr


@pytest.mark.process("skill-edit-guard.sh run against a real git repository")
def test_skill_edit_guard_only_unit_and_its_requirements_changed_in_any_state_exit_0(tmp_path):
    repo = tmp_path / "guard"
    (repo / "skills/foo").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "skills/foo/FOO.md").write_text("prose\n")
    (repo / "skills/foo/REQUIREMENTS.md").write_text("| K1 | rule |\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: foo")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "skills/foo/FOO.md").write_text("prose two\n")
    git(repo, "commit", "-q", "-am", "edit prose")
    (repo / "skills/foo/REQUIREMENTS.md").write_text("| K1 | rule |\n| K2 | more |\n")
    git(repo, "add", "-A")
    (repo / "skills/foo/FOO.md").write_text("prose three\n")

    assert guard(repo, "skills/foo/FOO.md", base) == (0, "")


@pytest.mark.process("skill-edit-guard.sh run against a real git repository")
def test_skill_edit_guard_untracked_requirements_beside_the_unit_exit_0(tmp_path):
    repo = tmp_path / "guard"
    (repo / "skills/foo").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "skills/foo/FOO.md").write_text("prose\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: foo")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "skills/foo/REQUIREMENTS.md").write_text("| K1 | rule |\n")

    assert git(repo, "status", "--porcelain") == "?? skills/foo/REQUIREMENTS.md"
    assert guard(repo, "skills/foo/FOO.md", base) == (0, "")


@pytest.mark.process("skill-edit-guard.sh run with no arguments")
def test_skill_edit_guard_2232_no_arguments_prints_usage_naming_pin_files_and_exit_2(tmp_path):
    ran = subprocess.run([str(GUARD)], cwd=tmp_path, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: skill-edit-guard.sh <unit-file> <base-sha> [<pin-file>...]\n")


@pytest.mark.process("skill-edit-guard.sh run against a real git repository")
def test_skill_edit_guard_another_path_changed_exit_1_and_prints_it(tmp_path):
    repo = tmp_path / "guard"
    (repo / "skills/foo").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "skills/foo/FOO.md").write_text("prose\n")
    (repo / "skills/foo/OTHER.md").write_text("other\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: foo")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "skills/foo/FOO.md").write_text("prose two\n")
    (repo / "skills/foo/OTHER.md").write_text("other two\n")

    code, out = guard(repo, "skills/foo/FOO.md", base)

    assert code == 1
    assert "skills/foo/OTHER.md" in out
    assert "skills/foo/FOO.md" not in out


@pytest.mark.process("skill-edit-guard.sh run against a real git repository")
def test_skill_edit_guard_untracked_other_file_exit_1_and_prints_it(tmp_path):
    repo = tmp_path / "guard"
    (repo / "skills/foo").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "skills/foo/FOO.md").write_text("prose\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: foo")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "skills/foo/NOTES.md").write_text("stray\n")

    assert git(repo, "status", "--porcelain") == "?? skills/foo/NOTES.md"
    code, out = guard(repo, "skills/foo/FOO.md", base)

    assert code == 1
    assert "skills/foo/NOTES.md" in out


@pytest.mark.process("skill-edit-guard.sh run against a real git repository")
def test_skill_edit_guard_graded_file_changed_exit_1_and_prints_it(tmp_path):
    repo = tmp_path / "guard"
    (repo / "skills/foo").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "skills/foo/FOO.md").write_text("prose\n")
    (repo / "skills/foo/REQUIREMENTS.md").write_text("| K1 | rule |\n")
    (repo / "skills/foo/GRADED").write_text("skills/foo/FOO.md sig 2026-10-19 ev1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: foo")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "skills/foo/FOO.md").write_text("prose two\n")
    (repo / "skills/foo/REQUIREMENTS.md").write_text("| K1 | rule two |\n")
    (repo / "skills/foo/GRADED").write_text("skills/foo/FOO.md forged 2026-10-20 ev2\n")

    assert guard(repo, "skills/foo/FOO.md", base) == (1, "skills/foo/GRADED\n")


@pytest.mark.process("skill-edit-guard.sh run against a real git repository")
def test_skill_edit_guard_base_sha_not_a_commit_exit_2(tmp_path):
    repo = tmp_path / "guard"
    (repo / "skills/foo").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "skills/foo/FOO.md").write_text("prose\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: foo")

    code, _ = guard(repo, "skills/foo/FOO.md", "0123456789abcdef0123456789abcdef01234567")

    assert code == 2


@pytest.mark.process("skill-edit-guard.sh run against a real git repository")
def test_skill_edit_guard_unit_file_in_neither_base_nor_working_tree_exit_2(tmp_path):
    repo = tmp_path / "guard"
    (repo / "skills/foo").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "skills/foo/FOO.md").write_text("prose\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: foo")
    base = git(repo, "rev-parse", "HEAD")

    code, _ = guard(repo, "skills/foo/MISSING.md", base)

    assert code == 2


@pytest.mark.process("skill-edit-guard.sh run against a real git repository")
def test_skill_edit_guard_new_unit_with_its_new_requirements_exit_0(tmp_path):
    repo = tmp_path / "guard"
    (repo / "skills").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "skills/README.md").write_text("skills\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore: skills")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "skills/foo").mkdir()
    (repo / "skills/foo/FOO.md").write_text("prose\n")
    (repo / "skills/foo/REQUIREMENTS.md").write_text("| K1 | rule |\n")

    assert guard(repo, "skills/foo/FOO.md", base) == (0, "")


@pytest.mark.process("skill-edit-guard.sh run against a real git repository")
def test_skill_edit_guard_file_moved_onto_the_requirements_list_exit_1_and_prints_the_old_path(tmp_path):
    repo = tmp_path / "guard"
    (repo / "skills/foo").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "skills/foo/FOO.md").write_text("prose\n")
    (repo / "skills/foo/OTHER.md").write_text("| K1 | rule |\n| K2 | more |\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: foo")
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "mv", "skills/foo/OTHER.md", "skills/foo/REQUIREMENTS.md")

    assert guard(repo, "skills/foo/FOO.md", base) == (1, "skills/foo/OTHER.md\n")


@pytest.mark.process("skill-edit-guard.sh run against a real git repository")
def test_skill_edit_guard_2232_pin_file_named_after_base_sha_is_not_printed_and_an_unnamed_test_file_is(tmp_path):
    repo = tmp_path / "guard"
    (repo / "skills/foo").mkdir(parents=True)
    (repo / "tests").mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / "skills/foo/FOO.md").write_text("prose\n")
    (repo / "tests/test_pin.py").write_text("pin one\n")
    (repo / "tests/test_stray.py").write_text("stray one\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: foo")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "skills/foo/FOO.md").write_text("prose two\n")
    (repo / "tests/test_pin.py").write_text("pin two\n")
    (repo / "tests/test_stray.py").write_text("stray two\n")

    ran = subprocess.run([str(GUARD), "skills/foo/FOO.md", base, "tests/test_pin.py"], cwd=repo, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (1, "tests/test_stray.py\n")


@pytest.mark.process("skill-edit-guard.sh run against a real git repository")
def test_skill_edit_guard_2232_only_unit_its_requirements_and_a_named_pin_file_changed_exit_0_and_prints_nothing(tmp_path):
    repo = tmp_path / "guard"
    (repo / "skills/foo").mkdir(parents=True)
    (repo / "tests").mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / "skills/foo/FOO.md").write_text("prose\n")
    (repo / "skills/foo/REQUIREMENTS.md").write_text("| K1 | rule |\n")
    (repo / "tests/test_pin.py").write_text("pin one\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: foo")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "skills/foo/FOO.md").write_text("prose two\n")
    (repo / "skills/foo/REQUIREMENTS.md").write_text("| K1 | rule |\n| K2 | more |\n")
    (repo / "tests/test_pin.py").write_text("pin two\n")

    ran = subprocess.run([str(GUARD), "skills/foo/FOO.md", base, "tests/test_pin.py"], cwd=repo, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout, ran.stderr) == (0, "", "")


@pytest.mark.process("skill-edit-guard.sh run against a real git repository")
def test_skill_edit_guard_2287_untracked_ledger_bookkeeping_is_not_printed_and_an_untracked_stray_file_is(tmp_path):
    repo = tmp_path / "guard"
    (repo / "skills/foo").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "skills/foo/FOO.md").write_text("prose\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: foo")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "skills/foo/FOO.md").write_text("prose two\n")
    (repo / ".tdd").mkdir()
    (repo / ".tdd/issue-2287-added.md").write_text("")

    assert guard(repo, "skills/foo/FOO.md", base) == (0, "")

    (repo / "skills/foo/NOTES.md").write_text("stray\n")

    assert guard(repo, "skills/foo/FOO.md", base) == (1, "skills/foo/NOTES.md\n")
