"""In-process cases for veri/ready_check.py, the module ready-check.sh is a shim over: only the gh, git and
detect-test-command.sh process boundaries are faked."""
import importlib

import pytest

WORKFLOW = "on:\n  pull_request:\n  push:\n    branches: [main]\n"
ONE_TEST_FILE = "detect-test-command.sh --tier one test file"


@pytest.fixture
def ready_check():
    return importlib.import_module("veri.ready_check")


def holding(**overrides):
    """The answers under which every row ready-check.sh prints holds, with <overrides> (command prefix → answer) on top."""
    table = {
        "git rev-parse --git-dir": (0, ".git\n", ""),
        "git symbolic-ref": (0, "origin/main\n", ""),
        "git ls-tree": (0, ".github/workflows/ci.yml\n", ""),
        "git show": (0, WORKFLOW, ""),
        "git ls-files": (0, "tests/test_x.py\n", ""),
        "git check-ignore": (0, "", ""),
        "gh auth status": (0, "", ""),
        "gh api repos/{owner}/{repo}": (0, '{"permissions": {"push": true}}', ""),
        "gh label list": (0, '[{"name": "ready-for-agent"}]', ""),
        "detect-test-command.sh": (0, "make test\n", ""),
    }
    table.update(overrides)
    return table


def check(ready_check, run_cli, fake_processes, tmp_path, **overrides):
    """ready-check.sh run over <tmp_path> under holding(**overrides): (exit code, stdout lines)."""
    fake_processes.answers(holding(**overrides))
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})
    return code, out.splitlines()


def test_issue_4087_ready_check_prints_an_ok_one_test_file_row_when_detect_test_command_finds_that_tier(ready_check, run_cli, fake_processes, tmp_path):
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **{ONE_TEST_FILE: (0, 'pytest "$1"\n', "")})

    assert "ok    one test file" in lines, lines
    assert (code, lines[-1]) == (0, "ready")


def one_test_file_row(lines):
    return next((line for line in lines if "one test file" in line), None)


def test_issue_4087_ready_check_fails_the_one_test_file_row_naming_the_claude_md_line_and_exits_1_when_that_tier_resolves_to_nothing(ready_check, run_cli, fake_processes, tmp_path):
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **{ONE_TEST_FILE: (3, "", "")})

    row = one_test_file_row(lines)
    assert row is not None and row.startswith("fail  one test file:"), lines
    assert "veri: one test file: <command>" in row and "CLAUDE.md" in row and '"$1"' in row, row
    assert (code, lines[-1]) == (1, "not ready — 1 rows to fix")
