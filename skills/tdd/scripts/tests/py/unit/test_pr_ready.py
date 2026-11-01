"""In-process cases for veri/pr_ready.py, the module pr-ready.sh is a shim over."""
import importlib
import subprocess
import time

import pytest

OLD_SHA, NEW_SHA = "a" * 40, "b" * 40
HEAD_READ = ("gh", "api", "repos/{owner}/{repo}/pulls/42", "--jq", ".head.sha")
PORCELAIN = ("gh", "pr", "ready", "42")
CCR = ("gh", "api", "-X", "POST", "repos/{owner}/{repo}/pulls/42/ccr/ready_for_review")
NODE_ID = ("gh", "api", "repos/{owner}/{repo}/pulls/42", "-q", ".node_id")


@pytest.fixture
def pr_ready():
    return importlib.import_module("veri.pr_ready")


def fake_gh(monkeypatch, answer):
    """subprocess.run answered by <answer>(argv tuple) → (returncode, stdout, stderr); gh's stderr folded
    into stdout when the caller asked for it. Returns the list of argv tuples run, and the sleeps taken."""
    calls, sleeps = [], []

    def fake_run(args, **kwargs):
        args = tuple(str(arg) for arg in args)
        calls.append(args)
        code, out, err = answer(args)
        if kwargs.get("stderr") is subprocess.STDOUT:
            out, err = out + err, None
        return subprocess.CompletedProcess(args, code, out, err)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(time, "sleep", sleeps.append)
    return calls, sleeps


def test_pr_ready_with_other_than_two_arguments_exits_2_with_its_usage_line_and_runs_no_gh(pr_ready, run_cli, monkeypatch):
    calls, _ = fake_gh(monkeypatch, lambda args: (0, "", ""))

    results = [run_cli(pr_ready, argv) for argv in ([], ["42"], ["42", NEW_SHA, "x"])]

    assert results == [(2, "", "usage: pr-ready.sh <pr-number> <sha>\n")] * 3
    assert calls == []


def test_pr_ready_under_auto_marks_the_pr_ready_over_gh_pr_ready_once_its_head_is_the_sha(pr_ready, run_cli, monkeypatch):
    def answer(args):
        return {HEAD_READ: (0, NEW_SHA + "\n", ""), PORCELAIN: (0, "", "")}[args]
    calls, sleeps = fake_gh(monkeypatch, answer)

    result = run_cli(pr_ready, ["42", NEW_SHA], env={"VERI_GH_DRIVER": "auto"})

    assert (result, calls, sleeps) == ((0, "", ""), [HEAD_READ, PORCELAIN], [])


def test_pr_ready_reads_the_head_again_every_veri_poll_seconds_until_it_is_the_sha(pr_ready, run_cli, monkeypatch):
    heads = iter([OLD_SHA, OLD_SHA, NEW_SHA])

    def answer(args):
        if args[0] == "git":
            return 1, "", ""
        return (0, next(heads) + "\n", "") if args == HEAD_READ else (0, "", "")
    calls, sleeps = fake_gh(monkeypatch, answer)

    result = run_cli(pr_ready, ["42", NEW_SHA], env={"VERI_POLL": "3"})

    assert result == (0, "", "")
    calls = [c for c in calls if c[0] != "git"]
    assert (calls, sleeps) == ([HEAD_READ] * 3 + [CCR], [3.0, 3.0])


def test_pr_ready_exits_2_unready_naming_both_shas_when_the_head_never_becomes_the_sha(pr_ready, run_cli, monkeypatch):
    calls, sleeps = fake_gh(monkeypatch, lambda args: (1, "", "") if args[0] == "git" else (0, OLD_SHA + "\n", ""))

    code, out, err = run_cli(pr_ready, ["42", NEW_SHA], env={"VERI_POLL": "0"})
    calls = [c for c in calls if c[0] != "git"]

    assert (code, out) == (2, "")
    assert err == "gh_pr_ready: PR 42 head is %s after 30 reads, expected %s\n" % (OLD_SHA, NEW_SHA)
    assert calls == [HEAD_READ] * 30 and len(sleeps) == 29


def test_pr_ready_with_the_driver_unset_never_runs_gh_pr_ready_and_falls_back_to_the_graphql_mutation_over_gh_api(
        pr_ready, run_cli, monkeypatch):
    def answer(args):
        if args == CCR:
            return 1, "", "gh: Not Found (HTTP 404)\n"
        if args == NODE_ID:
            return 0, "PR_node\n", ""
        return 0, "", ""
    calls, _ = fake_gh(monkeypatch, answer)

    result = run_cli(pr_ready, ["42", ""])

    assert result == (0, "", "")
    assert calls[:2] == [CCR, NODE_ID]
    assert calls[2][:3] == ("gh", "api", "graphql") and calls[2][-2:] == ("-f", "id=PR_node")
    assert PORCELAIN not in calls and HEAD_READ not in calls


def test_pr_ready_exits_2_printing_each_routes_error_when_every_route_fails(pr_ready, run_cli, monkeypatch):
    def answer(args):
        if args == PORCELAIN:
            return 1, "", "GraphQL: refused (HTTP 403)\n"
        if args == CCR:
            return 1, "", "gh: Bad Gateway (HTTP 502)\n"
        return 1, "", ""
    calls, _ = fake_gh(monkeypatch, answer)

    result = run_cli(pr_ready, ["42", ""], env={"VERI_GH_DRIVER": "auto"})

    assert result == (2, "", "GraphQL: refused (HTTP 403)\ngh: Bad Gateway (HTTP 502)\n")
    assert calls == [PORCELAIN, CCR, NODE_ID]


def test_pr_ready_under_graphql_runs_only_gh_pr_ready_with_no_rest_fallback(pr_ready, run_cli, monkeypatch):
    calls, _ = fake_gh(monkeypatch, lambda args: (1, "", "GraphQL: refused (HTTP 403)\n"))

    result = run_cli(pr_ready, ["42", ""], env={"VERI_GH_DRIVER": "graphql"})

    assert (result, calls) == ((2, "", "GraphQL: refused (HTTP 403)\n"), [PORCELAIN])


@pytest.mark.parametrize("driver", ["", "soap"])
def test_pr_ready_exits_2_naming_a_bad_veri_gh_driver_and_runs_no_gh(pr_ready, run_cli, monkeypatch, driver):
    calls, _ = fake_gh(monkeypatch, lambda args: (0, "", ""))

    result = run_cli(pr_ready, ["42", NEW_SHA], env={"VERI_GH_DRIVER": driver})

    assert result == (2, "", "VERI_GH_DRIVER is '%s': expected auto, rest or graphql\n" % driver)
    assert calls == []
