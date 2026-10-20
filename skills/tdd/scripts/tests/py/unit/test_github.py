"""In-process cases for veri/github.py, lib/github.sh's GraphQL→REST fallback in Python."""
import importlib
import os
import pathlib
import subprocess
import sys

import pytest

from conftest import SCRIPTS


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
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    path = "repos/{owner}/{repo}/pulls?state=open"
    calls = fake_gh(monkeypatch, {
        ("gh", "pr", "list", "--json", "number"): (0, '[{"number":7},{"number":9}]', ""),
    })

    answer = github.gh_list(path, "pr", "list", "--json", "number")

    assert answer == '[{"number":7},{"number":9}]'
    assert calls == [["gh", "pr", "list", "--json", "number"]]


def test_gh_list_answers_the_rest_pages_and_drops_the_graphql_stderr_when_the_gh_call_fails(monkeypatch, capsys, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
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


def test_gh_list_is_a_no_answer_with_the_rest_stderr_passed_through_when_both_routes_fail(monkeypatch, capsys, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    path = "repos/{owner}/{repo}/pulls?state=open"
    graphql_refusal = "GraphQL: Resource not accessible by integration\n"
    rest_refusal = "gh: HTTP 502: Bad Gateway (https://api.github.com/repos/o/r/pulls?state=open&page=1)\n"
    answers = {
        ("gh", "pr", "list", "--json", "number"): (1, "", graphql_refusal),
        ("gh", "api", path + "&page=1"): (1, "", rest_refusal),
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
        github.gh_list(path, "pr", "list", "--json", "number")

    assert calls == [
        ["gh", "pr", "list", "--json", "number"],
        ["gh", "api", path + "&page=1"],
    ]
    assert capsys.readouterr().err == rest_refusal


def test_gh_issue_view_answers_the_gh_issue_view_body_and_makes_no_gh_api_call_when_it_succeeds(monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    calls = fake_gh(monkeypatch, {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (0, "## What to build\n\nA thing.\n", ""),
    })

    answer = github.gh_issue_view("60", "body")

    assert answer == "## What to build\n\nA thing.\n"
    assert calls == [["gh", "issue", "view", "60", "--json", "body", "-q", ".body"]]


def test_gh_issue_view_answers_the_gh_issue_view_label_names_and_makes_no_gh_api_call_when_it_succeeds(monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    calls = fake_gh(monkeypatch, {
        ("gh", "issue", "view", "60", "--json", "labels", "-q", ".labels[].name"): (0, "bug\nready-for-agent\n", ""),
    })

    answer = github.gh_issue_view("60", "labels")

    assert answer == "bug\nready-for-agent\n"
    assert calls == [["gh", "issue", "view", "60", "--json", "labels", "-q", ".labels[].name"]]


def test_gh_issue_view_answers_the_rest_body_and_drops_the_graphql_stderr_when_gh_issue_view_fails(monkeypatch, capsys, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    refusal = "GraphQL: Resource not accessible by integration\n"
    answers = {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (1, "", refusal),
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (
            0, '{"number":60,"body":"## What to build\\n\\nA thing.","labels":[]}\n', ""),
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

    answer = github.gh_issue_view("60", "body")

    assert answer == "## What to build\n\nA thing.\n"
    assert calls == [
        ["gh", "issue", "view", "60", "--json", "body", "-q", ".body"],
        ["gh", "api", "repos/{owner}/{repo}/issues/60"],
    ]
    assert capsys.readouterr().err == ""


def test_gh_issue_view_answers_an_empty_body_from_the_rest_route_when_the_issue_body_is_null(monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    calls = fake_gh(monkeypatch, {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (1, "", ""),
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (
            0, '{"number":60,"body":null,"labels":[]}\n', ""),
    })

    answer = github.gh_issue_view("60", "body")

    assert answer == "\n"
    assert calls == [
        ["gh", "issue", "view", "60", "--json", "body", "-q", ".body"],
        ["gh", "api", "repos/{owner}/{repo}/issues/60"],
    ]


def test_gh_issue_view_answers_the_label_names_one_per_line_from_the_rest_route_for_labels(monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    calls = fake_gh(monkeypatch, {
        ("gh", "issue", "view", "60", "--json", "labels", "-q", ".labels[].name"): (1, "", ""),
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (
            0, '{"number":60,"body":"A thing.","labels":[{"name":"bug"},{"name":"ready-for-agent"}]}\n', ""),
    })

    answer = github.gh_issue_view("60", "labels")

    assert answer == "bug\nready-for-agent\n"
    assert calls == [
        ["gh", "issue", "view", "60", "--json", "labels", "-q", ".labels[].name"],
        ["gh", "api", "repos/{owner}/{repo}/issues/60"],
    ]


def test_gh_issue_view_is_a_no_answer_with_the_rest_stderr_then_the_json_decode_line_when_both_routes_fail_with_an_empty_rest_stdout(monkeypatch, capsys, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    graphql_refusal = "GraphQL: Resource not accessible by integration\n"
    rest_refusal = "gh: HTTP 502: Bad Gateway (https://api.github.com/repos/o/r/issues/60)\n"
    decode_line = "json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n"
    answers = {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (1, "", graphql_refusal),
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (1, "", rest_refusal),
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
        github.gh_issue_view("60", "body")

    assert calls == [
        ["gh", "issue", "view", "60", "--json", "body", "-q", ".body"],
        ["gh", "api", "repos/{owner}/{repo}/issues/60"],
    ]
    assert capsys.readouterr().err == rest_refusal + decode_line


def test_gh_issue_view_is_a_no_answer_when_the_rest_answer_is_not_json(monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    calls = fake_gh(monkeypatch, {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (1, "", ""),
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (0, "<html>Bad Gateway</html>\n", ""),
    })

    with pytest.raises(github.NoAnswer):
        github.gh_issue_view("60", "body")

    assert calls == [
        ["gh", "issue", "view", "60", "--json", "body", "-q", ".body"],
        ["gh", "api", "repos/{owner}/{repo}/issues/60"],
    ]


def test_gh_issue_view_is_a_no_answer_with_the_json_decode_line_when_gh_api_exits_0_with_a_non_json_stdout(monkeypatch, capsys, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake_gh(monkeypatch, {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (1, "", ""),
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (0, "<html>Bad Gateway</html>\n", ""),
    })

    with pytest.raises(github.NoAnswer):
        github.gh_issue_view("60", "body")

    assert capsys.readouterr().err == "json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n"


def test_gh_issue_view_is_a_no_answer_with_no_json_decode_line_when_gh_api_exits_non_zero_with_a_json_stdout(monkeypatch, capsys, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake_gh(monkeypatch, {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (1, "", ""),
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (
            1, '{"message":"Not Found","documentation_url":"https://docs.github.com/rest","status":"404"}\n', ""),
    })

    with pytest.raises(github.NoAnswer):
        github.gh_issue_view("60", "body")

    assert capsys.readouterr().err == ""


def test_gh_issue_edit_patches_the_issue_body_from_the_file_and_answers_nothing_of_its_stdout(monkeypatch, capsys, github):
    patch = ("gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/60", "-F", "body=@/tmp/body.md")
    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        if tuple(args) != patch:
            raise AssertionError("unexpected command: %r" % (args,))
        stdout = '{"number":60,"body":"New body."}\n'
        if kwargs.get("stdout") is None:
            sys.stdout.write(stdout)
        return subprocess.CompletedProcess(
            args, 0, stdout if kwargs.get("stdout") == subprocess.PIPE else None, None)

    monkeypatch.setattr(subprocess, "run", fake_run)

    answer = github.gh_issue_edit("60", "/tmp/body.md")

    assert answer is None
    assert calls == [list(patch)]
    assert capsys.readouterr().out == ""


def test_gh_issue_edit_is_a_no_answer_with_gh_stderr_passed_through_when_the_patch_fails(monkeypatch, capsys, github):
    patch = ("gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/60", "-F", "body=@/tmp/body.md")
    refusal = "gh: HTTP 502: Bad Gateway (https://api.github.com/repos/o/r/issues/60)\n"
    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        if tuple(args) != patch:
            raise AssertionError("unexpected command: %r" % (args,))
        if kwargs.get("stderr") is None:
            sys.stderr.write(refusal)
        return subprocess.CompletedProcess(
            args, 1, "" if kwargs.get("stdout") == subprocess.PIPE else None,
            refusal if kwargs.get("stderr") == subprocess.PIPE else None)

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(github.NoAnswer):
        github.gh_issue_edit("60", "/tmp/body.md")

    assert calls == [list(patch)]
    assert capsys.readouterr().err == refusal


def test_gh_issue_create_runs_only_the_rest_create_call_and_answers_its_stdout(monkeypatch, github):
    create = ("gh", "api", "repos/{owner}/{repo}/issues", "-f", "title=T", "-f", "body=B", "-q", ".html_url")
    calls = fake_gh(monkeypatch, {
        create: (0, "https://github.com/o/r/issues/61\n", ""),
    })

    answer = github.gh_issue_create("T", "B")

    assert answer == "https://github.com/o/r/issues/61\n"
    assert calls == [list(create)]


def test_gh_issue_create_is_a_no_answer_with_gh_stderr_passed_through_when_the_create_fails(monkeypatch, capsys, github):
    create = ("gh", "api", "repos/{owner}/{repo}/issues", "-f", "title=T", "-f", "body=B", "-q", ".html_url")
    refusal = "gh: HTTP 422: Validation Failed (https://api.github.com/repos/o/r/issues)\n"
    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        if tuple(args) != create:
            raise AssertionError("unexpected command: %r" % (args,))
        if kwargs.get("stderr") is None:
            sys.stderr.write(refusal)
        return subprocess.CompletedProcess(
            args, 1, "" if kwargs.get("stdout") == subprocess.PIPE else None,
            refusal if kwargs.get("stderr") == subprocess.PIPE else None)

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(github.NoAnswer):
        github.gh_issue_create("T", "B")

    assert calls == [list(create)]
    assert capsys.readouterr().err == refusal


def test_gh_json_answers_the_fixture_file_contents_and_makes_no_subprocess_call_when_veri_gh_json_is_set(monkeypatch, tmp_path, github):
    fixture = '[{"number":7,"title":"A thing"}]\n'
    (tmp_path / "prs.json").write_text(fixture)
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    calls = fake_gh(monkeypatch, {})

    answer = github.gh_json("prs.json", "repos/{owner}/{repo}/pulls?state=open",
                            "pr", "list", "--json", "number,title")

    assert answer == fixture
    assert calls == []


def test_gh_json_answers_the_rest_pages_when_veri_gh_json_is_unset_and_no_gh_args_are_given(monkeypatch, github):
    path = "repos/{owner}/{repo}/issues"
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    calls = fake_gh(monkeypatch, {
        ("gh", "api", path + "?page=1"): (0, '[{"number":4}]\n', ""),
        ("gh", "api", path + "?page=2"): (0, "[]\n", ""),
    })

    answer = github.gh_json("issues.json", path)

    assert answer == '[{"number":4}]'
    assert calls == [
        ["gh", "api", path + "?page=1"],
        ["gh", "api", path + "?page=2"],
    ]


def test_gh_json_answers_the_gh_list_answer_when_veri_gh_json_is_unset_and_gh_args_are_given(monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    path = "repos/{owner}/{repo}/pulls?state=open"
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    calls = fake_gh(monkeypatch, {
        ("gh", "pr", "list", "--json", "number"): (0, '[{"number":7},{"number":9}]', ""),
    })

    answer = github.gh_json("prs.json", path, "pr", "list", "--json", "number")

    assert answer == '[{"number":7},{"number":9}]'
    assert calls == [["gh", "pr", "list", "--json", "number"]]


def test_with_veri_gh_driver_unset_the_graphql_route_reads_run_only_their_rest_call_and_a_rest_failure_is_a_no_answer(monkeypatch, github):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    path = "repos/{owner}/{repo}/pulls?state=open"
    calls = fake_gh(monkeypatch, {
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (
            0, '{"number":60,"body":"A thing.","labels":[]}\n', ""),
        ("gh", "api", path + "&page=1"): (0, '[{"number":7}]\n', ""),
        ("gh", "api", path + "&page=2"): (0, "[]\n", ""),
        ("gh", "api", "repos/{owner}/{repo}/issues/61"): (1, "", ""),
    })

    assert github.gh_issue_view("60", "body") == "A thing.\n"
    assert github.gh_list(path, "pr", "list", "--json", "number") == '[{"number":7}]'
    assert github.gh_json("prs.json", path, "pr", "list", "--json", "number") == '[{"number":7}]'
    with pytest.raises(github.NoAnswer):
        github.gh_issue_view("61", "body")

    assert calls == [
        ["gh", "api", "repos/{owner}/{repo}/issues/60"],
        ["gh", "api", path + "&page=1"],
        ["gh", "api", path + "&page=2"],
        ["gh", "api", path + "&page=1"],
        ["gh", "api", path + "&page=2"],
        ["gh", "api", "repos/{owner}/{repo}/issues/61"],
    ]


def test_with_veri_gh_driver_rest_the_graphql_route_reads_run_only_rest_and_a_rest_failure_is_a_no_answer_with_gh_api_stderr(monkeypatch, capsys, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "rest")
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    path = "repos/{owner}/{repo}/pulls?state=open"
    broken = "repos/{owner}/{repo}/issues?state=open"
    refusal = "gh: HTTP 502: Bad Gateway\n"
    answers = {
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (
            0, '{"number":60,"body":"A thing.","labels":[]}\n', ""),
        ("gh", "api", path + "&page=1"): (0, '[{"number":7}]\n', ""),
        ("gh", "api", path + "&page=2"): (0, "[]\n", ""),
        ("gh", "api", "repos/{owner}/{repo}/issues/61"): (1, "", refusal),
        ("gh", "api", broken + "&page=1"): (1, "", refusal),
    }
    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        if tuple(args) not in answers:
            raise AssertionError("unexpected command: %r" % (args,))
        returncode, stdout, stderr = answers[tuple(args)]
        if kwargs.get("stderr") is None:
            sys.stderr.write(stderr)
        return subprocess.CompletedProcess(args, returncode, stdout, None)

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert github.gh_issue_view("60", "body") == "A thing.\n"
    assert github.gh_list(path, "pr", "list", "--json", "number") == '[{"number":7}]'
    assert github.gh_json("prs.json", path, "pr", "list", "--json", "number") == '[{"number":7}]'
    capsys.readouterr()
    errs = []
    for read in (lambda: github.gh_issue_view("61", "body"),
                 lambda: github.gh_list(broken, "issue", "list", "--json", "number"),
                 lambda: github.gh_json("issues.json", broken, "issue", "list", "--json", "number")):
        with pytest.raises(github.NoAnswer):
            read()
        errs.append(capsys.readouterr().err)

    assert [call for call in calls if call[1] != "api"] == []
    assert [err.startswith(refusal) for err in errs] == [True, True, True]


def test_with_veri_gh_driver_graphql_the_graphql_route_reads_answer_graphql_stdout_and_a_graphql_failure_is_a_no_answer_with_no_gh_api_call(monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    path = "repos/{owner}/{repo}/pulls?state=open"
    calls = fake_gh(monkeypatch, {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (0, "A thing.\n", ""),
        ("gh", "pr", "list", "--json", "number"): (0, '[{"number":7}]', ""),
        ("gh", "issue", "view", "61", "--json", "body", "-q", ".body"): (1, "", ""),
        ("gh", "issue", "list", "--json", "number"): (1, "", ""),
    })

    assert github.gh_issue_view("60", "body") == "A thing.\n"
    assert github.gh_list(path, "pr", "list", "--json", "number") == '[{"number":7}]'
    assert github.gh_json("prs.json", path, "pr", "list", "--json", "number") == '[{"number":7}]'
    for read in (lambda: github.gh_issue_view("61", "body"),
                 lambda: github.gh_list(path, "issue", "list", "--json", "number"),
                 lambda: github.gh_json("issues.json", path, "issue", "list", "--json", "number")):
        with pytest.raises(github.NoAnswer):
            read()

    assert [call for call in calls if call[1] == "api"] == []


def test_the_rest_only_operations_run_their_rest_call_and_no_graphql_call_under_each_veri_gh_driver(monkeypatch, github):
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    path = "repos/{owner}/{repo}/issues"
    patch = ("gh", "api", "-X", "PATCH", path + "/60", "-F", "body=@/tmp/body.md")
    create = ("gh", "api", path, "-f", "title=T", "-f", "body=B", "-q", ".html_url")
    calls = fake_gh(monkeypatch, {
        patch: (0, "", ""),
        create: (0, "https://github.com/o/r/issues/61\n", ""),
        ("gh", "api", path + "?page=1"): (0, '[{"number":4}]\n', ""),
        ("gh", "api", path + "?page=2"): (0, "[]\n", ""),
    })
    operations = (lambda: github.gh_issue_edit("60", "/tmp/body.md"),
                  lambda: github.gh_issue_create("T", "B"),
                  lambda: github.gh_rest_list(path),
                  lambda: github.gh_json("issues.json", path))
    observed = {}
    for driver in (None, "auto", "rest", "graphql"):
        if driver is None:
            monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
        else:
            monkeypatch.setenv("VERI_GH_DRIVER", driver)
        del calls[:]
        answers = []
        for operation in operations:
            try:
                answers.append(operation())
            except Exception as error:
                answers.append(type(error).__name__)
        observed[driver] = (answers, list(calls))

    pages = [["gh", "api", path + "?page=1"], ["gh", "api", path + "?page=2"]]
    expected = ([None, "https://github.com/o/r/issues/61\n", '[{"number":4}]', '[{"number":4}]'],
                [list(patch), list(create)] + pages + pages)
    assert observed == {driver: expected for driver in (None, "auto", "rest", "graphql")}


def test_with_veri_gh_json_set_gh_json_answers_the_fixture_file_contents_and_starts_no_process_under_each_veri_gh_driver(monkeypatch, tmp_path, github):
    fixture = '[{"number":7,"title":"A thing"}]\n'
    (tmp_path / "prs.json").write_text(fixture)
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    calls = fake_gh(monkeypatch, {})
    path = "repos/{owner}/{repo}/pulls?state=open"
    observed = {}
    for driver in (None, "auto", "rest", "graphql"):
        if driver is None:
            monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
        else:
            monkeypatch.setenv("VERI_GH_DRIVER", driver)
        del calls[:]
        answers = []
        for args in ((), ("pr", "list", "--json", "number,title")):
            try:
                answers.append(github.gh_json("prs.json", path, *args))
            except Exception as error:
                answers.append(type(error).__name__)
        observed[driver] = (answers, list(calls))

    assert observed == {driver: ([fixture, fixture], []) for driver in (None, "auto", "rest", "graphql")}


def test_the_module_is_importable_as_from_veri_import_github_and_as_import_veri_github(monkeypatch):
    monkeypatch.delitem(sys.modules, "veri.github", raising=False)
    monkeypatch.delattr(importlib.import_module("veri"), "github", raising=False)

    from veri import github as from_import
    import veri.github as dotted_import

    assert from_import is dotted_import
    assert pathlib.Path(from_import.__file__) == SCRIPTS / "veri" / "github.py"
    assert callable(from_import.gh_json)


def test_importing_the_module_starts_no_process_and_reads_veri_gh_json_only_when_called(monkeypatch, tmp_path):
    calls = fake_gh(monkeypatch, {})
    monkeypatch.setattr("os.system", lambda command: calls.append(command))
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    monkeypatch.delitem(sys.modules, "veri.github", raising=False)
    monkeypatch.delattr(importlib.import_module("veri"), "github", raising=False)

    import veri.github as github

    assert calls == []
    (tmp_path / "issues.json").write_text('[{"number":5}]')
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    assert github.gh_json("issues.json", "repos/{owner}/{repo}/issues") == '[{"number":5}]'
    assert calls == []


def test_with_veri_gh_driver_empty_or_unknown_every_public_function_starts_no_gh_process_and_is_a_no_answer_naming_the_variable_and_value(monkeypatch, capsys):
    calls = fake_gh(monkeypatch, {})
    reads = []

    class RecordingEnviron(dict):
        def get(self, key, default=None):
            reads.append(key)
            return dict.get(self, key, default)

        def __getitem__(self, key):
            reads.append(key)
            return dict.__getitem__(self, key)

    environ = RecordingEnviron(os.environ)
    environ.pop("VERI_GH_JSON", None)
    environ["VERI_GH_DRIVER"] = "gql"
    monkeypatch.setattr(os, "environ", environ)
    monkeypatch.delitem(sys.modules, "veri.github", raising=False)
    monkeypatch.delattr(importlib.import_module("veri"), "github", raising=False)

    import veri.github as github

    assert (reads, calls, capsys.readouterr().err) == ([], [], "")

    path = "repos/{owner}/{repo}/issues"
    operations = (lambda: github.gh_rest_list(path),
                  lambda: github.gh_list(path, "issue", "list", "--json", "number"),
                  lambda: github.gh_json("issues.json", path, "issue", "list", "--json", "number"),
                  lambda: github.gh_json("issues.json", path),
                  lambda: github.gh_issue_view("60", "body"),
                  lambda: github.gh_issue_edit("60", "/tmp/body.md"),
                  lambda: github.gh_issue_create("T", "B"))
    observed = {}
    for driver in ("", "REST", "gql"):
        environ["VERI_GH_DRIVER"] = driver
        outcomes = []
        for operation in operations:
            del calls[:]
            try:
                operation()
                outcome = "answered"
            except Exception as error:
                outcome = type(error).__name__
            err = capsys.readouterr().err
            outcomes.append((outcome, list(calls), err.count("\n"),
                             "VERI_GH_DRIVER" in err, "'%s'" % driver in err))
        observed[driver] = outcomes

    refused = [("NoAnswer", [], 1, True, True)] * len(operations)
    assert observed == {driver: refused for driver in ("", "REST", "gql")}
