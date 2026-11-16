"""In-process cases for veri/stack_green.py, the module stack-green.sh is a shim over (PRD 034.2b): the stack's span and
GitHub's check-run reads are injected in-process, so no case starts a process."""
import importlib

import pytest


@pytest.fixture
def stack_green():
    return importlib.import_module("veri.stack_green")


@pytest.mark.parametrize("subjects, ends", [
    (["feat: a (#1)", "feat: b (#2)", "fix: a again (#1)"], [False, False, True]),
    (["feat: a (#1)", "docs: names none", "feat: b (#2)"], [False, True, True]),
    (["chore: names none", "feat: a (#1)"], [True, True]),
    (["feat: a (#12) (#13)", "fix: b (#13)"], [False, True]),
    (["feat: a (#5)", "feat: b (#6)", 'Revert "feat: a (#5)"'], [True, False, True]),
    (["feat: (#12) mid-subject", "fix: b (#3)"], [True, True]),
    (["feat: a (#4)  ", "fix: b (#4)"], [False, True]),
    ([], []),
])
def test_a_commit_is_an_issue_end_when_no_issue_named_at_or_before_it_is_named_after_it_a_commit_naming_none_belonging_to_the_nearest_earlier(
        stack_green, subjects, ends):
    assert stack_green.issue_ends(subjects) == ends


OK, NEUTRAL, SKIPPED, FAILED, RUNNING = (("completed", "success"), ("completed", "neutral"), ("completed", "skipped"),
                                         ("completed", "failure"), ("in_progress", None))


def sha(n):
    return "%040x" % n


class World:
    """The stack's span as stack_branch.ahead answers it, each sha's check runs as github.check_runs answers them, and
    every sha read."""

    def __init__(self, monkeypatch, stack_green, subjects, runs, span=None):
        self.read = []
        commits = [(sha(n + 1), subject) for n, subject in enumerate(subjects)]

        def ahead(root):
            if isinstance(span, BaseException):
                raise span
            return ("stack", "trunk", commits) if span is None else span

        def check_runs(commit):
            self.read.append(commit)
            answer = runs.get(commit, [])
            if isinstance(answer, BaseException):
                raise answer
            return list(answer)

        monkeypatch.setattr(stack_green.stack_branch, "ahead", ahead)
        monkeypatch.setattr(stack_green.github, "check_runs", check_runs)


def test_prints_the_newest_issue_end_whose_check_runs_all_concluded_success_and_exits_0(monkeypatch, run_cli, stack_green):
    world = World(monkeypatch, stack_green, ["feat: a (#1)", "feat: b (#2)", "fix: b (#2)"],
                  {sha(1): [OK], sha(3): [OK, OK]})

    got = run_cli(stack_green, [])

    assert (got, world.read) == ((0, sha(3) + "\n", ""), [sha(3)])


def test_issue_ends_over_300_commits_reads_each_subject_once(stack_green):
    subjects = ["feat: part %d (#%d)" % (n, n // 2) for n in range(300)]

    ends = stack_green.issue_ends(subjects)

    assert [n for n, end in enumerate(ends) if end] == list(range(1, 300, 2))
