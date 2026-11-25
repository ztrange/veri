"""`snapshot --step` cases for veri/tests_frozen.py that run git in a real repository under tmp_path."""
import importlib
import subprocess
from pathlib import Path

import pytest

from repo_builder import git, new_repo

STEP = "step one adds a case"
OWN = "tests/test_own.py"
OLD = "tests/test_old.py"
SHIM = Path(__file__).resolve().parents[2] / "tests-frozen.sh"


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


@pytest.fixture
def red(tmp_path, monkeypatch):
    """A repository whose HEAD holds lib.py and OLD, with Red's untracked OWN on disk."""
    for name in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(name, "t")
    for name in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(name, "t@t")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "lib.py").write_text("one\n")
    (tmp_path / OLD).write_text("def test_old():\n    assert True\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "lib.py", OLD)
    git(tmp_path, "commit", "-q", "-m", "base")
    (tmp_path / OWN).write_text("def test_own():\n    assert lib() == 2\n")
    return tmp_path


@pytest.mark.process("a real git repository under tmp_path, its objects written and diffed")
def test_snapshot_step_prints_a_commit_git_diff_against_which_shows_the_test_edits_and_no_production_change_4730(
        red, run_cli, tests_frozen):
    assert run_cli(tests_frozen, ["record", "--step", STEP, OWN], cwd=red)[0] == 0
    (red / "lib.py").write_text("two\n")
    (red / OWN).write_text("def test_own():\n    assert lib() in (1, 2)\n")
    (red / OLD).write_text("def test_old():\n    pass\n")

    code, out, err = run_cli(tests_frozen, ["snapshot", "--step", STEP], cwd=red)

    assert (code, err) == (0, "")
    shown = git(red, "diff", out.strip())
    assert sorted(git(red, "diff", "--name-only", out.strip()).split()) == [OLD, OWN]
    assert "-    assert lib() == 2" in shown and "+    assert lib() in (1, 2)" in shown
    assert "-    assert True" in shown and "+    pass" in shown
    assert "lib.py" not in shown


@pytest.mark.process("a real git repository under tmp_path, its objects written and diffed")
def test_snapshot_step_prints_a_commit_with_an_empty_diff_when_check_step_would_pass_4730(red, run_cli, tests_frozen):
    assert run_cli(tests_frozen, ["record", "--step", STEP, OWN], cwd=red)[0] == 0
    (red / "lib.py").write_text("two\n")

    code, out, err = run_cli(tests_frozen, ["snapshot", "--step", STEP], cwd=red)

    assert (code, err) == (0, "")
    assert git(red, "diff", out.strip()) == ""


@pytest.mark.process("the tests-frozen.sh shim, run in a real git repository under tmp_path")
def test_the_shims_snapshot_step_exits_2_with_nothing_on_stdout_on_a_missing_record_4730(red):
    ran = subprocess.run([str(SHIM), "snapshot", "--step", STEP], cwd=red, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL, timeout=20)

    assert (ran.returncode, ran.stdout) == (2, "")
    assert "missing" in ran.stderr
