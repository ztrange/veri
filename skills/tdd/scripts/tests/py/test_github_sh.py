"""Cases for lib/github.sh, driven through one bash process each with gh faked on PATH."""
import os
import re
import shutil
import subprocess

import pytest

from conftest import SCRIPTS

LIB = SCRIPTS / "lib" / "github.sh"
REFUSAL = ("GitHub GraphQL is not available from Claude Code sessions; "
           "use the REST API (gh api repos/{owner}/{repo}/...)")
PROXY = ("gh: Numeric-ID repository paths (repositories/{id}/...) are not supported through this proxy. "
         "Use repos/{owner}/{repo}/... endpoints instead. (HTTP 403)")
THREE_PAGES = """\
[ "$1" = api ] || exit 1
case "$2" in
  *repositories/*) echo '%s' >&2; exit 1 ;;
  *repos/*page=1) echo '[{"number":1},{"number":2}]' ;;
  *repos/*page=2) echo '[{"number":3},{"number":4}]' ;;
  *repos/*page=3) echo '[{"number":5},{"number":6}]' ;;
  *repos/*page=*) echo '[]' ;;
  *) echo "stub gh: unexpected path $2" >&2; exit 1 ;;
esac
""" % PROXY


def run_lib(tmp_path, gh_body, call, driver=None):
    """(returncode, stdout, stderr, gh calls) of <call> run in bash after sourcing lib/github.sh,
    with an executable gh running <gh_body> first on PATH."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    calls = tmp_path / "calls"
    calls.write_text("")
    gh = bin_dir / "gh"
    gh.write_text('#!/bin/sh\necho "gh $*" >> "$CALLS"\n' + gh_body)
    gh.chmod(0o755)
    env = {"PATH": os.pathsep.join([str(bin_dir), os.path.dirname(shutil.which("bash")), "/usr/bin", "/bin"]),
           "CALLS": str(calls), "LIB": str(LIB)}
    if driver is not None:
        env["VERI_GH_DRIVER"] = driver
    ran = subprocess.run(["bash", "-c", 'source "$LIB"; ' + call], capture_output=True, text=True, env=env)
    return ran.returncode, ran.stdout, ran.stderr, calls.read_text().splitlines()


def numbers_in(stdout):
    return [int(n) for n in re.findall(r'"number": *(\d+)', stdout)]


@pytest.mark.process("bash sources lib/github.sh")
def test_gh_pr_ready_runs_gh_pr_ready_when_graphql_answers_and_never_calls_the_ccr_route(tmp_path):
    code, out, err, calls = run_lib(tmp_path, "exit 0\n", "gh_pr_ready 42", "auto")

    assert (code, out, err) == (0, "", "")
    assert calls == ["gh pr ready 42"]


@pytest.mark.process("bash sources lib/github.sh")
def test_gh_pr_ready_calls_the_ccr_route_over_gh_api_when_graphql_is_refused_with_the_403(tmp_path):
    body = 'case "$1" in\n  issue|pr|repo) echo "HTTP 403: %s" >&2; exit 1 ;;\nesac\nexit 0\n' % REFUSAL

    code, out, err, calls = run_lib(tmp_path, body, "gh_pr_ready 42", "auto")

    assert (code, out, err) == (0, "", "")
    assert calls == ["gh pr ready 42", "gh api -X POST repos/{owner}/{repo}/pulls/42/ccr/ready_for_review"]


@pytest.mark.process("bash sources lib/github.sh")
def test_gh_pr_ready_returns_2_when_gh_pr_ready_fails_with_a_404_and_when_the_ccr_route_fails_with_a_502(tmp_path):
    not_found = "HTTP 404: Not Found (https://api.github.com/graphql)"
    ordinary = run_lib(tmp_path, 'echo "%s" >&2; exit 1\n' % not_found, "gh_pr_ready 42", "auto")
    body = ('case "$1" in\n  issue|pr|repo) echo "HTTP 403: %s" >&2; exit 1 ;;\n'
            '  api) echo "HTTP 502: Bad Gateway" >&2; exit 1 ;;\nesac\nexit 1\n' % REFUSAL)
    ccr = run_lib(tmp_path, body, "gh_pr_ready 42", "auto")

    assert (ordinary[0], ordinary[1], not_found in ordinary[2]) == (2, "", True)
    assert ordinary[3][0] == "gh pr ready 42"
    assert (ccr[0], ccr[1], "HTTP 502: Bad Gateway" in ccr[2]) == (2, "", True)
    assert ccr[3][:2] == ["gh pr ready 42", "gh api -X POST repos/{owner}/{repo}/pulls/42/ccr/ready_for_review"]


@pytest.mark.process("bash sources lib/github.sh")
def test_gh_rest_list_pages_on_the_repos_path_when_the_proxy_refuses_repositories_paths(tmp_path):
    code, out, err, calls = run_lib(tmp_path, THREE_PAGES, "gh_rest_list 'repos/{owner}/{repo}/issues?per_page=2'")

    assert (code, numbers_in(out), err) == (0, [1, 2, 3, 4, 5, 6], "")
    assert not [call for call in calls if "repositories/" in call]


@pytest.mark.process("bash sources lib/github.sh")
def test_gh_rest_list_gives_a_path_with_no_query_string_page_n_as_its_query_string(tmp_path):
    body = ('case "$*" in\n'
            "  'api repos/{owner}/{repo}/pulls?page=1') echo '[{\"number\":1},{\"number\":2}]' ;;\n"
            "  'api repos/{owner}/{repo}/pulls?page=2') echo '[{\"number\":3}]' ;;\n"
            "  'api repos/{owner}/{repo}/pulls?page='*) echo '[]' ;;\n"
            "  *) echo 'gh: Not Found (HTTP 404)' >&2; exit 1 ;;\nesac\n")

    code, out, err, calls = run_lib(tmp_path, body, "gh_rest_list 'repos/{owner}/{repo}/pulls'")

    assert (code, numbers_in(out), err) == (0, [1, 2, 3], "")
    assert calls[0] == "gh api repos/{owner}/{repo}/pulls?page=1"


@pytest.mark.process("bash sources lib/github.sh")
def test_gh_list_falls_back_to_rest_paging_on_the_repos_path_when_gh_issue_list_is_refused(tmp_path):
    body = 'if [ "$1" != api ]; then echo "HTTP 403: %s" >&2; exit 1; fi\nshift\nset -- api "$@"\n' % REFUSAL + THREE_PAGES

    code, out, err, calls = run_lib(
        tmp_path, body, "gh_list 'repos/{owner}/{repo}/issues?per_page=2' issue list --state all --json number", "auto")

    assert (code, numbers_in(out), err) == (0, [1, 2, 3, 4, 5, 6], "")
    assert calls[0] == "gh issue list --state all --json number"
    assert not [call for call in calls if "repositories/" in call]


@pytest.mark.process("bash sources lib/github.sh")
def test_gh_rest_list_and_gh_list_return_2_when_page_2_fails_with_a_502_and_with_a_network_error(tmp_path):
    page_1 = "  'api repos/{owner}/{repo}/issues?per_page=2&page=1') echo '[{\"number\":1},{\"number\":2}]' ;;\n"
    rest = run_lib(
        tmp_path,
        'case "$*" in\n' + page_1 +
        "  'api repos/{owner}/{repo}/issues?per_page=2&page=2') echo 'gh: Bad Gateway (HTTP 502)' >&2; exit 1 ;;\n"
        "  *) echo 'stub gh: unexpected call' >&2; exit 1 ;;\nesac\n",
        "gh_rest_list 'repos/{owner}/{repo}/issues?per_page=2'")
    listed = run_lib(
        tmp_path,
        'case "$*" in\n' + page_1 +
        "  'api repos/{owner}/{repo}/issues?per_page=2&page=2') echo 'error connecting to api.github.com' >&2; exit 1 ;;\n"
        '  *) echo "HTTP 403: %s" >&2; exit 1 ;;\nesac\n' % REFUSAL,
        "gh_list 'repos/{owner}/{repo}/issues?per_page=2' issue list --state all --json number", "auto")

    assert (rest[0], numbers_in(rest[1]), rest[2]) == (2, [1, 2], "gh: Bad Gateway (HTTP 502)\n")
    assert (listed[0], numbers_in(listed[1]), listed[2]) == (2, [1, 2], "error connecting to api.github.com\n")
