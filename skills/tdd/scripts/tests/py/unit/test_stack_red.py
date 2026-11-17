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
