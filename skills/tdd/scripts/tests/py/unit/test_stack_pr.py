"""In-process cases for veri/stack_pr.py, the module stack-pr.sh is a shim over (PRD 034.2a): the stack's span and the
GitHub reads and writes are injected in-process, so no case starts a process."""
import importlib

import pytest


@pytest.fixture
def stack_pr():
    return importlib.import_module("veri.stack_pr")


URL = "https://github.com/o/r/pull/%d"


class World:
    """The stack's span as stack_branch.ahead answers it, the open pull requests GitHub lists, and every pull request
    opened."""

    def __init__(self, monkeypatch, stack_pr, span=("stack", "trunk", [("a" * 40, "feat: x (#1)")]), pulls=(),
                 opened=URL % 9):
        self.opened, self.listed = [], []
        github, stack_branch = stack_pr.github, stack_pr.stack_branch

        def ahead(root):
            if isinstance(span, BaseException):
                raise span
            return span

        def stack_pulls(head, base):
            self.listed.append((head, base))
            if isinstance(pulls, BaseException):
                raise pulls
            return list(pulls)

        def pr_open(head, base, title, body):
            self.opened.append((head, base, title, body))
            if isinstance(opened, BaseException):
                raise opened
            return opened

        monkeypatch.setattr(stack_branch, "ahead", ahead)
        monkeypatch.setattr(github, "stack_pulls", stack_pulls)
        monkeypatch.setattr(github, "pr_open", pr_open)


def open_pull(stack_pr, number, draft=False):
    return stack_pr.github.Pull(number=number, url=None, html_url=URL % number, draft=draft, head_ref="stack",
                                head_sha="abc", body="", state="OPEN", labels=())


def test_with_the_stack_ahead_and_one_pull_request_open_from_it_to_the_default_branch_prints_its_url_opening_nothing(
        monkeypatch, run_cli, stack_pr):
    world = World(monkeypatch, stack_pr, pulls=[open_pull(stack_pr, 4)])

    got = run_cli(stack_pr, [])

    assert (got, world.listed, world.opened) == ((0, URL % 4 + "\n", ""), [("stack", "trunk")], [])


def test_with_the_stack_ahead_and_none_open_opens_one_from_the_stack_to_the_default_branch_and_prints_its_url(
        monkeypatch, run_cli, stack_pr):
    world = World(monkeypatch, stack_pr)

    got = run_cli(stack_pr, [])

    assert (got, [(head, base) for head, base, _, _ in world.opened]) == ((0, URL % 9 + "\n", ""), [("stack", "trunk")])


def test_the_body_of_the_pull_request_it_opens_says_it_is_never_merged_and_slices_are_cut_from_it_closing_nothing(
        monkeypatch, run_cli, stack_pr):
    world = World(monkeypatch, stack_pr)

    run_cli(stack_pr, [])
    body = world.opened[0][3]

    assert ("never merged" in body, "slices" in body and "cut from" in body,
            [line for line in body.splitlines() if any(w in line.lower() for w in ("closes", "fixes", "resolves"))]) == (
        True, True, [])


def test_with_the_stack_not_ahead_of_the_default_branch_opens_nothing_and_exits_3(monkeypatch, run_cli, stack_pr):
    world = World(monkeypatch, stack_pr, span=("stack", "trunk", []))

    code, out, err = run_cli(stack_pr, [])

    assert (code, out, world.listed, world.opened, err.count("\n")) == (3, "", [], [], 1)


def test_an_open_draft_tracking_pull_request_is_printed_with_one_stderr_line_saying_ci_skips_a_draft(
        monkeypatch, run_cli, stack_pr):
    world = World(monkeypatch, stack_pr, pulls=[open_pull(stack_pr, 4, draft=True)])

    code, out, err = run_cli(stack_pr, [])

    assert (code, out, world.opened, err.count("\n"), "draft" in err) == (0, URL % 4 + "\n", [], 1, True)


def no_answer(stack_pr, detail):
    return stack_pr.github.NoAnswer("", detail)


@pytest.mark.parametrize("given, code, said", [
    (dict(pulls="no answer"), 2, "reading the open pull requests from stack: HTTP 502"),
    (dict(opened="no answer"), 2, "reading the open pull requests from stack: HTTP 502"),
    (dict(pulls="two"), 2, "%s and %s" % (URL % 4, URL % 5)),
    (dict(span=None), 3, None),
    (dict(span="refused"), 2, "CLAUDE.md: the line names the default branch"),
])
def test_exits_2_on_no_answer_or_two_open_and_what_stack_branch_exits_when_not_0_opening_nothing(
        monkeypatch, run_cli, stack_pr, given, code, said):
    pulls = {"no answer": no_answer(stack_pr, "reading the open pull requests from stack: HTTP 502"),
             "two": [open_pull(stack_pr, 4), open_pull(stack_pr, 5)]}.get(given.get("pulls"), ())
    span = {None: None, "refused": stack_pr.stack_branch.Refused("CLAUDE.md: the line names the default branch")}
    world = World(monkeypatch, stack_pr, pulls=pulls,
                  opened=no_answer(stack_pr, "reading the open pull requests from stack: HTTP 502"),
                  **({"span": span[given["span"]]} if "span" in given else {}))

    got_code, out, err = run_cli(stack_pr, [])
    opened_ok = world.opened == [] or given == dict(opened="no answer")

    assert (got_code, out, opened_ok, err.count("\n") <= 1, err == "" if said is None else said in err,
            "Traceback" in err or "NoAnswer" in err) == (code, "", True, True, True, False)
