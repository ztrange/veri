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
