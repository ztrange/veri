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


def run_lib(tmp_path, gh_body, call, driver=None, env=None):
    """(returncode, stdout, stderr, calls) of <call> run in bash after sourcing lib/github.sh,
    with an executable gh running <gh_body> first on PATH, and a sleep and a python3 that only record."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    calls = tmp_path / "calls"
    calls.write_text("")
    gh = bin_dir / "gh"
    gh.write_text('#!/bin/sh\necho "gh $*" >> "$CALLS"\n' + gh_body)
    gh.chmod(0o755)
    for name, body in (("sleep", 'echo "sleep $*" >> "$CALLS"\n'),
                       ("python3", 'echo "python3 $*" >> "$CALLS"\ncat > /dev/null\necho rest-body\n')):
        fake = bin_dir / name
        fake.write_text("#!/bin/sh\n" + body)
        fake.chmod(0o755)
    env = {**(env or {}), "PATH": os.pathsep.join([str(bin_dir), os.path.dirname(shutil.which("bash")), "/usr/bin", "/bin"]),
           "CALLS": str(calls), "LIB": str(LIB)}
    if driver is not None:
        env["VERI_GH_DRIVER"] = driver
    ran = subprocess.run(["bash", "-c", 'set -o pipefail; source "$LIB"; ' + call], capture_output=True, text=True, env=env)
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


ISSUES = "'repos/{owner}/{repo}/issues'"
OPS = {
    "view": "gh_issue_view 7 body",
    "list": "gh_list %s issue list --json number" % ISSUES,
    "json": "gh_json issues.json %s issue list --json number" % ISSUES,
    "ready": "gh_pr_ready 42",
}
API_PAGES = """\
    case "$*" in *page=1) echo '[{"number":1}]' ;; *page=*) echo '[]' ;; *) echo '{}' ;; esac
    exit 0 ;;
"""
OLD_SHA = "8a7980e1" + "a" * 32
NEW_SHA = "a245e8b0" + "b" * 32


def rest_stub(rest_answers, graphql_reply):
    """A gh whose issue and pr routes print <graphql_reply> and whose api route answers, or fails with a 502."""
    fail = "" if rest_answers else "echo 'gh: Bad Gateway (HTTP 502)' >&2; exit 1"
    return ("case \"$1\" in\n  issue|pr) echo " + graphql_reply + "; exit 0 ;;\n  api)\n    " + fail + "\n"
            + API_PAGES + "esac\nexit 1\n")


def started(calls, command):
    return [call for call in calls if call.startswith(command + " ")]


def reads_of_pr_42(calls):
    return [call for call in calls if re.match(r"gh api .*pulls/42([^/]|$)", call)]


@pytest.mark.process("bash sources lib/github.sh")
def test_with_the_driver_unset_every_graphql_operation_runs_only_gh_api_and_returns_2_when_it_fails(tmp_path):
    for rest_answers in (True, False):
        for op, call in OPS.items():
            body = rest_stub(rest_answers, "'[]'")

            code, _, _, calls = run_lib(tmp_path, body, call)

            where = (op, rest_answers)
            assert code == (0 if rest_answers else 2), where
            assert started(calls, "gh api"), where
            assert not started(calls, "gh issue") + started(calls, "gh pr"), where


@pytest.mark.process("bash sources lib/github.sh")
def test_with_the_driver_rest_every_graphql_operation_answers_from_gh_api_alone_and_passes_its_stderr_on(tmp_path):
    answers = {"view": "rest-body", "list": '[{"number":1}]', "json": '[{"number":1}]', "ready": ""}
    for rest_answers in (True, False):
        for op, call in OPS.items():
            body = rest_stub(rest_answers, "graphql-answer")

            code, out, err, calls = run_lib(tmp_path, body, call, "rest")

            where = (op, rest_answers)
            assert code == (0 if rest_answers else 2), where
            assert started(calls, "gh api"), where
            assert not started(calls, "gh issue") + started(calls, "gh pr"), where
            if rest_answers:
                assert out.strip() == answers[op], where
            else:
                assert "gh: Bad Gateway (HTTP 502)" in err, where


@pytest.mark.process("bash sources lib/github.sh")
def test_with_the_driver_graphql_every_graphql_operation_returns_2_without_gh_api_when_graphql_fails(tmp_path):
    for graphql_answers in (True, False):
        for op, call in OPS.items():
            fail = "" if graphql_answers else 'echo "%s" >&2; exit 1' % REFUSAL
            body = ("case \"$1\" in\n  issue|pr)\n    " + fail + "\n    echo graphql-answer; exit 0 ;;\n  api)\n"
                    + API_PAGES + "esac\nexit 1\n")

            code, out, _, calls = run_lib(tmp_path, body, call, "graphql")

            where = (op, graphql_answers)
            assert code == (0 if graphql_answers else 2), where
            assert started(calls, "gh issue") + started(calls, "gh pr"), where
            assert not started(calls, "gh api"), where
            if graphql_answers:
                assert out.strip() == "graphql-answer", where


@pytest.mark.process("bash sources lib/github.sh")
def test_operations_with_no_graphql_route_run_gh_api_and_no_gh_issue_or_pr_under_every_driver(tmp_path):
    body = "case \"$1\" in\n  issue|pr) echo graphql-answer; exit 0 ;;\n  api)\n" + API_PAGES + "esac\nexit 1\n"
    body_file = tmp_path / "body"
    body_file.write_text("a new body\n")
    ops = {"edit": "gh_issue_edit 7 '%s'" % body_file,
           "rest_list": "gh_rest_list %s" % ISSUES,
           "json": "gh_json issues.json %s" % ISSUES}
    for driver in (None, "auto", "rest", "graphql"):
        for op, call in ops.items():
            code, _, _, calls = run_lib(tmp_path, body, call, driver)

            where = (op, driver)
            assert code == 0, where
            assert started(calls, "gh api"), where
            assert not started(calls, "gh issue") + started(calls, "gh pr"), where


@pytest.mark.process("bash sources lib/github.sh")
def test_with_the_driver_empty_or_unknown_every_gh_function_starts_no_gh_and_names_the_variable_and_value(tmp_path):
    body = "case \"$1\" in\n  issue|pr|api) echo '[]'; exit 0 ;;\nesac\nexit 1\n"
    ops = {**OPS, "json_rest": "gh_json issues.json %s" % ISSUES,
           "edit": "gh_issue_edit 7 '%s'" % (tmp_path / "body"),
           "rest_list": "gh_rest_list %s" % ISSUES}
    for driver in ("", "REST", "gql"):
        for op, call in ops.items():
            code, out, err, calls = run_lib(tmp_path, body, call, driver)

            where = (op, driver)
            assert code == 2, where
            assert out == "", where
            assert not started(calls, "gh"), where
            assert len(err.splitlines()) == 1, where
            assert "VERI_GH_DRIVER" in err and "'%s'" % driver in err, where


@pytest.mark.process("bash sources lib/github.sh")
def test_with_veri_gh_json_set_gh_json_prints_the_fixture_and_starts_no_gh_or_python3_under_every_driver(tmp_path):
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    (fixtures / "prs.json").write_text('[{"number":7,"title":"A thing"}]\n')
    body = "echo '[{\"number\":99}]'\n"
    path = "'repos/{owner}/{repo}/pulls?state=open'"
    for driver in (None, "auto", "rest", "graphql"):
        for call in ("gh_json prs.json %s pr list --json number,title" % path, "gh_json prs.json %s" % path):
            code, out, _, calls = run_lib(tmp_path, body, call, driver, {"VERI_GH_JSON": str(fixtures)})

            where = (call, driver)
            assert code == 0, where
            assert out == '[{"number":7,"title":"A thing"}]\n', where
            assert calls == [], where


def pr_head_stub(tmp_path, answers):
    """A gh whose pulls/42 read prints the shell expression <answers> and counts its reads in $READS."""
    reads = tmp_path / "reads"
    reads.write_text("")
    return ('case "$*" in\n  *pulls/42/ccr/ready_for_review*) exit 0 ;;\n'
            '  *pulls/42*) echo x >> "$READS"; n=$(wc -l < "$READS"); ' + answers + '; exit 0 ;;\nesac\n'
            'echo "stub gh: unexpected call $*" >&2; exit 1\n'), {"READS": str(reads), "VERI_POLL": "7"}


@pytest.mark.process("bash sources lib/github.sh")
def test_gh_pr_ready_with_a_head_sha_marks_ready_only_after_pulls_42_reports_it_polling_every_veri_poll(tmp_path):
    body, env = pr_head_stub(tmp_path, 'if [ "$n" -ge 3 ]; then echo %s; else echo %s; fi' % (NEW_SHA, OLD_SHA))

    code, out, err, calls = run_lib(tmp_path, body, "gh_pr_ready 42 " + NEW_SHA, None, env)

    ready_at = next(i for i, call in enumerate(calls) if "ccr/ready_for_review" in call)
    assert (code, out, err) == (0, "", "")
    assert len(reads_of_pr_42(calls)) == 3
    assert len(reads_of_pr_42(calls[:ready_at])) == 3
    assert "sleep 7" in calls


@pytest.mark.process("bash sources lib/github.sh")
def test_gh_pr_ready_with_a_head_sha_returns_2_unready_naming_both_shas_when_pulls_42_never_reports_it(tmp_path):
    body, env = pr_head_stub(
        tmp_path, 'if [ "$n" -gt 200 ]; then echo "stub gh: pulls/42 read more than 200 times" >&2; exit 1; fi; echo ' + OLD_SHA)

    code, out, err, calls = run_lib(tmp_path, body, "gh_pr_ready 42 " + NEW_SHA, None, env)

    assert (code, out) == (2, "")
    assert not [call for call in calls if "ccr/ready_for_review" in call or call.startswith("gh pr ready")]
    assert len(reads_of_pr_42(calls)) <= 200
    assert [line for line in err.splitlines() if OLD_SHA in line and NEW_SHA in line]


@pytest.mark.process("bash sources lib/github.sh")
def test_gh_pr_ready_with_no_head_sha_marks_ready_at_once_reading_no_pulls_42_and_never_sleeping(tmp_path):
    body, env = pr_head_stub(tmp_path, "echo " + OLD_SHA)

    code, out, err, calls = run_lib(tmp_path, body, "gh_pr_ready 42", None, env)

    assert (code, out, err) == (0, "", "")
    assert [call for call in calls if "ccr/ready_for_review" in call]
    assert reads_of_pr_42(calls) == []
    assert not started(calls, "sleep")


NODE_ID = "PR_kwDOnode42"
CCR_404 = "echo 'gh: Not Found (HTTP 404)' >&2; exit 1"
CCR_404_WITH_BODY = ("printf '{\\n  \"message\": \"Not Found\",\\n  \"documentation_url\": \"https://docs.github.com/rest\","
                     "\\n  \"status\": \"404\"\\n}\\n'; " + CCR_404)
GRAPHQL_READIES = ("echo '{\"data\":{\"markPullRequestReadyForReview\":{\"pullRequest\":{\"isDraft\":false}}}}'")
GRAPHQL_502 = "echo 'gh: Bad Gateway (HTTP 502)' >&2; exit 1"


def ready_route_stub(ccr, graphql):
    """A gh whose ccr ready route runs <ccr>, whose markPullRequestReadyForReview runs <graphql>,
    and which answers the node id lookup."""
    return ('[ "$1" = api ] || exit 1\ncase "$*" in\n'
            "  *ccr/ready_for_review*) " + ccr + " ;;\n"
            "  *markPullRequestReadyForReview*) " + graphql + " ;;\n"
            "  *' -q '* | *' --jq '* | *--jq=*) echo " + NODE_ID + " ;;\n"
            "  *pulls/42*) echo '{\"number\":42,\"node_id\":\"" + NODE_ID + "\",\"draft\":true}' ;;\n"
            "  *) exit 1 ;;\nesac\n")


def graphql_ready_calls(calls):
    return [call for call in "\n".join(calls).split("gh ") if call.startswith("api graphql")]


def mark_ready_calls(calls):
    return [call for call in graphql_ready_calls(calls) if "markPullRequestReadyForReview" in call]


@pytest.mark.process("bash sources lib/github.sh")
def test_with_the_driver_unset_a_404_on_the_ccr_route_sends_mark_ready_with_the_node_id_over_gh_api_graphql(tmp_path):
    code, out, err, calls = run_lib(tmp_path, ready_route_stub(CCR_404, GRAPHQL_READIES), "gh_pr_ready 42")

    sent = [call for call in mark_ready_calls(calls) if NODE_ID in call]
    assert (code, out) == (0, "")
    assert sent
    assert not started(calls, "gh pr")


@pytest.mark.process("bash sources lib/github.sh")
def test_with_the_driver_unset_a_404_on_the_ccr_route_and_a_502_on_mark_ready_tries_both_and_returns_2(tmp_path):
    code, out, err, calls = run_lib(tmp_path, ready_route_stub(CCR_404, GRAPHQL_502), "gh_pr_ready 42")

    assert (code, out) == (2, "")
    assert [call for call in calls if "ccr/ready_for_review" in call]
    assert mark_ready_calls(calls)


@pytest.mark.process("bash sources lib/github.sh")
def test_with_the_driver_unset_a_404_on_the_ccr_route_that_mark_ready_recovers_from_leaves_no_http_404_on_stderr(tmp_path):
    code, out, err, calls = run_lib(tmp_path, ready_route_stub(CCR_404, GRAPHQL_READIES), "gh_pr_ready 42")

    assert code == 0
    assert mark_ready_calls(calls)
    assert "HTTP 404" not in err


@pytest.mark.process("bash sources lib/github.sh")
def test_with_the_driver_unset_a_404_and_a_502_return_2_with_both_routes_failure_messages_on_stderr(tmp_path):
    code, out, err, calls = run_lib(tmp_path, ready_route_stub(CCR_404, GRAPHQL_502), "gh_pr_ready 42")

    assert code == 2
    assert "gh: Not Found (HTTP 404)" in err
    assert "gh: Bad Gateway (HTTP 502)" in err


@pytest.mark.process("bash sources lib/github.sh")
def test_with_the_driver_unset_a_ccr_route_that_readies_the_pr_is_the_only_route_and_gh_api_graphql_never_runs(tmp_path):
    ccr = "echo '{\"number\":42,\"draft\":false}'"

    code, out, err, calls = run_lib(tmp_path, ready_route_stub(ccr, GRAPHQL_READIES), "gh_pr_ready 42")

    assert code == 0
    assert "gh api -X POST repos/{owner}/{repo}/pulls/42/ccr/ready_for_review" in calls
    assert not started(calls, "gh api graphql")


@pytest.mark.process("bash sources lib/github.sh")
def test_with_the_driver_unset_the_404_body_of_the_ccr_route_stays_off_stdout_once_mark_ready_readies_the_pr(tmp_path):
    code, out, err, calls = run_lib(tmp_path, ready_route_stub(CCR_404_WITH_BODY, GRAPHQL_READIES), "gh_pr_ready 42")

    assert (code, out) == (0, "")


@pytest.mark.process("bash sources lib/github.sh")
def test_with_the_driver_unset_the_404_body_of_the_ccr_route_reaches_stderr_when_mark_ready_also_fails(tmp_path):
    graphql = "echo 'gh: Something went wrong (HTTP 502)' >&2; exit 1"

    code, out, err, calls = run_lib(tmp_path, ready_route_stub(CCR_404_WITH_BODY, graphql), "gh_pr_ready 42")

    assert code == 2
    assert '"documentation_url": "https://docs.github.com/rest",' in err


@pytest.mark.process("bash sources lib/github.sh")
def test_with_the_driver_unset_a_gh_pr_ready_refused_with_403_is_never_run_and_the_pr_is_readied_over_the_ccr_route(tmp_path):
    body = ('case "$1" in\n  pr) echo "%s (HTTP 403)" >&2; exit 1 ;;\n  api) echo \'{"number":42,"draft":false}\' ;;\n'
            '  *) exit 1 ;;\nesac\n' % REFUSAL)

    code, out, err, calls = run_lib(tmp_path, body, "gh_pr_ready 42")

    assert (code, err) == (0, "")
    assert "gh api -X POST repos/{owner}/{repo}/pulls/42/ccr/ready_for_review" in calls
    assert not started(calls, "gh pr")


NO_WAIT = {"VERI_TOOL_RETRY_SLEEP": "1", "VERI_TOOL_FAST_WAIT": "0", "VERI_TOOL_SLOW_SLEEP": "1", "VERI_TOOL_WAIT": "0"}


def clocked_sleep(factor):
    return f'sleep() {{ echo "$1" >> "$SLEEPS"; SECONDS=$((SECONDS + $1 * {factor})); }}; '


def run_without_gh(tmp_path, call, env, tools=("bash",), sleep_after=None):
    """(returncode, stdout, named, taken) of <call> run in bash after sourcing lib/github.sh, with a
    PATH whose one directory holds only <tools> and, when <sleep_after> is given, a sleep that
    records its argument and then runs <sleep_after>; no directory on it holds gh. <named> are the
    stderr lines naming gh other than bash's "command not found", <taken> the sleeps recorded.
    $BODY names a file holding an issue body, $BIN the directory."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for tool in tools:
        (bin_dir / tool).symlink_to(shutil.which(tool))
    sleeps = tmp_path / "sleeps"
    if sleep_after is not None:
        sleep = bin_dir / "sleep"
        sleep.write_text('#!/bin/sh\necho "$*" >> "$SLEEPS"\n' + sleep_after)
        sleep.chmod(0o755)
    body = tmp_path / "body"
    body.write_text("new body")
    env = {**env, "PATH": str(bin_dir), "LIB": str(LIB), "BODY": str(body), "BIN": str(bin_dir), "SLEEPS": str(sleeps)}

    ran = subprocess.run(["bash", "-c", 'source "$LIB"; ' + call], capture_output=True, text=True, env=env)

    named = [line for line in ran.stderr.splitlines() if "gh" in line and "command not found" not in line]
    taken = sleeps.read_text().split() if sleeps.exists() else []
    return ran.returncode, ran.stdout, named, taken


@pytest.mark.process("bash sources lib/github.sh")
def test_the_gh_function_itself_returns_exactly_2_naming_gh_when_no_directory_on_path_holds_gh_and_the_wait_is_0_issue_2097(tmp_path):
    code, _, named, _ = run_without_gh(tmp_path, "gh api x", NO_WAIT)

    assert (code, bool(named)) == (2, True), named


@pytest.mark.process("bash sources lib/github.sh")
def test_gh_issue_edit_returns_2_naming_the_missing_gh_when_no_directory_on_path_holds_gh_and_the_wait_is_0_issue_2097(tmp_path):
    code, _, named, _ = run_without_gh(tmp_path, 'gh_issue_edit 7 "$BODY"', NO_WAIT)

    assert (code, bool(named)) == (2, True), named


@pytest.mark.process("bash sources lib/github.sh")
def test_gh_issue_edit_sleeps_the_retry_then_the_slow_interval_naming_gh_each_wait_and_returns_2_once_the_wait_is_spent_issue_2097(tmp_path):
    env = {"VERI_TOOL_RETRY_SLEEP": "2", "VERI_TOOL_FAST_WAIT": "5", "VERI_TOOL_SLOW_SLEEP": "4", "VERI_TOOL_WAIT": "13"}

    code, _, named, taken = run_without_gh(tmp_path, clocked_sleep(1) + 'gh_issue_edit 7 "$BODY"', env)

    assert (code, taken, len(named)) == (2, ["2", "2", "2", "4", "4"], 6), named


@pytest.mark.process("bash sources lib/github.sh")
def test_gh_issue_edit_waits_out_a_gh_missing_from_path_sleeping_the_retry_naming_gh_and_answers_once_gh_is_back_issue_2097(tmp_path):
    installs_gh = 'printf \'#!/bin/sh\\necho "gh $*" >> "$CALLS"\\n\' > "$BIN/gh"\nchmod +x "$BIN/gh"\n'
    env = {"VERI_TOOL_RETRY_SLEEP": "7", "CALLS": str(tmp_path / "calls")}

    code, out, named, taken = run_without_gh(tmp_path, "gh_issue_edit 7 /dev/null", env, tools=("bash", "chmod"), sleep_after=installs_gh)

    answered = (tmp_path / "calls").read_text().split() if (tmp_path / "calls").exists() else []
    assert (code, out, taken, len(named), answered[:2]) == (0, "", ["7"], 1, ["gh", "api"]), named


@pytest.mark.process("bash sources lib/github.sh")
def test_gh_that_runs_and_fails_with_a_code_other_than_127_is_run_once_never_waited_on_and_returns_its_code_issue_2097(tmp_path):
    for code in (1, 2, 5, 126):
        code_out, stdout, stderr, calls = run_lib(tmp_path, f"exit {code}\n", "gh api x; echo \"rc=$?\"", env=NO_WAIT)
        assert (code_out, stdout, stderr, calls) == (0, f"rc={code}\n", "", ["gh api x"]), (code, stderr)


@pytest.mark.process("bash sources lib/github.sh")
def test_the_gh_function_gives_up_once_the_clock_shows_the_wait_spent_even_when_each_sleep_ran_ten_times_longer_than_asked_issue_2097(tmp_path):
    env = {"VERI_TOOL_RETRY_SLEEP": "2", "VERI_TOOL_FAST_WAIT": "100", "VERI_TOOL_SLOW_SLEEP": "2", "VERI_TOOL_WAIT": "20"}

    code, _, named, taken = run_without_gh(tmp_path, clocked_sleep(10) + "gh api x", env)

    assert (code, taken, len(named)) == (2, ["2"], 2), (taken, named)
