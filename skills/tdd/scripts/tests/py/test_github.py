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
