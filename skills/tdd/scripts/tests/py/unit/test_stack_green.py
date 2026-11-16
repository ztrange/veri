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


def test_issue_ends_over_300_commits_reads_each_subject_once(stack_green):
    subjects = ["feat: part %d (#%d)" % (n, n // 2) for n in range(300)]

    ends = stack_green.issue_ends(subjects)

    assert [n for n, end in enumerate(ends) if end] == list(range(1, 300, 2))
