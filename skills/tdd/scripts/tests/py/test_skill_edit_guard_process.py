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
def test_skill_edit_guard_no_arguments_prints_usage_and_exit_2(tmp_path):
    ran = subprocess.run([str(GUARD)], cwd=tmp_path, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: skill-edit-guard.sh <unit-file> <base-sha>\n")


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
