"""In-process cases for veri/github.py, veri's GitHub access through gh and its GraphQL→REST fallback."""
import importlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time

import pytest

from conftest import SCRIPTS
from process_fakes import HANGS


@pytest.fixture
def github():
    return importlib.import_module("veri.github")


def fake_gh(fake_processes, answers):
    """fake_processes answering each command in <answers> (argv tuple → (returncode, stdout,
    stderr)) and no other; every subprocess call, run or Popen, recorded in the returned fake's argvs."""
    return fake_processes.answers({" ".join(argv): answer for argv, answer in answers.items()}, exact=True)


def inheriting(answers):
    """An answer callable for fake_processes.answers(default=...) behaving like gh for the streams: <answers>
    maps an argv tuple to (returncode, stdout, stderr); a stream the call did not ask for as PIPE is written
    to this process's own stream and answered None, and a command not in <answers> fails the case."""
    table = {" ".join(argv): answer for argv, answer in answers.items()}

    def answer(line, **kwargs):
        if line not in table:
            raise AssertionError("unexpected command: %r" % (line,))
        returncode, stdout, stderr = table[line]
        for stream, text, name in ((sys.stdout, stdout, "stdout"), (sys.stderr, stderr, "stderr")):
            if kwargs.get(name) is None:
                stream.write(text)
        return (returncode, stdout if kwargs.get("stdout") == subprocess.PIPE else None,
                stderr if kwargs.get("stderr") == subprocess.PIPE else None)
    return answer


def fake_clock(monkeypatch):
    """time.monotonic, time.time and time.sleep on one fake clock starting at 1000.0, which
    each sleep advances; returns ([now], sleeps), the sleeps taken in order. A 200th sleep fails
    the case, so a wait that never ends is red, not hung."""
    now = [1000.0]
    sleeps = []

    def fake_sleep(seconds):
        assert len(sleeps) < 200, "still waiting after %d sleeps" % len(sleeps)
        sleeps.append(seconds)
        now[0] += seconds

    monkeypatch.setattr(time, "monotonic", lambda: now[0])
    monkeypatch.setattr(time, "time", lambda: now[0])
    monkeypatch.setattr(time, "sleep", fake_sleep)
    return now, sleeps


def fake_missing_gh(fake_processes, misses=None):
    """subprocess.run raising the FileNotFoundError of a gh missing from PATH for the first
    <misses> calls (every call when None), then answering '{"number":7}'; returns the fake."""
    def answer(line, **kwargs):
        if misses is None or len(fake.argvs) <= misses:
            raise FileNotFoundError(2, "No such file or directory", "gh")
        return (0, '{"number":7}', "")

    fake = fake_processes.answers({}, default=answer)
    return fake


def test_gh_missing_from_path_twice_is_waited_out_with_a_stderr_line_per_wait_then_answers_2097(fake_processes, monkeypatch, capsys, github):
    _, sleeps = fake_clock(monkeypatch)
    monkeypatch.delenv("VERI_TOOL_RETRY_SLEEP", raising=False)
    fake = fake_missing_gh(fake_processes, misses=2)

    run = github.gh_api("repos/{owner}/{repo}/issues/7")

    assert (run.returncode, run.stdout) == (0, '{"number":7}')
    assert sleeps == [15, 15]
    assert len(fake.argvs) == 3
    err_lines = capsys.readouterr().err.splitlines()
    assert len(err_lines) == 2
    assert all("gh" in line for line in err_lines)


def test_gh_missing_from_path_twice_sleeps_the_veri_tool_retry_sleep_value_before_each_retry_2097(fake_processes, monkeypatch, capsys, github):
    _, sleeps = fake_clock(monkeypatch)
    monkeypatch.setenv("VERI_TOOL_RETRY_SLEEP", "2")
    fake_missing_gh(fake_processes, misses=2)

    run = github.gh_api("repos/{owner}/{repo}/issues/7")

    assert (run.returncode, run.stdout) == (0, '{"number":7}')
    assert sleeps == [2, 2]


def test_gh_never_found_on_path_is_polled_every_15s_for_900s_then_every_900s_and_is_a_no_answer_naming_gh_at_3600s_2097(fake_processes, monkeypatch, capsys, github):
    _, sleeps = fake_clock(monkeypatch)
    for name in ("VERI_TOOL_RETRY_SLEEP", "VERI_TOOL_FAST_WAIT", "VERI_TOOL_SLOW_SLEEP", "VERI_TOOL_WAIT"):
        monkeypatch.delenv(name, raising=False)
    fake = fake_missing_gh(fake_processes)

    with pytest.raises(github.NoAnswer):
        github.gh_api("repos/{owner}/{repo}/issues/7")

    assert sleeps == [15] * 60 + [900] * 3
    assert len(fake.argvs) == 64
    err_lines = capsys.readouterr().err.splitlines()
    assert err_lines and all("gh" in line for line in err_lines)


def test_gh_never_found_on_path_follows_the_four_tool_wait_tunables_when_set_to_non_default_values_2097(fake_processes, monkeypatch, capsys, github):
    now, sleeps = fake_clock(monkeypatch)
    monkeypatch.setenv("VERI_TOOL_RETRY_SLEEP", "10")
    monkeypatch.setenv("VERI_TOOL_FAST_WAIT", "30")
    monkeypatch.setenv("VERI_TOOL_SLOW_SLEEP", "50")
    monkeypatch.setenv("VERI_TOOL_WAIT", "100")
    fake = fake_missing_gh(fake_processes)

    with pytest.raises(github.NoAnswer):
        github.gh_api("repos/{owner}/{repo}/issues/7")

    assert sleeps == [10, 10, 10, 50, 50]
    assert len(fake.argvs) == 6
    assert now[0] == 1130.0
    err_lines = capsys.readouterr().err.splitlines()
    assert err_lines and all("gh" in line for line in err_lines)


def test_gh_that_runs_and_fails_is_not_waited_on_and_its_exit_code_reaches_the_caller_unchanged_2097(fake_processes, monkeypatch, capsys, github):
    sleeps = []
    monkeypatch.setattr(time, "sleep", lambda seconds: sleeps.append(seconds))
    fake = fake_gh(fake_processes, {("gh", "api", "repos/{owner}/{repo}/issues/7"): (4, "", "")})

    run = github.gh_api("repos/{owner}/{repo}/issues/7")

    assert run.returncode == 4
    assert sleeps == []
    assert len(fake.argvs) == 1
    assert capsys.readouterr().err == ""


def test_gh_rest_list_answers_each_page_back_to_back_until_the_first_bare_empty_page(fake_processes, monkeypatch, github):
    path = "repos/{owner}/{repo}/pulls"
    fake = fake_gh(fake_processes, {
        ("gh", "api", path + "?page=1"): (0, '[{"number":1},{"number":2}]', ""),
        ("gh", "api", path + "?page=2"): (0, '[{"number":3}]', ""),
        ("gh", "api", path + "?page=3"): (0, "[]", ""),
    })

    answer = github.gh_rest_list(path)

    assert answer == '[{"number":1},{"number":2}][{"number":3}]'
    assert fake.argvs == [
        ["gh", "api", path + "?page=1"],
        ["gh", "api", path + "?page=2"],
        ["gh", "api", path + "?page=3"],
    ]


def test_gh_rest_list_drops_the_trailing_newlines_gh_api_prints_after_each_page(fake_processes, monkeypatch, github):
    path = "repos/{owner}/{repo}/issues"
    fake_gh(fake_processes, {
        ("gh", "api", path + "?page=1"): (0, '[{"number":1}]\n', ""),
        ("gh", "api", path + "?page=2"): (0, '[{"number":2}]\n\n', ""),
        ("gh", "api", path + "?page=3"): (0, "[]\n", ""),
    })

    assert github.gh_rest_list(path) == '[{"number":1}][{"number":2}]'


def test_gh_rest_list_joins_page_with_an_ampersand_when_the_path_already_holds_a_query(fake_processes, monkeypatch, github):
    path = "repos/{owner}/{repo}/commits/abc123/check-runs?per_page=100"
    fake = fake_gh(fake_processes, {
        ("gh", "api", path + "&page=1"): (0, '[{"id":1}]', ""),
        ("gh", "api", path + "&page=2"): (0, "[]", ""),
    })

    answer = github.gh_rest_list(path)

    assert answer == '[{"id":1}]'
    assert fake.argvs == [
        ["gh", "api", path + "&page=1"],
        ["gh", "api", path + "&page=2"],
    ]


def test_gh_rest_list_stops_at_the_first_page_matching_a_caller_given_empty_pattern(fake_processes, monkeypatch, github):
    path = "repos/{owner}/{repo}/commits/abc123/check-runs"
    fake = fake_gh(fake_processes, {
        ("gh", "api", path + "?page=1"): (0, '{"total_count":1,"check_runs":[{"id":1}]}', ""),
        ("gh", "api", path + "?page=2"): (0, '{"total_count":1,"check_runs": [ ]}', ""),
    })

    answer = github.gh_rest_list(path, r'"check_runs": *\[ *\]')

    assert answer == '{"total_count":1,"check_runs":[{"id":1}]}'
    assert fake.argvs == [
        ["gh", "api", path + "?page=1"],
        ["gh", "api", path + "?page=2"],
    ]


def test_gh_rest_list_is_a_no_answer_when_page_two_fails_with_gh_stderr_passed_through(fake_processes, monkeypatch, capsys, github):
    path = "repos/{owner}/{repo}/pulls"
    refusal = "gh: HTTP 502: Bad Gateway (https://api.github.com/repos/o/r/pulls?page=2)\n"
    answers = {
        ("gh", "api", path + "?page=1"): (0, '[{"number":1}]', ""),
        ("gh", "api", path + "?page=2"): (1, "", refusal),
    }
    fake = fake_processes.answers({}, default=inheriting(answers))

    with pytest.raises(github.NoAnswer):
        github.gh_rest_list(path)

    assert fake.argvs == [
        ["gh", "api", path + "?page=1"],
        ["gh", "api", path + "?page=2"],
    ]
    assert capsys.readouterr().err == refusal


def test_gh_rest_list_hands_the_pages_fetched_before_a_failing_page_along_with_the_no_answer(fake_processes, monkeypatch, github):
    path = "repos/{owner}/{repo}/issues?per_page=2"
    fake_gh(fake_processes, {
        ("gh", "api", path + "&page=1"): (0, '[{"number":1},{"number":2}]\n', ""),
        ("gh", "api", path + "&page=2"): (0, '[{"number":3},{"number":4}]\n', ""),
        ("gh", "api", path + "&page=3"): (1, "", "gh: Bad Gateway (HTTP 502)\n"),
    })

    with pytest.raises(github.NoAnswer) as no_answer:
        github.gh_rest_list(path)

    assert no_answer.value.answer == '[{"number":1},{"number":2}][{"number":3},{"number":4}]'


def test_gh_list_answers_the_gh_call_stdout_and_makes_no_gh_api_call_when_it_succeeds(fake_processes, monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    path = "repos/{owner}/{repo}/pulls?state=open"
    fake = fake_gh(fake_processes, {
        ("gh", "pr", "list", "--json", "number"): (0, '[{"number":7},{"number":9}]', ""),
    })

    answer = github.gh_list(path, "pr", "list", "--json", "number")

    assert answer == '[{"number":7},{"number":9}]'
    assert fake.argvs == [["gh", "pr", "list", "--json", "number"]]


def test_gh_list_answers_the_rest_pages_and_drops_the_graphql_stderr_when_the_gh_call_fails(fake_processes, monkeypatch, capsys, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    path = "repos/{owner}/{repo}/pulls?state=open"
    refusal = "GraphQL: Resource not accessible by integration\n"
    answers = {
        ("gh", "pr", "list", "--json", "number"): (1, "", refusal),
        ("gh", "api", path + "&page=1"): (0, '[{"number":7}]\n', ""),
        ("gh", "api", path + "&page=2"): (0, '[{"number":9}]\n', ""),
        ("gh", "api", path + "&page=3"): (0, "[]\n", ""),
    }
    fake = fake_processes.answers({}, default=inheriting(answers))

    answer = github.gh_list(path, "pr", "list", "--json", "number")

    assert answer == '[{"number":7}][{"number":9}]'
    assert fake.argvs == [
        ["gh", "pr", "list", "--json", "number"],
        ["gh", "api", path + "&page=1"],
        ["gh", "api", path + "&page=2"],
        ["gh", "api", path + "&page=3"],
    ]
    assert capsys.readouterr().err == ""


def test_gh_list_is_a_no_answer_with_the_rest_stderr_passed_through_when_both_routes_fail(fake_processes, monkeypatch, capsys, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    path = "repos/{owner}/{repo}/pulls?state=open"
    graphql_refusal = "GraphQL: Resource not accessible by integration\n"
    rest_refusal = "gh: HTTP 502: Bad Gateway (https://api.github.com/repos/o/r/pulls?state=open&page=1)\n"
    answers = {
        ("gh", "pr", "list", "--json", "number"): (1, "", graphql_refusal),
        ("gh", "api", path + "&page=1"): (1, "", rest_refusal),
    }
    fake = fake_processes.answers({}, default=inheriting(answers))

    with pytest.raises(github.NoAnswer):
        github.gh_list(path, "pr", "list", "--json", "number")

    assert fake.argvs == [
        ["gh", "pr", "list", "--json", "number"],
        ["gh", "api", path + "&page=1"],
    ]
    assert capsys.readouterr().err == rest_refusal


def test_gh_issue_view_answers_the_gh_issue_view_body_and_makes_no_gh_api_call_when_it_succeeds(fake_processes, monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake = fake_gh(fake_processes, {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (0, "## What to build\n\nA thing.\n", ""),
    })

    answer = github.gh_issue_view("60", "body")

    assert answer == "## What to build\n\nA thing.\n"
    assert fake.argvs == [["gh", "issue", "view", "60", "--json", "body", "-q", ".body"]]


def test_gh_issue_view_answers_the_gh_issue_view_label_names_and_makes_no_gh_api_call_when_it_succeeds(fake_processes, monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake = fake_gh(fake_processes, {
        ("gh", "issue", "view", "60", "--json", "labels", "-q", ".labels[].name"): (0, "bug\nready-for-agent\n", ""),
    })

    answer = github.gh_issue_view("60", "labels")

    assert answer == "bug\nready-for-agent\n"
    assert fake.argvs == [["gh", "issue", "view", "60", "--json", "labels", "-q", ".labels[].name"]]


def test_gh_issue_view_answers_the_rest_body_and_drops_the_graphql_stderr_when_gh_issue_view_fails(fake_processes, monkeypatch, capsys, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    refusal = "GraphQL: Resource not accessible by integration\n"
    answers = {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (1, "", refusal),
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (
            0, '{"number":60,"body":"## What to build\\n\\nA thing.","labels":[]}\n', ""),
    }
    fake = fake_processes.answers({}, default=inheriting(answers))

    answer = github.gh_issue_view("60", "body")

    assert answer == "## What to build\n\nA thing.\n"
    assert fake.argvs == [
        ["gh", "issue", "view", "60", "--json", "body", "-q", ".body"],
        ["gh", "api", "repos/{owner}/{repo}/issues/60"],
    ]
    assert capsys.readouterr().err == ""


def test_gh_issue_view_answers_an_empty_body_from_the_rest_route_when_the_issue_body_is_null(fake_processes, monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake = fake_gh(fake_processes, {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (1, "", ""),
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (
            0, '{"number":60,"body":null,"labels":[]}\n', ""),
    })

    answer = github.gh_issue_view("60", "body")

    assert answer == "\n"
    assert fake.argvs == [
        ["gh", "issue", "view", "60", "--json", "body", "-q", ".body"],
        ["gh", "api", "repos/{owner}/{repo}/issues/60"],
    ]


def test_gh_issue_view_answers_the_label_names_one_per_line_from_the_rest_route_for_labels(fake_processes, monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake = fake_gh(fake_processes, {
        ("gh", "issue", "view", "60", "--json", "labels", "-q", ".labels[].name"): (1, "", ""),
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (
            0, '{"number":60,"body":"A thing.","labels":[{"name":"bug"},{"name":"ready-for-agent"}]}\n', ""),
    })

    answer = github.gh_issue_view("60", "labels")

    assert answer == "bug\nready-for-agent\n"
    assert fake.argvs == [
        ["gh", "issue", "view", "60", "--json", "labels", "-q", ".labels[].name"],
        ["gh", "api", "repos/{owner}/{repo}/issues/60"],
    ]


def test_gh_issue_view_answers_the_comment_bodies_of_every_page_for_comments_issue_3687(fake_processes, monkeypatch, github):
    base = "repos/{owner}/{repo}/issues/3241/comments"
    fake = fake_gh(fake_processes, {
        ("gh", "api", base + "?page=1"): (0, '[{"body":"first comment"}]\n', ""),
        ("gh", "api", base + "?page=2"): (0, '[{"body":"### \u26d4 Preflight refused\\n\\nwhy"}]\n', ""),
        ("gh", "api", base + "?page=3"): (0, "[]\n", ""),
    })

    answer = github.gh_issue_view("3241", "comments")

    assert "### \u26d4 Preflight refused" in answer
    assert "first comment" in answer
    assert fake.argvs


def test_graphql_gh_issue_view_answers_the_comment_bodies_of_every_page_not_the_label_names_for_comments_issue_3687(fake_processes, monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    base = "repos/{owner}/{repo}/issues/3241/comments"
    fake_gh(fake_processes, {
        ("gh", "issue", "view", "3241", "--json", "comments", "-q", ".labels[].name"): (0, "taken:mu\n", ""),
        ("gh", "api", base + "?page=1"): (0, '[{"body":"first comment"}]\n', ""),
        ("gh", "api", base + "?page=2"): (0, '[{"body":"### \u26d4 Preflight refused\\n\\nwhy"}]\n', ""),
        ("gh", "api", base + "?page=3"): (0, "[]\n", ""),
    })

    answer = github.gh_issue_view("3241", "comments")

    assert "### \u26d4 Preflight refused" in answer
    assert "first comment" in answer


def test_rest_gh_issue_view_with_an_unknown_field_is_a_no_answer_not_the_issue_body_issue_3687(fake_processes, monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "rest")
    fake_gh(fake_processes, {
        ("gh", "api", "repos/{owner}/{repo}/issues/3241"): (
            0, '{"number":3241,"body":"## Problem","labels":[{"name":"taken:mu"}]}\n', ""),
    })

    with pytest.raises(github.NoAnswer):
        github.gh_issue_view("3241", "assignees")


def test_graphql_gh_issue_view_with_an_unknown_field_is_a_no_answer_not_the_label_names_issue_3687(fake_processes, monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    fake_gh(fake_processes, {
        ("gh", "issue", "view", "3241", "--json", "assignees", "-q", ".labels[].name"): (0, "taken:mu\n", ""),
    })

    with pytest.raises(github.NoAnswer):
        github.gh_issue_view("3241", "assignees")


def test_gh_issue_view_for_comments_is_a_no_answer_not_a_json_decode_error_when_a_comments_page_fails_issue_3687(fake_processes, monkeypatch, github):
    base = "repos/{owner}/{repo}/issues/3241/comments"
    fake_gh(fake_processes, {
        ("gh", "api", base + "?page=1"): (0, '[{"body":"first comment"}]\n', ""),
        ("gh", "api", base + "?page=2"): (1, "", "gh: HTTP 502: Bad Gateway\n"),
    })

    with pytest.raises(github.NoAnswer):
        github.gh_issue_view("3241", "comments")


def test_gh_issue_view_is_a_no_answer_with_the_rest_stderr_then_the_json_decode_line_when_both_routes_fail_with_an_empty_rest_stdout(fake_processes, monkeypatch, capsys, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    graphql_refusal = "GraphQL: Resource not accessible by integration\n"
    rest_refusal = "gh: HTTP 502: Bad Gateway (https://api.github.com/repos/o/r/issues/60)\n"
    decode_line = "json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n"
    answers = {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (1, "", graphql_refusal),
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (1, "", rest_refusal),
    }
    fake = fake_processes.answers({}, default=inheriting(answers))

    with pytest.raises(github.NoAnswer):
        github.gh_issue_view("60", "body")

    assert fake.argvs == [
        ["gh", "issue", "view", "60", "--json", "body", "-q", ".body"],
        ["gh", "api", "repos/{owner}/{repo}/issues/60"],
    ]
    assert capsys.readouterr().err == rest_refusal + decode_line


def test_gh_issue_view_is_a_no_answer_when_the_rest_answer_is_not_json(fake_processes, monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake = fake_gh(fake_processes, {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (1, "", ""),
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (0, "<html>Bad Gateway</html>\n", ""),
    })

    with pytest.raises(github.NoAnswer):
        github.gh_issue_view("60", "body")

    assert fake.argvs == [
        ["gh", "issue", "view", "60", "--json", "body", "-q", ".body"],
        ["gh", "api", "repos/{owner}/{repo}/issues/60"],
    ]


def test_gh_issue_view_is_a_no_answer_with_the_json_decode_line_when_gh_api_exits_0_with_a_non_json_stdout(fake_processes, monkeypatch, capsys, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake_gh(fake_processes, {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (1, "", ""),
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (0, "<html>Bad Gateway</html>\n", ""),
    })

    with pytest.raises(github.NoAnswer):
        github.gh_issue_view("60", "body")

    assert capsys.readouterr().err == "json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n"


def test_gh_issue_view_is_a_no_answer_with_no_json_decode_line_when_gh_api_exits_non_zero_with_a_json_stdout(fake_processes, monkeypatch, capsys, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake_gh(fake_processes, {
        ("gh", "issue", "view", "60", "--json", "body", "-q", ".body"): (1, "", ""),
        ("gh", "api", "repos/{owner}/{repo}/issues/60"): (
            1, '{"message":"Not Found","documentation_url":"https://docs.github.com/rest","status":"404"}\n', ""),
    })

    with pytest.raises(github.NoAnswer):
        github.gh_issue_view("60", "body")

    assert capsys.readouterr().err == ""


def test_gh_issue_edit_patches_the_issue_body_from_the_file_and_answers_nothing_of_its_stdout(fake_processes, monkeypatch, capsys, github):
    patch = ("gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/60", "-F", "body=@/tmp/body.md")
    fake = fake_processes.answers({}, default=inheriting({patch: (0, '{"number":60,"body":"New body."}\n', "")}))

    answer = github.gh_issue_edit("60", "/tmp/body.md")

    assert answer is None
    assert fake.argvs == [list(patch)]
    assert capsys.readouterr().out == ""


def test_gh_issue_edit_is_a_no_answer_with_gh_stderr_passed_through_when_the_patch_fails(fake_processes, monkeypatch, capsys, github):
    patch = ("gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/60", "-F", "body=@/tmp/body.md")
    refusal = "gh: HTTP 502: Bad Gateway (https://api.github.com/repos/o/r/issues/60)\n"
    fake = fake_processes.answers({}, default=inheriting({patch: (1, "", refusal)}))

    with pytest.raises(github.NoAnswer):
        github.gh_issue_edit("60", "/tmp/body.md")

    assert fake.argvs == [list(patch)]
    assert capsys.readouterr().err == refusal


def test_gh_issue_create_runs_only_the_rest_create_call_and_answers_its_stdout(fake_processes, monkeypatch, github):
    create = ("gh", "api", "repos/{owner}/{repo}/issues", "-f", "title=T", "-f", "body=B", "-q", ".html_url")
    fake = fake_gh(fake_processes, {
        create: (0, "https://github.com/o/r/issues/61\n", ""),
    })

    answer = github.gh_issue_create("T", "B")

    assert answer == "https://github.com/o/r/issues/61\n"
    assert fake.argvs == [list(create)]


def test_gh_issue_create_sends_each_label_as_a_labels_array_field_after_title_and_body(fake_processes, monkeypatch, github):
    create = ("gh", "api", "repos/{owner}/{repo}/issues", "-f", "title=T", "-f", "body=B",
              "-f", "labels[]=ready-for-agent", "-f", "labels[]=filed-by:x", "-q", ".html_url")
    fake = fake_gh(fake_processes, {
        create: (0, "https://github.com/o/r/issues/62\n", ""),
    })

    answer = github.gh_issue_create("T", "B", "ready-for-agent", "filed-by:x")

    assert answer == "https://github.com/o/r/issues/62\n"
    assert fake.argvs == [list(create)]


def test_gh_issue_comment_asks_gh_for_the_html_url_alone_and_answers_it_not_the_whole_comment_json(fake_processes, monkeypatch, github):
    url = "https://github.com/o/r/issues/7#issuecomment-99"
    post = ("gh", "api", "repos/{owner}/{repo}/issues/7/comments", "-f", "body=B")
    fake_gh(fake_processes, {
        post + ("-q", ".html_url"): (0, url + "\n", ""),
        post: (0, '{"id":99,"html_url":"%s","body":"B"}\n' % url, ""),
    })

    answer = github.gh_issue_comment("7", "B")

    assert answer == url + "\n"


def test_gh_issue_create_is_a_no_answer_with_gh_stderr_passed_through_when_the_create_fails(fake_processes, monkeypatch, capsys, github):
    create = ("gh", "api", "repos/{owner}/{repo}/issues", "-f", "title=T", "-f", "body=B", "-q", ".html_url")
    refusal = "gh: HTTP 422: Validation Failed (https://api.github.com/repos/o/r/issues)\n"
    fake = fake_processes.answers({}, default=inheriting({create: (1, "", refusal)}))

    with pytest.raises(github.NoAnswer):
        github.gh_issue_create("T", "B")

    assert fake.argvs == [list(create)]
    assert capsys.readouterr().err == refusal


def test_gh_json_answers_the_fixture_file_contents_and_makes_no_subprocess_call_when_veri_gh_json_is_set(fake_processes, monkeypatch, tmp_path, github):
    fixture = '[{"number":7,"title":"A thing"}]\n'
    (tmp_path / "prs.json").write_text(fixture)
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake = fake_gh(fake_processes, {})

    answer = github.gh_json("prs.json", "repos/{owner}/{repo}/pulls?state=open",
                            "pr", "list", "--json", "number,title")

    assert answer == fixture
    assert fake.argvs == []


def test_gh_json_answers_the_rest_pages_when_veri_gh_json_is_unset_and_no_gh_args_are_given(fake_processes, monkeypatch, github):
    path = "repos/{owner}/{repo}/issues"
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    fake = fake_gh(fake_processes, {
        ("gh", "api", path + "?page=1"): (0, '[{"number":4}]\n', ""),
        ("gh", "api", path + "?page=2"): (0, "[]\n", ""),
    })

    answer = github.gh_json("issues.json", path)

    assert answer == '[{"number":4}]'
    assert fake.argvs == [
        ["gh", "api", path + "?page=1"],
        ["gh", "api", path + "?page=2"],
    ]


def test_gh_json_answers_the_gh_list_answer_when_veri_gh_json_is_unset_and_gh_args_are_given(fake_processes, monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    path = "repos/{owner}/{repo}/pulls?state=open"
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    fake = fake_gh(fake_processes, {
        ("gh", "pr", "list", "--json", "number"): (0, '[{"number":7},{"number":9}]', ""),
    })

    answer = github.gh_json("prs.json", path, "pr", "list", "--json", "number")

    assert answer == '[{"number":7},{"number":9}]'
    assert fake.argvs == [["gh", "pr", "list", "--json", "number"]]


def test_with_veri_gh_driver_unset_the_graphql_route_reads_run_only_their_rest_call_and_a_rest_failure_is_a_no_answer(fake_processes, monkeypatch, github):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    path = "repos/{owner}/{repo}/pulls?state=open"
    fake = fake_gh(fake_processes, {
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

    assert fake.argvs == [
        ["gh", "api", "repos/{owner}/{repo}/issues/60"],
        ["gh", "api", path + "&page=1"],
        ["gh", "api", path + "&page=2"],
        ["gh", "api", path + "&page=1"],
        ["gh", "api", path + "&page=2"],
        ["gh", "api", "repos/{owner}/{repo}/issues/61"],
    ]


def test_with_veri_gh_driver_rest_the_graphql_route_reads_run_only_rest_and_a_rest_failure_is_a_no_answer_with_gh_api_stderr(fake_processes, monkeypatch, capsys, github):
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
    fake = fake_processes.answers({}, default=inheriting(answers))

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

    assert [call for call in fake.argvs if call[1] != "api"] == []
    assert [err.startswith(refusal) for err in errs] == [True, True, True]


def test_with_veri_gh_driver_graphql_the_graphql_route_reads_answer_graphql_stdout_and_a_graphql_failure_is_a_no_answer_with_no_gh_api_call(fake_processes, monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    path = "repos/{owner}/{repo}/pulls?state=open"
    fake = fake_gh(fake_processes, {
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

    assert [call for call in fake.argvs if call[1] == "api"] == []


def test_the_rest_only_operations_run_their_rest_call_and_no_graphql_call_under_each_veri_gh_driver(fake_processes, monkeypatch, github):
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    path = "repos/{owner}/{repo}/issues"
    patch = ("gh", "api", "-X", "PATCH", path + "/60", "-F", "body=@/tmp/body.md")
    create = ("gh", "api", path, "-f", "title=T", "-f", "body=B", "-q", ".html_url")
    fake = fake_gh(fake_processes, {
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
        del fake.seen[:]
        answers = []
        for operation in operations:
            try:
                answers.append(operation())
            except Exception as error:
                answers.append(type(error).__name__)
        observed[driver] = (answers, list(fake.argvs))

    pages = [["gh", "api", path + "?page=1"], ["gh", "api", path + "?page=2"]]
    expected = ([None, "https://github.com/o/r/issues/61\n", '[{"number":4}]', '[{"number":4}]'],
                [list(patch), list(create)] + pages + pages)
    assert observed == {driver: expected for driver in (None, "auto", "rest", "graphql")}


def test_with_veri_gh_json_set_gh_json_answers_the_fixture_file_contents_and_starts_no_process_under_each_veri_gh_driver(fake_processes, monkeypatch, tmp_path, github):
    fixture = '[{"number":7,"title":"A thing"}]\n'
    (tmp_path / "prs.json").write_text(fixture)
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake = fake_gh(fake_processes, {})
    path = "repos/{owner}/{repo}/pulls?state=open"
    observed = {}
    for driver in (None, "auto", "rest", "graphql"):
        if driver is None:
            monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
        else:
            monkeypatch.setenv("VERI_GH_DRIVER", driver)
        del fake.seen[:]
        answers = []
        for args in ((), ("pr", "list", "--json", "number,title")):
            try:
                answers.append(github.gh_json("prs.json", path, *args))
            except Exception as error:
                answers.append(type(error).__name__)
        observed[driver] = (answers, list(fake.argvs))

    assert observed == {driver: ([fixture, fixture], []) for driver in (None, "auto", "rest", "graphql")}


def test_the_module_is_importable_as_from_veri_import_github_and_as_import_veri_github(monkeypatch):
    monkeypatch.delitem(sys.modules, "veri.github", raising=False)
    monkeypatch.delattr(importlib.import_module("veri"), "github", raising=False)

    import veri.github as dotted_import
    from veri import github as from_import

    assert from_import is dotted_import
    assert pathlib.Path(from_import.__file__) == SCRIPTS / "veri" / "github.py"
    assert callable(from_import.gh_json)


def test_importing_the_module_starts_no_process_and_reads_veri_gh_json_only_when_called(fake_processes, monkeypatch, tmp_path):
    fake = fake_gh(fake_processes, {})
    systems = []
    monkeypatch.setattr("os.system", lambda command: systems.append(command))
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    monkeypatch.delitem(sys.modules, "veri.github", raising=False)
    monkeypatch.delattr(importlib.import_module("veri"), "github", raising=False)

    import veri.github as github

    assert fake.argvs + systems == []
    (tmp_path / "issues.json").write_text('[{"number":5}]')
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    assert github.gh_json("issues.json", "repos/{owner}/{repo}/issues") == '[{"number":5}]'
    assert fake.argvs + systems == []


def test_with_veri_gh_driver_empty_or_unknown_every_public_function_starts_no_gh_process_and_is_a_no_answer_naming_the_variable_and_value(fake_processes, monkeypatch, capsys):
    fake = fake_gh(fake_processes, {})
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

    assert (reads, fake.argvs, capsys.readouterr().err) == ([], [], "")

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
            del fake.seen[:]
            try:
                operation()
                outcome = "answered"
            except Exception as error:
                outcome = type(error).__name__
            err = capsys.readouterr().err
            outcomes.append((outcome, list(fake.argvs), err.count("\n"),
                             "VERI_GH_DRIVER" in err, "'%s'" % driver in err))
        observed[driver] = outcomes

    refused = [("NoAnswer", [], 1, True, True)] * len(operations)
    assert observed == {driver: refused for driver in ("", "REST", "gql")}


def test_gh_never_found_on_path_gives_up_once_veri_tool_wait_seconds_of_clock_have_passed_though_the_sleeps_asked_for_sum_to_less_2097(fake_processes, monkeypatch, capsys, github):
    now = [1000.0]
    sleeps = []

    def slow_sleep(seconds):
        assert len(sleeps) < 200, "still waiting after %d sleeps" % len(sleeps)
        sleeps.append(seconds)
        now[0] += 2 * seconds

    monkeypatch.setattr(time, "monotonic", lambda: now[0])
    monkeypatch.setattr(time, "time", lambda: now[0])
    monkeypatch.setattr(time, "sleep", slow_sleep)
    monkeypatch.setenv("VERI_TOOL_RETRY_SLEEP", "10")
    monkeypatch.setenv("VERI_TOOL_FAST_WAIT", "30")
    monkeypatch.setenv("VERI_TOOL_SLOW_SLEEP", "50")
    monkeypatch.setenv("VERI_TOOL_WAIT", "100")
    fake = fake_missing_gh(fake_processes)

    with pytest.raises(github.NoAnswer):
        github.gh_api("repos/{owner}/{repo}/issues/7")

    assert sleeps == [10, 10, 50]
    assert len(fake.argvs) == 4
    assert now[0] == 1140.0
    err_lines = capsys.readouterr().err.splitlines()
    assert err_lines and all("gh" in line for line in err_lines)


_INTERVALS = ("VERI_TOOL_RETRY_SLEEP", "VERI_TOOL_SLOW_SLEEP")
_LIMITS = ("VERI_TOOL_FAST_WAIT", "VERI_TOOL_WAIT")


def clear_tool_wait_tunables(monkeypatch):
    """Unset the four tool-wait tunables, so a case sees only the ones it sets."""
    for tunable in _INTERVALS + _LIMITS:
        monkeypatch.delenv(tunable, raising=False)


@pytest.mark.parametrize("name, value", [
    (name, value)
    for name in _INTERVALS + _LIMITS
    for value in (("0", "-1", "abc", "1.5", "inf", "") if name in _INTERVALS else ("-1", "abc", "1.5", "inf", ""))
])
def test_gh_never_found_on_path_with_an_invalid_tool_wait_tunable_is_a_no_answer_at_once_naming_the_variable_and_value_2097(fake_processes, monkeypatch, capsys, github, name, value):
    _, sleeps = fake_clock(monkeypatch)
    clear_tool_wait_tunables(monkeypatch)
    monkeypatch.setenv(name, value)
    fake = fake_missing_gh(fake_processes)

    with pytest.raises(github.NoAnswer):
        github.gh_api("repos/{owner}/{repo}/issues/7")

    assert sleeps == []
    assert len(fake.argvs) == 1
    err_lines = capsys.readouterr().err.splitlines()
    assert any(name in line and repr(value) in line for line in err_lines)


def test_gh_missing_from_path_with_veri_tool_fast_wait_0_is_accepted_and_waits_at_the_slow_interval_2097(fake_processes, monkeypatch, capsys, github):
    _, sleeps = fake_clock(monkeypatch)
    clear_tool_wait_tunables(monkeypatch)
    monkeypatch.setenv("VERI_TOOL_FAST_WAIT", "0")
    fake = fake_missing_gh(fake_processes, misses=1)

    run = github.gh_api("repos/{owner}/{repo}/issues/7")

    assert (run.returncode, run.stdout) == (0, '{"number":7}')
    assert sleeps == [900]
    assert len(fake.argvs) == 2
    assert "VERI_TOOL_FAST_WAIT" not in capsys.readouterr().err


def test_gh_never_found_on_path_with_veri_tool_wait_0_is_accepted_and_gives_up_at_the_first_miss_naming_gh_2097(fake_processes, monkeypatch, capsys, github):
    _, sleeps = fake_clock(monkeypatch)
    clear_tool_wait_tunables(monkeypatch)
    monkeypatch.setenv("VERI_TOOL_WAIT", "0")
    fake = fake_missing_gh(fake_processes)

    with pytest.raises(github.NoAnswer):
        github.gh_api("repos/{owner}/{repo}/issues/7")

    assert sleeps == []
    assert len(fake.argvs) == 1
    err_lines = capsys.readouterr().err.splitlines()
    assert err_lines and all("gh" in line and "VERI_TOOL_WAIT" not in line for line in err_lines)


def test_gh_never_found_on_path_with_veri_tool_wait_08_reads_8_decimal_seconds_and_gives_up_only_once_8s_of_clock_have_passed_naming_gh_2132(fake_processes, monkeypatch, capsys, github):
    now, sleeps = fake_clock(monkeypatch)
    clear_tool_wait_tunables(monkeypatch)
    monkeypatch.setenv("VERI_TOOL_RETRY_SLEEP", "2")
    monkeypatch.setenv("VERI_TOOL_FAST_WAIT", "100")
    monkeypatch.setenv("VERI_TOOL_SLOW_SLEEP", "2")
    monkeypatch.setenv("VERI_TOOL_WAIT", "08")
    fake = fake_missing_gh(fake_processes)

    with pytest.raises(github.NoAnswer):
        github.gh_api("repos/{owner}/{repo}/issues/7")

    assert (sleeps, len(fake.argvs), now[0]) == ([2, 2, 2, 2], 5, 1008.0)
    err_lines = capsys.readouterr().err.splitlines()
    assert err_lines and all("gh" in line and "VERI_TOOL_WAIT" not in line for line in err_lines)


@pytest.mark.parametrize("name, env", [
    ("VERI_TOOL_RETRY_SLEEP", {}),
    ("VERI_TOOL_SLOW_SLEEP", {"VERI_TOOL_FAST_WAIT": "0"}),
])
def test_gh_missing_from_path_with_an_interval_tunable_of_1_is_accepted_and_waits_1s_2097(fake_processes, monkeypatch, capsys, github, name, env):
    _, sleeps = fake_clock(monkeypatch)
    clear_tool_wait_tunables(monkeypatch)
    for var, value in {**env, name: "1"}.items():
        monkeypatch.setenv(var, value)
    fake = fake_missing_gh(fake_processes, misses=1)

    run = github.gh_api("repos/{owner}/{repo}/issues/7")

    assert (run.returncode, run.stdout) == (0, '{"number":7}')
    assert sleeps == [1]
    assert len(fake.argvs) == 2
    assert name not in capsys.readouterr().err


def test_gh_pr_ready_waits_out_a_rate_limit_refusal_that_clears_and_retries_the_rest_route_2581(fake_processes, monkeypatch, github, tmp_path):
    from veri import pr_ready
    monkeypatch.chdir(tmp_path)  # its ready stage's lines go to the case's own .tdd (#4230)
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    monkeypatch.delenv("VERI_GH_REFUSAL_SLEEP", raising=False)
    monkeypatch.delenv("VERI_GH_REFUSAL_RETRIES", raising=False)
    sleeps = []
    monkeypatch.setattr(time, "sleep", lambda seconds: sleeps.append(seconds))
    pulls = "repos/{owner}/{repo}/pulls/12"
    ready = ["gh", "api", "-X", "POST", pulls + "/ccr/ready_for_review"]
    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        if list(args) == ["gh", "api", pulls, "--jq", ".head.sha"]:
            return (0, "abc123\n", "")
        if list(args) == ready:
            if fake.argvs.count(ready) == 1:
                return (1, "API rate limit already exceeded\n", "")
            return (0, "{}\n", "")
        return (1, "", "")

    fake = fake_processes.answers({}, default=fake_run)

    assert pr_ready.main(["12", "abc123"]) == 0
    assert sleeps == [60]
    assert fake.argvs.count(ready) == 2


def test_gh_pr_ready_retries_a_refused_rest_route_at_most_veri_gh_refusal_retries_times_then_falls_through_to_graphql_2581(fake_processes, monkeypatch, github):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    monkeypatch.setenv("VERI_GH_REFUSAL_RETRIES", "2")
    monkeypatch.setenv("VERI_GH_REFUSAL_SLEEP", "5")
    sleeps = []
    monkeypatch.setattr(time, "sleep", lambda seconds: sleeps.append(seconds))
    pulls = "repos/{owner}/{repo}/pulls/12"
    ready = ["gh", "api", "-X", "POST", pulls + "/ccr/ready_for_review"]
    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        if list(args) == ready:
            assert fake.argvs.count(ready) <= 10, "still retrying ccr after 10 fake.argvs"
            return (1, "You have exceeded a secondary rate limit\n", "")
        if list(args) == ["gh", "api", pulls, "-q", ".node_id"]:
            return (0, "NODE\n", "")
        if args[:3] == ["gh", "api", "graphql"]:
            return (0, "{}\n", "")
        return (1, "", "")

    fake = fake_processes.answers({}, default=fake_run)

    github.gh_pr_ready("12")

    assert fake.argvs.count(ready) == 3
    assert sleeps == [5, 5]
    assert fake.argvs[-1][:3] == ["gh", "api", "graphql"]


def test_gh_pr_ready_with_veri_gh_refusal_retries_unset_retries_a_refused_rest_route_3_times_then_falls_through_to_graphql_2581(fake_processes, monkeypatch, github):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    monkeypatch.delenv("VERI_GH_REFUSAL_RETRIES", raising=False)
    monkeypatch.delenv("VERI_GH_REFUSAL_SLEEP", raising=False)
    sleeps = []
    monkeypatch.setattr(time, "sleep", lambda seconds: sleeps.append(seconds))
    pulls = "repos/{owner}/{repo}/pulls/12"
    ready = ["gh", "api", "-X", "POST", pulls + "/ccr/ready_for_review"]
    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        if list(args) == ready:
            assert fake.argvs.count(ready) <= 10, "still retrying ccr after 10 fake.argvs"
            return (1, "You have exceeded a secondary rate limit\n", "")
        if list(args) == ["gh", "api", pulls, "-q", ".node_id"]:
            return (0, "NODE\n", "")
        if args[:3] == ["gh", "api", "graphql"]:
            return (0, "{}\n", "")
        return (1, "", "")

    fake = fake_processes.answers({}, default=fake_run)

    github.gh_pr_ready("12")

    assert fake.argvs.count(ready) == 4
    assert sleeps == [60, 60, 60]
    assert fake.argvs[-1][:3] == ["gh", "api", "graphql"]


def test_gh_pr_ready_with_a_rate_limit_refusal_that_never_clears_is_a_no_answer_with_the_refusal_as_the_last_stderr_line_not_a_later_routes_404_2581(fake_processes, monkeypatch, capsys, github, tmp_path):
    from veri import pr_ready
    monkeypatch.chdir(tmp_path)  # its ready stage's lines go to the case's own .tdd (#4230)
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    monkeypatch.delenv("VERI_GH_REFUSAL_SLEEP", raising=False)
    monkeypatch.delenv("VERI_GH_REFUSAL_RETRIES", raising=False)
    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    pulls = "repos/{owner}/{repo}/pulls/12"
    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        assert len(fake.argvs) <= 50, "still calling gh after 50 fake.argvs"
        if list(args) == ["gh", "api", pulls, "--jq", ".head.sha"]:
            return (0, "abc123\n", "")
        if list(args) == ["gh", "pr", "ready", "12"]:
            return (1, "", "API rate limit already exceeded\n")
        return (1, "HTTP 404: Not Found\n", "")

    fake = fake_processes.answers({}, default=fake_run)

    assert pr_ready.main(["12", "abc123"]) == 2
    err_lines = capsys.readouterr().err.splitlines()
    assert err_lines[-1] == "API rate limit already exceeded"


def test_gh_pr_ready_waits_out_a_rate_limit_refusal_that_clears_and_retries_the_graphql_route_2581(fake_processes, monkeypatch, github, tmp_path):
    from veri import pr_ready
    monkeypatch.chdir(tmp_path)  # its ready stage's lines go to the case's own .tdd (#4230)
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")
    monkeypatch.delenv("VERI_GH_REFUSAL_SLEEP", raising=False)
    monkeypatch.delenv("VERI_GH_REFUSAL_RETRIES", raising=False)
    sleeps = []
    monkeypatch.setattr(time, "sleep", lambda seconds: sleeps.append(seconds))
    pulls = "repos/{owner}/{repo}/pulls/12"
    ready = ["gh", "pr", "ready", "12"]
    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        if list(args) == ["gh", "api", pulls, "--jq", ".head.sha"]:
            return (0, "abc123\n", "")
        if list(args) == ready:
            if fake.argvs.count(ready) == 1:
                return (1, "", "API rate limit already exceeded\n")
            return (0, "", "")
        return (1, "", "")

    fake = fake_processes.answers({}, default=fake_run)

    assert pr_ready.main(["12", "abc123"]) == 0
    assert sleeps == [60]
    assert fake.argvs.count(ready) == 2


def test_gh_pr_ready_does_not_retry_a_ccr_404_and_takes_no_sleep_before_falling_through_to_graphql_2581(fake_processes, monkeypatch, github):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    sleeps = []
    monkeypatch.setattr(time, "sleep", lambda seconds: sleeps.append(seconds))
    pulls = "repos/{owner}/{repo}/pulls/12"
    ready = ["gh", "api", "-X", "POST", pulls + "/ccr/ready_for_review"]
    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        if list(args) == ready:
            assert fake.argvs.count(ready) <= 10, "still retrying ccr after 10 fake.argvs"
            return (1, "gh: HTTP 404: Not Found\n", "")
        if list(args) == ["gh", "api", pulls, "-q", ".node_id"]:
            return (0, "NODE\n", "")
        if args[:3] == ["gh", "api", "graphql"]:
            return (0, "{}\n", "")
        return (1, "", "")

    fake = fake_processes.answers({}, default=fake_run)

    github.gh_pr_ready("12")

    assert fake.argvs.count(ready) == 1
    assert sleeps == []
    assert fake.argvs[-1][:3] == ["gh", "api", "graphql"]


def test_gh_pr_ready_with_a_non_integer_veri_gh_refusal_sleep_is_a_no_answer_naming_the_variable_when_ccr_answers_a_rate_limit_refusal_2581(fake_processes, monkeypatch, capsys, github):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    monkeypatch.setenv("VERI_GH_REFUSAL_SLEEP", "abc")
    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    pulls = "repos/{owner}/{repo}/pulls/12"
    ready = ["gh", "api", "-X", "POST", pulls + "/ccr/ready_for_review"]

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        if list(args) == ready:
            return (1, "API rate limit already exceeded\n", "")
        return (1, "", "")

    fake = fake_processes.answers({}, default=fake_run)

    with pytest.raises(github.NoAnswer):
        github.gh_pr_ready("12")
    assert "VERI_GH_REFUSAL_SLEEP" in capsys.readouterr().err


def test_gh_pr_ready_with_a_negative_veri_gh_refusal_retries_is_a_no_answer_naming_the_variable_when_ccr_answers_a_rate_limit_refusal_2581(fake_processes, monkeypatch, capsys, github):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    monkeypatch.setenv("VERI_GH_REFUSAL_RETRIES", "-1")
    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    pulls = "repos/{owner}/{repo}/pulls/12"
    ready = ["gh", "api", "-X", "POST", pulls + "/ccr/ready_for_review"]

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        if list(args) == ready:
            return (1, "API rate limit already exceeded\n", "")
        return (1, "", "")

    fake = fake_processes.answers({}, default=fake_run)

    with pytest.raises(github.NoAnswer):
        github.gh_pr_ready("12")
    assert "VERI_GH_REFUSAL_RETRIES" in capsys.readouterr().err


def test_a_failed_graphql_gh_call_carries_gh_stderr_in_the_no_answer_detail_only_when_the_call_asked_for_it_piped_3651(fake_processes, monkeypatch, github):
    """The fake honours the stderr argument like the real subprocess: no text unless PIPE was passed, so a
    caller that stops capturing stderr loses the 'HTTP 503' that dispatch.sh's retry reads from the detail."""
    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        said = "gh: Service Unavailable (HTTP 503)\n" if kwargs.get("stderr") == subprocess.PIPE else None
        return (1, "", said)

    fake = fake_processes.answers({}, default=fake_run)

    with pytest.raises(github.NoAnswer) as no_answer:
        github.GraphQLAdapter().list("pr", "list", "--json", "number")

    assert no_answer.value.detail == "gh: Service Unavailable (HTTP 503)\n"


@pytest.mark.parametrize("text, kind", [
    ("gh: API rate limit exceeded for user (HTTP 403)", "rate-limit"),
    ("HTTP 403: secondary thing\nRetry-After: 30", "rate-limit"),
    ("X-RateLimit-Remaining: 0", "rate-limit"),
    ("HTTP 502: Bad Gateway", "transient"),
    ("error connecting to api.github.com", "transient"),
    ("HTTP 404: Not Found", "refused"),
    ("", "refused"),
])
def test_refusal_kind_names_what_kind_of_refusal_gh_stderr_describes(github, text, kind):
    assert github.refusal_kind(text) == kind


def test_a_rate_limit_marker_wins_over_a_transient_one(github):
    assert github.refusal_kind("HTTP 503 and then: rate limit exceeded") == "rate-limit"


@pytest.mark.parametrize("answer, detail, kind", [
    ("", "API rate limit exceeded", "rate-limit"),
    ("API rate limit exceeded", "", "rate-limit"),
    ("", "HTTP 503", "transient"),
    ("", "", "refused"),
    ("partial answer", "", "refused"),
])
def test_no_answer_kind_classifies_its_detail_else_its_answer(github, answer, detail, kind):
    assert github.NoAnswer(answer, detail).kind == kind


def test_gh_pr_ready_reads_an_empty_veri_gh_driver_as_empty_and_refuses_it_not_as_the_default_rest(monkeypatch, capsys, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "")

    with pytest.raises(github.NoAnswer):
        github.gh_pr_ready("12")

    assert capsys.readouterr().err == "VERI_GH_DRIVER is '': expected auto, rest or graphql\n"


def test_every_gh_process_and_the_git_ls_remote_against_a_process_that_never_returns_end_after_veri_gh_timeout_naming_the_command_and_the_limit_3983(
        fake_processes, monkeypatch, capsys, tmp_path, github):
    monkeypatch.chdir(tmp_path)
    fake_clock(monkeypatch)
    monkeypatch.setenv("VERI_GH_TIMEOUT", "7")
    monkeypatch.setenv("VERI_GH_DRIVER", "rest")
    head = "a" * 40
    pull = "gh api repos/{owner}/{repo}/pulls/12"
    fake = fake_processes.answers({
        "gh api x": HANGS,
        "gh pr view 1": HANGS,
        "gh api rate_limit --jq .resources.core.reset": HANGS,
        pull + " --jq .head.sha": [(0, "b" * 40 + "\n", ""), (0, head + "\n", "")],
        pull + " --jq .head.ref": (0, "br\n", ""),
        "git ls-remote origin refs/heads/br": HANGS,
        "gh api -X POST repos/{owner}/{repo}/pulls/12/ccr/ready_for_review": (0, "", ""),
    }, exact=True)
    monkeypatch.setattr(os, "killpg", lambda group, sig: [c.send_signal(sig) for c in fake.popens if c.pid == group])

    run = github.run_gh("api", "x", stderr=subprocess.PIPE)
    probe = github.gh_probe("pr", "view", "1")
    reset = github.rate_limit_reset(subprocess.run)
    reset_err = capsys.readouterr().err
    github.gh_pr_ready("12", head)
    ready_err = capsys.readouterr().err

    assert (run.returncode != 0, run.stderr) == (True, "gh api x: no answer after 7s (VERI_GH_TIMEOUT)\n")
    assert (probe.returncode != 0, probe.stderr) == (True, "gh pr view 1: no answer after 7s (VERI_GH_TIMEOUT)\n")
    assert (reset, reset_err) == (None, "gh api rate_limit --jq .resources.core.reset: no answer after 7s (VERI_GH_TIMEOUT)\n")
    assert ready_err == "git ls-remote origin refs/heads/br: no answer after 7s (VERI_GH_TIMEOUT)\n"
    assert {kwargs.get("timeout") for argv, kwargs in fake.seen if argv[0] == "gh"} == {7}


def test_a_git_ls_remote_whose_group_kill_is_refused_with_eperm_as_on_macos_for_a_zombie_leader_still_answers_124_naming_the_limit_3983(
        fake_processes, monkeypatch, capsys, tmp_path, github):
    """macOS answers killpg with EPERM when the group holds only its zombie leader: git exited at the bound."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_GH_TIMEOUT", "7")
    fake = fake_processes.answers({"git ls-remote origin refs/heads/br": HANGS}, exact=True)

    def killpg(group, sig):
        for child in fake.popens:
            child.send_signal(sig)
        raise PermissionError(1, "Operation not permitted")

    monkeypatch.setattr(os, "killpg", killpg)

    listed = github.bounded_group(["git", "ls-remote", "origin", "refs/heads/br"],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

    assert (listed.returncode, listed.stdout, capsys.readouterr().err) == (
        124, "", "git ls-remote origin refs/heads/br: no answer after 7s (VERI_GH_TIMEOUT)\n")


def test_a_git_ls_remote_that_never_returns_is_started_in_its_own_session_and_its_whole_process_group_killed_at_veri_gh_timeout_3983(
        fake_processes, monkeypatch, capsys, tmp_path, github):
    """ssh under a git ls-remote outlives a kill of git alone; the group kill takes it too."""
    monkeypatch.chdir(tmp_path)
    fake_clock(monkeypatch)
    monkeypatch.setenv("VERI_GH_TIMEOUT", "7")
    monkeypatch.setenv("VERI_GH_DRIVER", "rest")
    head = "a" * 40
    pull = "gh api repos/{owner}/{repo}/pulls/12"
    fake = fake_processes.answers({
        pull + " --jq .head.sha": [(0, "b" * 40 + "\n", ""), (0, head + "\n", "")],
        pull + " --jq .head.ref": (0, "br\n", ""),
        "git ls-remote origin refs/heads/br": HANGS,
        "gh api -X POST repos/{owner}/{repo}/pulls/12/ccr/ready_for_review": (0, "", ""),
    }, exact=True)
    killed = []

    def killpg(group, sig):
        killed.append((group, sig))
        for child in fake.popens:
            if child.pid == group:
                child.send_signal(sig)

    monkeypatch.setattr(os, "killpg", killpg)

    github.gh_pr_ready("12", head)

    started = [kwargs for argv, kwargs in fake.seen if argv[0] == "git"]
    assert (killed, [kwargs.get("start_new_session") for kwargs in started], capsys.readouterr().err) == (
        [(4242, 9)], [True], "git ls-remote origin refs/heads/br: no answer after 7s (VERI_GH_TIMEOUT)\n")


def test_pr_ready_sh_with_a_veri_gh_timeout_that_is_not_a_whole_number_of_at_least_1_exits_2_with_one_line_naming_it_and_starts_no_gh_3983(
        fake_processes, run_cli, tmp_path):
    pr_ready = importlib.import_module("veri.pr_ready")
    fake = fake_processes.answers({})
    observed = {}
    for value in ("0", "abc", "1.5", "-3", ""):
        code, out, err = run_cli(pr_ready, ["12", "a" * 40], env={"VERI_GH_TIMEOUT": value, "VERI_GH_DRIVER": "rest"},
                                 cwd=tmp_path)
        observed[value] = (code, out, err)

    assert observed == {value: (2, "", "VERI_GH_TIMEOUT: invalid value %r\n" % value)
                        for value in ("0", "abc", "1.5", "-3", "")}
    assert fake.calls == []


@pytest.mark.parametrize("driver", ["rest", "graphql", "auto"])
def test_gh_json_page_with_no_gh_args_reads_the_path_through_gh_api_never_running_bare_gh_under_each_driver_3991(
        fake_processes, monkeypatch, github, driver):
    monkeypatch.setenv("VERI_GH_DRIVER", driver)
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    path = "repos/o/r/issues/1/comments"
    fake = fake_gh(fake_processes, {("gh", "api", path): (0, '[{"body": "x"}]', "")})

    page = github.gh_json_page("", path)

    assert (page, fake.argvs) == ('[{"body": "x"}]', [["gh", "api", path]])


def test_published_keeps_a_veri_script_name_and_drops_every_directory_of_a_path_outside_home_4661(monkeypatch, github):
    monkeypatch.setenv("HOME", "/root")

    posted = [github.published(line) for line in ("/home/user/x/run-conductor.sh 7",
                                                  "/tmp/alice/secret/run-conductor.sh 7")]

    assert posted == ["<path>/run-conductor.sh 7", "<path>/run-conductor.sh 7"]


def test_published_leaves_a_temp_path_whose_last_component_only_starts_with_a_script_name_as_redact_local_left_it_4661(
        monkeypatch, github):
    monkeypatch.setenv("HOME", "/root")

    posted = [github.published(line) for line in ("/tmp/alice/x/foo.shell 7", "/tmp/alice/x/foo.sh.bak 7")]

    assert posted == ["<tmp>/alice/x/foo.shell 7", "<tmp>/alice/x/foo.sh.bak 7"]


def test_published_drops_a_directory_named_like_a_script_whole_with_the_path_after_it_4661(monkeypatch, github):
    monkeypatch.setenv("HOME", "/root")

    posted = [github.published(line) for line in ("/home/alice/x/foo.sh/secret 7", "/home/alice/x/foo.sh.bak 7")]

    assert posted == ["<path> 7", "<path> 7"]


def test_gh_pr_diff_names_answers_every_file_of_a_pr_spanning_two_rest_pages_when_graphql_refuses_issue_4664(fake_processes, monkeypatch, github):
    monkeypatch.setenv("VERI_GH_DRIVER", "rest")
    pages = {"1": [{"filename": "a/one.py"}, {"filename": "a/two.py"}], "2": [{"filename": "b/three.py"}]}

    def answer(line, **kwargs):
        if line.startswith("gh pr "):
            return (1, "", "GraphQL: HTTP 403\n")
        page = re.search(r"page=(\d+)", line)
        if line.startswith("gh api ") and "repos/{owner}/{repo}/pulls/12/files" in line and page:
            return (0, json.dumps(pages.get(page.group(1), [])) + "\n", "")
        raise AssertionError("unexpected command: %r" % (line,))

    fake_processes.answers({}, default=answer)

    assert github.gh_pr_diff_names(12) == ["a/one.py", "a/two.py", "b/three.py"]


@pytest.mark.parametrize("driver", [None, "rest", "auto"])
def test_gh_issue_list_reads_the_rest_issues_listing_dropping_pull_requests_and_upper_casing_state_issue_4663(fake_processes, monkeypatch, github, driver):
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    if driver is None:
        monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    else:
        monkeypatch.setenv("VERI_GH_DRIVER", driver)
    path = "repos/{owner}/{repo}/issues?state=all&per_page=100&page="
    fake = fake_gh(fake_processes, {
        ("gh", "api", path + "1"): (0, '[{"number":1,"state":"open","title":"a"},'
                                       '{"number":2,"state":"open","pull_request":{}}]', ""),
        ("gh", "api", path + "2"): (0, '[{"number":3,"state":"closed","title":"c"}]', ""),
        ("gh", "api", path + "3"): (0, "[]", ""),
    })

    answer = github.gh_issue_list("--state", "all", "--limit", "1000", "--json", "number,state")

    assert json.loads(answer) == [{"number": 1, "state": "OPEN"}, {"number": 3, "state": "CLOSED"}]
    assert [call[:3] for call in fake.argvs if call[1] != "api"] == []




def test_4663_gh_issue_list_under_rest_never_runs_gh_issue_list(fake_processes, monkeypatch, github):
    from urllib.parse import unquote_plus
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    monkeypatch.setenv("VERI_GH_DRIVER", "rest")
    listing = re.compile(r"gh api search/issues\?.*page=(\d+)")
    queries = []

    def rest_listing(line, **kwargs):
        found = listing.fullmatch(line)
        if not found:
            raise AssertionError("unexpected command: %r" % (line,))
        if "repo:{owner}/{repo}" not in line:
            return (1, "", "gh: Validation Failed (HTTP 422)")  # gh substitutes only a literal placeholder
        queries.append(unquote_plus(line))
        items = [{"number": 7, "title": "x in title", "html_url": "https://github.example/o/r/issues/7"}]
        return (0, json.dumps({"items": items if found.group(1) == "1" else []}), "")

    fake_processes.answers({}, default=rest_listing)
    calls = []
    real = github.run_gh

    def spy(*args, **kwargs):
        calls.append(args)
        return real(*args, **kwargs)

    monkeypatch.setattr(github, "run_gh", spy)

    out = github.gh_issue_list("--state", "open", "--limit", "5", "--search", "x in:title", "--json", "number,title")

    assert [c for c in calls if c[:2] == ("issue", "list")] == []
    assert json.loads(out) == [{"number": 7, "title": "x in title", "url": "https://github.example/o/r/issues/7"}]
    assert queries and all("repo:{owner}/{repo} is:issue" in q and "state:open" in q and "x in:title" in q for q in queries)


def test_4663_gh_issue_list_search_with_state_all_sends_no_state_qualifier_since_github_search_answers_none(
        fake_processes, monkeypatch, github):
    from urllib.parse import unquote_plus
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    monkeypatch.setenv("VERI_GH_DRIVER", "rest")
    listing = re.compile(r"gh api search/issues\?.*page=(\d+)")
    queries = []

    def github_search(line, **kwargs):
        found = listing.fullmatch(line)
        if not found:
            raise AssertionError("unexpected command: %r" % (line,))
        if "repo:{owner}/{repo}" not in line:
            return (1, "", "gh: Validation Failed (HTTP 422)")
        asked = unquote_plus(line)
        queries.append(asked)
        items = [{"number": 7, "title": "x", "html_url": "u7"}]
        return (0, json.dumps({"items": items if found.group(1) == "1" and "state:all" not in asked else []}), "")

    fake_processes.answers({}, default=github_search)

    out = github.gh_issue_list("--state", "all", "--limit", "5", "--search", "x in:title", "--json", "number")

    assert ([r["number"] for r in json.loads(out)], [q for q in queries if "state:" in q]) == ([7], [])


def test_4663_gh_issue_list_search_raises_no_answer_when_the_rest_search_read_exits_non_zero(fake_processes, monkeypatch, github):
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    monkeypatch.setenv("VERI_GH_DRIVER", "rest")
    fake_processes.answers({}, default=lambda line, **kwargs: (1, "", "HTTP 422: search failed"))

    with pytest.raises(github.NoAnswer):
        github.gh_issue_list("--state", "open", "--limit", "5", "--search", "x in:title", "--json", "number,title")
