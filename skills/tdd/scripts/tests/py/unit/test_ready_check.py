"""In-process cases for veri/ready_check.py, the module ready-check.sh is a shim over: only the gh, git and
detect-test-command.sh process boundaries are faked."""
import importlib

import pytest

WORKFLOW = "on:\n  pull_request:\n  push:\n    branches: [main]\n"
ONE_TEST_FILE = "detect-test-command.sh --tier one test file"


@pytest.fixture(autouse=True)
def outside_this_repository(monkeypatch, tmp_path):
    """A row run in-process reads the repository of the working directory: a scratch one, never veri's own."""
    monkeypatch.chdir(tmp_path)


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


def test_issue_4087_ready_check_fails_the_one_test_file_row_naming_exit_2_when_detect_test_command_gives_no_answer(ready_check, run_cli, fake_processes, tmp_path):
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **{ONE_TEST_FILE: (2, "", "")})

    row = one_test_file_row(lines)
    assert row is not None and row.startswith("fail  one test file:"), lines
    assert 'exit 2 from detect-test-command.sh --tier "one test file"' in row, row
    assert (code, lines[-1]) == (1, "not ready — 1 rows to fix")


SSH_ORIGIN = (0, "git@github.com:o/r.git\n", "")
HTTPS_ORIGIN = (0, "https://github.com/o/r.git\n", "")


def user_headers(scopes=None):
    """`gh api -i user`'s answer: a status line and headers, X-Oauth-Scopes listing <scopes> unless None, then the body."""
    scope_line = "" if scopes is None else "X-Oauth-Scopes: %s\r\n" % scopes
    return 0, "HTTP/2.0 200 OK\r\nContent-Type: application/json\r\n%s\r\n{\"login\": \"o\"}" % scope_line, ""


def test_issue_4089_token_scopes_row_is_ok_when_the_header_lists_repo_and_origin_is_not_https(ready_check, fake_processes):
    fake_processes.answers({"gh api -i user": user_headers("gist, repo"), "git remote get-url origin": SSH_ORIGIN}, exact=True)

    assert ready_check.token_scopes_row() == ("token scopes", None)


def test_issue_4089_token_scopes_row_over_an_https_origin_fails_without_workflow_its_fix_refreshing_that_scope(ready_check, fake_processes):
    fake_processes.answers({"gh api -i user": user_headers("repo"), "git remote get-url origin": HTTPS_ORIGIN}, exact=True)

    assert ready_check.token_scopes_row() == ("token scopes", "gh auth refresh -s workflow")


def test_issue_4089_token_scopes_row_over_an_https_origin_lacking_both_scopes_names_each_in_its_fix(ready_check, fake_processes):
    fake_processes.answers({"gh api -i user": user_headers("gist"), "git remote get-url origin": HTTPS_ORIGIN}, exact=True)

    assert ready_check.token_scopes_row() == ("token scopes", "gh auth refresh -s repo,workflow")


def test_issue_4089_token_scopes_row_with_no_x_oauth_scopes_header_reads_not_verifiable(ready_check, fake_processes):
    fake_processes.answers({"gh api -i user": user_headers(None), "git remote get-url origin": SSH_ORIGIN}, exact=True)

    name, verdict = ready_check.token_scopes_row()

    assert (name, verdict) == ("token scopes", "not verifiable")
    assert verdict is ready_check.NOT_VERIFIABLE


NOT_FOUND = (1, '{"message": "Not Found", "status": "404"}', "gh: Not Found (HTTP 404)\n")


def test_issue_4089_the_label_row_for_veri_priority_label_is_ok_when_it_answers_and_fails_on_404_with_gh_label_create(ready_check, fake_processes, monkeypatch):
    monkeypatch.setenv("VERI_PRIORITY_LABEL", "urgent")
    fake_processes.answers({"gh api repos/{owner}/{repo}/labels/urgent": [(0, '{"name": "urgent"}', ""), NOT_FOUND]}, exact=True)

    assert ready_check.priority_label_row() == ("label urgent", None)
    assert ready_check.priority_label_row() == ("label urgent", "gh label create urgent")


def test_issue_4089_the_label_bug_row_is_ok_when_it_answers_and_fails_on_404_with_gh_label_create_bug(ready_check, fake_processes):
    fake_processes.answers({"gh api repos/{owner}/{repo}/labels/bug": [(0, '{"name": "bug"}', ""), NOT_FOUND]}, exact=True)

    assert ready_check.bug_label_row() == ("label bug", None)
    assert ready_check.bug_label_row() == ("label bug", "gh label create bug")


ACTIONS_RUNS = "gh api repos/{owner}/{repo}/actions/runs?per_page=1"
WITH_WORKFLOWS = {"git symbolic-ref": (0, "origin/main\n", ""), "git ls-tree": (0, ".github/workflows/ci.yml\n", "")}


def test_issue_4089_the_actions_read_row_is_ok_when_the_runs_call_exits_0_and_fails_otherwise(ready_check, fake_processes):
    fake_processes.answers({**WITH_WORKFLOWS, ACTIONS_RUNS: [(0, '{"workflow_runs": []}', ""), (1, "", "gh: Resource not accessible by integration (HTTP 403)\n")]})

    assert ready_check.actions_read_row() == ("actions read", None)
    name, fix = ready_check.actions_read_row()
    assert name == "actions read" and fix and "actions: read" in fix, fix
