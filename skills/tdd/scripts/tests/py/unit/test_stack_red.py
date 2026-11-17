"""In-process cases for veri/stack_red.py, the module stack-red.sh is a shim over (PRD 034.3a): the stack's span and
GitHub's workflow-run read are injected in-process, so no case starts a process."""
import importlib

import pytest


@pytest.fixture
def stack_red():
    return importlib.import_module("veri.stack_red")


def run(n, status="completed", conclusion="failure"):
    """Run <n>: created at second <n>, so a higher n is newer."""
    return ("%040x" % n, "https://github.com/o/r/actions/runs/%d" % n, status, conclusion, "2026-11-16T10:00:%02dZ" % n)


class World:
    """The stack's span as stack_branch.ahead answers it, the runs github.workflow_runs lists, and every branch read."""

    def __init__(self, monkeypatch, stack_red, runs, span=("stack", "trunk", [])):
        self.read = []

        def ahead(root):
            if isinstance(span, BaseException):
                raise span
            return span

        def workflow_runs(branch):
            self.read.append(branch)
            if isinstance(runs, BaseException):
                raise runs
            return list(runs)

        monkeypatch.setattr(stack_red.stack_branch, "ahead", ahead)
        monkeypatch.setattr(stack_red.github, "workflow_runs", workflow_runs)


@pytest.mark.parametrize("conclusion", ["failure", "timed_out"])
def test_prints_the_head_sha_url_and_conclusion_of_a_red_latest_answer_on_one_line_and_exits_0(
        monkeypatch, run_cli, stack_red, conclusion):
    world = World(monkeypatch, stack_red, [run(1, conclusion="success"), run(2, conclusion=conclusion)])

    got = run_cli(stack_red, [])

    assert (got, world.read) == ((0, "%040x https://github.com/o/r/actions/runs/2 %s\n" % (2, conclusion), ""), ["stack"])


@pytest.mark.parametrize("newer", [run(3, "in_progress", None), run(3, "queued", None), run(3, conclusion="cancelled")])
def test_a_newer_run_in_progress_or_concluded_cancelled_is_skipped_for_the_newest_older_completed_one(
        monkeypatch, run_cli, stack_red, newer):
    World(monkeypatch, stack_red, [newer, run(1, conclusion="success"), run(2)])

    code, out, _ = run_cli(stack_red, [])

    assert (code, out.split()[:1]) == (0, ["%040x" % 2])


@pytest.mark.parametrize("runs, said", [
    ([run(1), run(2, conclusion="success")], "success"),
    ([run(1), run(2, conclusion="neutral")], "neutral"),
    ([run(1), run(2, conclusion="skipped"), run(3, "in_progress", None)], "skipped"),
    ([], "not answered"),
    ([run(1, "in_progress", None), run(2, "queued", None)], "not answered"),
    ([run(1, conclusion="cancelled"), run(2, conclusion="cancelled")], "not answered"),
])
def test_exits_3_printing_nothing_when_the_latest_answer_is_green_or_no_run_answered_saying_which_on_stderr(
        monkeypatch, run_cli, stack_red, runs, said):
    World(monkeypatch, stack_red, runs)

    code, out, err = run_cli(stack_red, [])

    assert (code, out, err.count("\n"), err.startswith("stack-red: "), said in err) == (3, "", 1, True, True), err


@pytest.mark.parametrize("given, said", [
    ("no answer", "the workflow runs of stack: HTTP 502"),
    ("fetch", "fetch origin got no answer"),
    ("refused", "CLAUDE.md: the line names the default branch"),
    ("unnamed", "names no stack branch"),
])
def test_exits_2_with_one_stderr_line_when_github_or_a_fetch_gives_no_answer_or_stack_branch_does_not_exit_0(
        monkeypatch, run_cli, stack_red, given, said):
    runs = stack_red.github.NoAnswer("", "the workflow runs of stack: HTTP 502") if given == "no answer" else [run(1)]
    span = {"no answer": ("stack", "trunk", []), "unnamed": None,
            "fetch": stack_red.stack_branch.Refused("fetch origin got no answer (exit 128): timeout"),
            "refused": stack_red.stack_branch.Refused("CLAUDE.md: the line names the default branch")}[given]
    World(monkeypatch, stack_red, runs, span=span)

    code, out, err = run_cli(stack_red, [])

    assert (code, out, err.count("\n"), err.startswith("stack-red: "), said in err) == (2, "", 1, True, True), err


def test_exits_2_naming_its_usage_when_given_an_argument(monkeypatch, run_cli, stack_red):
    World(monkeypatch, stack_red, [run(1)])

    code, out, err = run_cli(stack_red, ["stack"])

    assert (code, out, "usage: stack-red.sh" in err) == (2, "", True)


def on(n, head, status="completed", conclusion="failure"):
    """Run <n> (created at second <n>) on the head commit sha(<head>)."""
    return ("%040x" % head, "https://github.com/o/r/actions/runs/%d" % n, status, conclusion,
            "2026-11-16T10:00:%02dZ" % n)


@pytest.mark.parametrize("runs, expected", [
    ([on(1, 7), on(2, 5, conclusion="success"), on(3, 7, "in_progress", None)], (0, 1)),
    ([on(1, 7), on(2, 5, conclusion="success"), on(3, 7, conclusion="cancelled"), on(4, 7, "queued", None)], (0, 1)),
    ([on(1, 7, conclusion="success"), on(2, 5), on(3, 7, "in_progress", None)], (3, None)),
    ([on(1, 5, conclusion="success"), on(2, 6), on(3, 7, "in_progress", None)], (0, 2)),
    ([on(1, 5), on(2, 6, conclusion="success"), on(3, 7, "in_progress", None)], (3, None)),
])
def test_a_newest_run_not_completed_is_answered_by_the_newest_completed_run_on_its_own_head_else_the_branchs(
        monkeypatch, run_cli, stack_red, runs, expected):
    World(monkeypatch, stack_red, runs)

    code, out, err = run_cli(stack_red, [])

    code_wanted, n = expected
    assert (code, out.split()[1:2]) == (code_wanted, ["https://github.com/o/r/actions/runs/%d" % n] if n else []), err
