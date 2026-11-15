"""In-process cases for veri/case_history.py, the git history queries tests_frozen's policy asks.

subprocess.run is faked on the module and each case runs inside tmp_path, so a fake that failed to
engage would ask git about an empty directory, never about the repository under test."""
import importlib
import subprocess

import pytest


@pytest.fixture
def case_history(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    return importlib.import_module("veri.case_history")


class Runs:
    """Stands in for subprocess.run: answers by argv after "git", records each call."""

    def __init__(self, answers):
        self.answers = answers
        self.calls = []

    def __call__(self, argv, **kwargs):
        self.calls.append((argv, kwargs))
        answer = self.answers.get(tuple(argv[1:]), (1, b"", b"fatal: nope\n"))
        if isinstance(answer, Exception):
            raise answer
        code, out, err = answer
        return subprocess.CompletedProcess(argv, code, out, err)


@pytest.fixture
def runs(monkeypatch):
    def install(answers):
        fake = Runs(answers)
        monkeypatch.setattr(subprocess, "run", fake)
        return fake
    return install


def test_toplevel_is_the_working_trees_root_without_its_newline(case_history, runs):
    runs({("rev-parse", "--show-toplevel"): (0, b"/work/repo\n", b"")})
    assert case_history.toplevel() == "/work/repo"


def test_toplevel_is_none_outside_a_repository(case_history, runs):
    runs({("rev-parse", "--show-toplevel"): (128, b"", b"fatal: not a git repository\n")})
    assert case_history.toplevel() is None


def test_has_rev_is_true_for_a_revision_git_verifies(case_history, runs):
    runs({("rev-parse", "--verify", "-q", "HEAD~1"): (0, b"", b"")})
    assert case_history.has_rev("HEAD~1") is True


def test_has_rev_is_false_for_a_revision_git_cannot_verify(case_history, runs):
    runs({})
    assert case_history.has_rev("HEAD") is False


def test_current_branch_is_the_abbreviated_head(case_history, runs):
    runs({("rev-parse", "--abbrev-ref", "HEAD"): (0, b"tdd/12-port\n", b"")})
    assert case_history.current_branch() == "tdd/12-port"


def test_current_branch_is_empty_when_git_cannot_say(case_history, runs):
    runs({})
    assert case_history.current_branch() == ""
