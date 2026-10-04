"""In-process cases for veri/github.py, lib/github.sh's GraphQL→REST fallback in Python."""
import importlib
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def github():
    return importlib.import_module("veri.github")


def fake_gh(monkeypatch, answers):
    """subprocess.run answering each command in <answers> (argv tuple → (returncode, stdout,
    stderr)); every subprocess call, run or Popen, recorded in the returned list."""
    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        if tuple(args) not in answers:
            raise AssertionError("unexpected command: %r" % (args,))
        returncode, stdout, stderr = answers[tuple(args)]
        return subprocess.CompletedProcess(args, returncode, stdout, stderr)

    def fake_popen(args, *rest, **kwargs):
        calls.append(list(args))
        raise AssertionError("unexpected Popen: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    return calls


def test_gh_rest_list_answers_each_page_back_to_back_until_the_first_bare_empty_page(monkeypatch, github):
    path = "repos/{owner}/{repo}/pulls"
    calls = fake_gh(monkeypatch, {
        ("gh", "api", path + "?page=1"): (0, '[{"number":1},{"number":2}]', ""),
        ("gh", "api", path + "?page=2"): (0, '[{"number":3}]', ""),
        ("gh", "api", path + "?page=3"): (0, "[]", ""),
    })

    answer = github.gh_rest_list(path)

    assert answer == '[{"number":1},{"number":2}][{"number":3}]'
    assert calls == [
        ["gh", "api", path + "?page=1"],
        ["gh", "api", path + "?page=2"],
        ["gh", "api", path + "?page=3"],
    ]


def test_gh_rest_list_drops_the_trailing_newlines_gh_api_prints_after_each_page(monkeypatch, github):
    path = "repos/{owner}/{repo}/issues"
    fake_gh(monkeypatch, {
        ("gh", "api", path + "?page=1"): (0, '[{"number":1}]\n', ""),
        ("gh", "api", path + "?page=2"): (0, '[{"number":2}]\n\n', ""),
        ("gh", "api", path + "?page=3"): (0, "[]\n", ""),
    })

    assert github.gh_rest_list(path) == '[{"number":1}][{"number":2}]'


def test_gh_rest_list_joins_page_with_an_ampersand_when_the_path_already_holds_a_query(monkeypatch, github):
    path = "repos/{owner}/{repo}/commits/abc123/check-runs?per_page=100"
    calls = fake_gh(monkeypatch, {
        ("gh", "api", path + "&page=1"): (0, '[{"id":1}]', ""),
        ("gh", "api", path + "&page=2"): (0, "[]", ""),
    })

    answer = github.gh_rest_list(path)

    assert answer == '[{"id":1}]'
    assert calls == [
        ["gh", "api", path + "&page=1"],
        ["gh", "api", path + "&page=2"],
    ]


def test_gh_rest_list_stops_at_the_first_page_matching_a_caller_given_empty_pattern(monkeypatch, github):
    path = "repos/{owner}/{repo}/commits/abc123/check-runs"
    calls = fake_gh(monkeypatch, {
        ("gh", "api", path + "?page=1"): (0, '{"total_count":1,"check_runs":[{"id":1}]}', ""),
        ("gh", "api", path + "?page=2"): (0, '{"total_count":1,"check_runs": [ ]}', ""),
    })

    answer = github.gh_rest_list(path, r'"check_runs": *\[ *\]')

    assert answer == '{"total_count":1,"check_runs":[{"id":1}]}'
    assert calls == [
        ["gh", "api", path + "?page=1"],
        ["gh", "api", path + "?page=2"],
    ]


def test_gh_rest_list_is_a_no_answer_when_page_two_fails_with_gh_stderr_passed_through(monkeypatch, capsys, github):
    path = "repos/{owner}/{repo}/pulls"
    refusal = "gh: HTTP 502: Bad Gateway (https://api.github.com/repos/o/r/pulls?page=2)\n"
    answers = {
        ("gh", "api", path + "?page=1"): (0, '[{"number":1}]', ""),
        ("gh", "api", path + "?page=2"): (1, "", refusal),
    }
    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        if tuple(args) not in answers:
            raise AssertionError("unexpected command: %r" % (args,))
        returncode, stdout, stderr = answers[tuple(args)]
        if kwargs.get("stderr") is None:
            sys.stderr.write(stderr)
        return subprocess.CompletedProcess(
            args, returncode, stdout, stderr if kwargs.get("stderr") == subprocess.PIPE else None)

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(github.NoAnswer):
        github.gh_rest_list(path)

    assert calls == [
        ["gh", "api", path + "?page=1"],
        ["gh", "api", path + "?page=2"],
    ]
    assert capsys.readouterr().err == refusal


def test_gh_rest_list_hands_the_pages_fetched_before_a_failing_page_along_with_the_no_answer(monkeypatch, github):
    path = "repos/{owner}/{repo}/issues?per_page=2"
    fake_gh(monkeypatch, {
        ("gh", "api", path + "&page=1"): (0, '[{"number":1},{"number":2}]\n', ""),
        ("gh", "api", path + "&page=2"): (0, '[{"number":3},{"number":4}]\n', ""),
        ("gh", "api", path + "&page=3"): (1, "", "gh: Bad Gateway (HTTP 502)\n"),
    })

    with pytest.raises(github.NoAnswer) as no_answer:
        github.gh_rest_list(path)

    assert no_answer.value.answer == '[{"number":1},{"number":2}][{"number":3},{"number":4}]'


def test_gh_list_answers_the_gh_call_stdout_and_makes_no_gh_api_call_when_it_succeeds(monkeypatch, github):
    path = "repos/{owner}/{repo}/pulls?state=open"
    calls = fake_gh(monkeypatch, {
        ("gh", "pr", "list", "--json", "number"): (0, '[{"number":7},{"number":9}]', ""),
    })

    answer = github.gh_list(path, "pr", "list", "--json", "number")

    assert answer == '[{"number":7},{"number":9}]'
    assert calls == [["gh", "pr", "list", "--json", "number"]]


def test_gh_list_answers_the_rest_pages_and_drops_the_graphql_stderr_when_the_gh_call_fails(monkeypatch, capsys, github):
    path = "repos/{owner}/{repo}/pulls?state=open"
    refusal = "GraphQL: Resource not accessible by integration\n"
    answers = {
        ("gh", "pr", "list", "--json", "number"): (1, "", refusal),
        ("gh", "api", path + "&page=1"): (0, '[{"number":7}]\n', ""),
        ("gh", "api", path + "&page=2"): (0, '[{"number":9}]\n', ""),
        ("gh", "api", path + "&page=3"): (0, "[]\n", ""),
    }
    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        if tuple(args) not in answers:
            raise AssertionError("unexpected command: %r" % (args,))
        returncode, stdout, stderr = answers[tuple(args)]
        if kwargs.get("stderr") is None:
            sys.stderr.write(stderr)
        return subprocess.CompletedProcess(
            args, returncode, stdout, stderr if kwargs.get("stderr") == subprocess.PIPE else None)

    monkeypatch.setattr(subprocess, "run", fake_run)

    answer = github.gh_list(path, "pr", "list", "--json", "number")

    assert answer == '[{"number":7}][{"number":9}]'
    assert calls == [
        ["gh", "pr", "list", "--json", "number"],
        ["gh", "api", path + "&page=1"],
        ["gh", "api", path + "&page=2"],
        ["gh", "api", path + "&page=3"],
    ]
    assert capsys.readouterr().err == ""
