"""In-process cases for veri/stack_green.py, the module stack-green.sh is a shim over (PRD 034.2b): the stack's span and
GitHub's check-run reads are injected in-process, so no case starts a process."""
import importlib
import os
import re

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

    def __init__(self, monkeypatch, stack_green, subjects, runs, span="commits"):
        self.read = []
        commits = [(sha(n + 1), subject) for n, subject in enumerate(subjects)]

        def ahead(root):
            if isinstance(span, BaseException):
                raise span
            return ("stack", "trunk", commits) if span == "commits" else span

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


@pytest.mark.parametrize("tip, verdict", [
    ([OK], 3), ([OK, NEUTRAL, SKIPPED], 3), ([NEUTRAL, SKIPPED], 1), ([SKIPPED], 1), ([OK, FAILED, OK], 1),
    ([], 1), ([OK, ("completed", "cancelled")], 1), ([OK, ("completed", "timed_out")], 1),
    ([OK, ("completed", "action_required")], 1),
])
def test_a_commit_is_tested_only_when_its_check_runs_all_completed_success_neutral_or_skipped_with_one_success(
        monkeypatch, run_cli, stack_green, tip, verdict):
    world = World(monkeypatch, stack_green, ["feat: a (#1)", "feat: b (#2)", "fix: b (#2)"], {sha(1): [OK], sha(3): tip})

    code, out, _ = run_cli(stack_green, [])

    assert (code, out, world.read) == (0, sha(verdict) + "\n", [sha(3)] + ([sha(1)] if verdict == 1 else []))


@pytest.mark.parametrize("subjects, runs, reads", [
    (["feat: a (#1)", "feat: b (#2)"], {sha(1): [OK, RUNNING], sha(2): [RUNNING]}, 2),
    (["feat: a (#1)", "feat: b (#2)"], {sha(1): [("queued", None)], sha(2): [OK, FAILED]}, 2),
    ([], {}, 0),
    (["feat: part (#%d)" % n for n in range(1, 26)], {sha(n): [FAILED] for n in range(1, 26)}, 20),
])
def test_exits_3_with_one_stderr_line_when_no_commit_qualifies_a_run_in_progress_not_tested_reading_at_most_20_ends(
        monkeypatch, run_cli, stack_green, subjects, runs, reads):
    world = World(monkeypatch, stack_green, subjects, runs)

    code, out, err = run_cli(stack_green, [])

    assert (code, out, len(world.read), err.count("\n"), err.startswith("stack-green: ")) == (3, "", reads, 1, True), err
    assert stack_green.ENDS_READ == 20
    assert ("20" in err) == (len(subjects) > 20)


@pytest.mark.parametrize("given, said", [
    ("no answer", "the check runs of %s: HTTP 502" % sha(2)),
    ("refused", "CLAUDE.md: the line names the default branch"),
    ("unnamed", "names no stack branch"),
])
def test_exits_2_with_one_stderr_line_when_github_gives_no_answer_or_stack_branch_does_not_exit_0(
        monkeypatch, run_cli, stack_green, given, said):
    runs = {sha(2): stack_green.github.NoAnswer("", "the check runs of %s: HTTP 502" % sha(2)), sha(1): [OK]}
    span = {"no answer": "commits", "unnamed": None,
            "refused": stack_green.stack_branch.Refused("CLAUDE.md: the line names the default branch")}[given]
    World(monkeypatch, stack_green, ["feat: a (#1)", "feat: b (#2)"], runs, span=span)

    code, out, err = run_cli(stack_green, [])

    assert (code, out, err.count("\n"), err.startswith("stack-green: "), said in err) == (2, "", 1, True, True), err


def test_the_module_names_no_ci_job_or_check_name_so_every_check_run_counts(stack_green):
    with open(stack_green.__file__, encoding="utf-8") as f:
        named = [line for line in f if re.search(r'gates|"ci"|check_name|name ==', line)]

    assert named == []


@pytest.mark.parametrize("subject, issues", [
    ("feat: a (#1)", {"1"}), ("docs: z (#1, #3)", {"1", "3"}), ("fix: y (#1) (#2)", {"1", "2"}),
    ("fix: y (#1,#3)", {"1", "3"}), ("fix: y (#1 #3)", {"1", "3"}), ("fix: y (#1 and #3)", {"1", "3"}),
    ("fix: (#1, #3) mid-subject", set()), ("fix: names none", set()), ('Revert "feat: a (#5)"', set()),
])
def test_a_subject_names_every_issue_number_in_the_parenthesised_group_or_groups_it_ends_with(stack_green, subject, issues):
    assert stack_green.named(subject) == issues


def test_a_comma_form_subject_naming_an_earlier_issue_again_keeps_that_earlier_commit_from_being_an_end(stack_green):
    assert stack_green.issue_ends(["x (#1)", "y (#2)", "docs: z (#1, #3)"]) == [False, False, True]


FIXTURE = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures", "stack-subjects", "origin-main-40.txt")


def test_over_40_real_subjects_of_origin_main_the_comma_forms_name_each_issue_and_only_two_commits_are_ends(stack_green):
    with open(FIXTURE, encoding="utf-8") as f:
        newest_first = f.read().splitlines()
    subjects = newest_first[::-1]

    ends = stack_green.issue_ends(subjects)
    commas = [stack_green.named(s) for s in subjects if re.search(r"\(#\d+, #\d+", s)]

    assert ([subjects[n] for n, end in enumerate(ends) if end] == [newest_first[37], newest_first[0]],
            commas) == (True, [{"4071", "4076", "4077"}, {"4076", "4077"}])


def test_issue_ends_over_300_commits_reads_each_subject_once(stack_green):
    subjects = ["feat: part %d (#%d)" % (n, n // 2) for n in range(300)]

    ends = stack_green.issue_ends(subjects)

    assert [n for n, end in enumerate(ends) if end] == list(range(1, 300, 2))
