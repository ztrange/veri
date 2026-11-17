"""In-process cases for veri/stack_culprit.py, the module stack-culprit.sh is a shim over (PRD 034.3b): the stack's span,
GitHub's reads and comment, the worktree it adds and removes, and each alone run are injected in-process, so no case
starts a process."""
import importlib

import pytest

TOP = "/repo"


@pytest.fixture
def culprit():
    return importlib.import_module("veri.stack_culprit")


def sha(n):
    return "%040x" % n


def log(*targets):
    """A `gh run view --log-failed` log naming each target as pytest's FAILED line, with gh's prefix and a BOM."""
    return "".join("tests\tRun make test\t﻿2026-11-16T10:00:%02d.1234567Z FAILED %s - assert 0\n" % (n, t)
                   for n, t in enumerate(targets))


class World:
    """The stack (subjects, oldest first, sha(1) up), what each read answers, which cases are red at which commits, and
    every alone run, worktree step and comment made."""

    def __init__(self, monkeypatch, culprit, subjects, red=None, cases=("t/test_a.py::test_x",), reds=None,
                 absent=(), tested=(), runs=None, failed_log=None, span="commits", pulls=("pull",), comments=(),
                 add=True, alone=None):
        self.alone, self.steps, self.posted, self.checked = [], [], [], []
        commits = [(sha(n + 1), subject) for n, subject in enumerate(subjects)]
        self.red = red or (commits[-1][0] if commits else sha(99))
        reds = reds or {}

        def ahead(root):
            if isinstance(span, BaseException):
                raise span
            return ("stack", "trunk", commits) if span == "commits" else span

        def workflow_runs(branch):
            if isinstance(runs, BaseException):
                raise runs
            return list(runs) if runs is not None else [
                (self.red, "https://github.com/o/r/actions/runs/42", "completed", "failure", "2026-11-16T10:00:00Z")]

        def run_failed_log(run_id):
            if isinstance(failed_log, BaseException):
                raise failed_log
            return failed_log if failed_log is not None else log(*cases)

        def check_runs(commit):
            self.checked.append(commit)
            return [("completed", "success")] if commit in tested else [("completed", "failure")]

        def add_worktree(path, commit):
            self.steps.append(("add", path, commit))
            return add

        def checkout(path, commit):
            self.steps.append(("checkout", path, commit))
            self.at = commit
            return True

        def remove(path):
            self.steps.append(("remove", path))
            return True

        def has(path, commit, name):
            return (commit, name) not in absent

        def run_alone(path, command, target):
            self.alone.append((self.at, target))
            if alone is not None:
                return alone
            return (1, "FAILED %s - AssertionError: red at %s\n" % (target, self.at[-2:])) \
                if target in reds.get(self.at, ()) else (0, "1 passed\n")

        def stack_pulls(head, base):
            if isinstance(pulls, BaseException):
                raise pulls
            return [type("P", (), {"number": 5, "html_url": "https://github.com/o/r/pull/5"})() for _ in pulls]

        def issue_comments(number):
            return [{"body": body} for body in comments]

        def comment_post(number, body):
            self.posted.append((number, body))

        for name, fake in (("stack_branch.ahead", ahead), ("github.workflow_runs", workflow_runs),
                           ("github.run_failed_log", run_failed_log), ("github.check_runs", check_runs),
                           ("github.stack_pulls", stack_pulls), ("github.issue_comments", issue_comments),
                           ("github.gh_comment_post", comment_post)):
            module, attr = name.split(".")
            monkeypatch.setattr(getattr(culprit, module), attr, fake)
        for attr, fake in (("_add_worktree", add_worktree), ("_checkout", checkout), ("_remove_worktree", remove),
                           ("_has", has), ("_run_alone", run_alone)):
            monkeypatch.setattr(culprit, attr, fake)
        monkeypatch.setattr(culprit, "_top", lambda: TOP)
        monkeypatch.setattr(culprit, "_one_file_command", lambda root: 'make test TESTS="$1"')


def test_runs_at_most_the_first_5_cases_the_failed_log_names_saying_on_stderr_how_many_it_did_not_run(
        monkeypatch, run_cli, culprit):
    cases = ["t/test_%s.py::test_x" % c for c in "abcdefgh"]
    world = World(monkeypatch, culprit, ["feat: a (#1)"], cases=cases + cases[:1])

    code, _, err = run_cli(culprit, [sha(1)])

    assert ([target for _, target in world.alone], "3" in err and "not run" in err) == (cases[:5], True), err


@pytest.mark.parametrize("subjects, tested, ends", [
    (["feat: a (#1)", "feat: b (#2)", "fix: a again (#1)", "feat: c (#3)"], (), [1, 2, 3, 4]),
    (["feat: a (#1)", "feat: b (#2)", "fix: b (#2)", "docs: names none", "feat: c (#3)", "fix: c (#3)"], (1,), [4, 6]),
    (["feat: a (#1)", "feat: b (#2)", "fix: b (#2)", "feat: c (#3)"], (1, 3), [4]),
    (["feat: a (#1)", "feat: b (#2)", "fix: a again (#1)", "feat: c (#3)"], (2,), [1, 2, 3, 4]),
])
def test_tests_each_issue_end_oldest_first_from_the_newest_tested_kt5_end_at_or_below_the_red_sha_to_the_red_sha(
        monkeypatch, run_cli, culprit, subjects, tested, ends):
    world = World(monkeypatch, culprit, subjects, tested={sha(n) for n in tested})

    run_cli(culprit, [sha(len(subjects))])

    assert [commit for commit, _ in world.alone] == [sha(n) for n in ends]


@pytest.mark.parametrize("alone, reds", [(None, {}), (None, {sha(1): ("t/test_a.py::test_x",)}), ((None, ""), {}),
                                         ((3, ""), {})])
def test_runs_in_a_detached_worktree_of_its_own_under_the_trees_tdd_dir_removing_it_on_every_exit(
        monkeypatch, run_cli, culprit, alone, reds):
    world = World(monkeypatch, culprit, ["feat: a (#1)", "feat: b (#2)"], reds=reds, alone=alone)

    run_cli(culprit, [sha(2)])

    kinds = [step[0] for step in world.steps]
    path = world.steps[0][1]
    assert (kinds[0], kinds[-1], path.startswith(TOP + "/.tdd/"), {step[1] for step in world.steps}) == (
        "add", "remove", True, {path})


def test_a_worktree_that_cannot_be_added_is_exit_2_running_nothing_and_removing_nothing(monkeypatch, run_cli, culprit):
    world = World(monkeypatch, culprit, ["feat: a (#1)"], add=False)

    code, out, err = run_cli(culprit, [sha(1)])

    assert (code, out, world.alone, [step[0] for step in world.steps], "worktree" in err) == (2, "", [], ["add"], True)


@pytest.mark.parametrize("alone, code", [((1, "FAILED x"), 0), ((0, ""), 3), ((4, ""), 3), ((5, ""), 3), ((2, ""), 2),
                                         ((3, ""), 2), ((None, ""), 2)])
def test_a_case_is_red_only_when_its_alone_run_exits_1_0_4_and_5_are_not_red_and_any_other_exit_or_none_is_exit_2(
        monkeypatch, run_cli, culprit, alone, code):
    World(monkeypatch, culprit, ["feat: a (#1)"], alone=alone)

    got, out, err = run_cli(culprit, [sha(1)])

    assert (got, bool(out)) == (code, code == 0), err


def test_a_case_whose_file_is_absent_at_an_end_is_not_red_there_so_a_case_the_culprit_added_blames_the_culprit(
        monkeypatch, run_cli, culprit):
    case = "t/test_new.py::test_x"
    world = World(monkeypatch, culprit, ["feat: a (#1)", "feat: b (#2)"], cases=(case,), alone=(1, "FAILED x"),
                  absent={(sha(1), "t/test_new.py")})

    code, out, err = run_cli(culprit, [sha(2)])

    assert (code, world.alone, sha(2) in out) == (0, [(sha(2), case)], True), err
