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


SUITE = "def test_a():\n    assert 1\n\n\ndef test_b():\n    assert 2\n"


def test_text_at_is_the_file_as_it_was_at_the_revision(case_history, runs):
    runs({("show", "abc:t_x.py"): (0, SUITE.encode(), b"")})
    assert case_history.text_at("abc", "t_x.py") == SUITE


def test_text_at_replaces_bytes_that_are_not_utf8(case_history, runs):
    runs({("show", "abc:t_x.py"): (0, b"assert '\xff'\n", b"")})
    assert case_history.text_at("abc", "t_x.py") == "assert '�'\n"


def test_text_at_is_empty_when_the_file_cannot_be_shown(case_history, runs):
    runs({})
    assert case_history.text_at("abc", "t_x.py") == ""


def test_text_at_lets_stderr_through_unless_asked_to_be_quiet(case_history, runs):
    fake = runs({("show", "abc:t_x.py"): (0, b"", b"")})
    case_history.text_at("abc", "t_x.py")
    case_history.text_at("abc", "t_x.py", quiet=True)
    assert [kwargs["stderr"] for _, kwargs in fake.calls] == [None, subprocess.DEVNULL]


def test_cases_at_names_each_case_with_its_body(case_history, runs):
    runs({("show", "abc:t_x.py"): (0, SUITE.encode(), b"")})
    assert case_history.cases_at("abc", "t_x.py") == {
        "test_a": "def test_a():\n    assert 1", "test_b": "def test_b():\n    assert 2"}


def test_cases_at_is_empty_for_a_file_absent_from_a_readable_revision(case_history, runs):
    runs({("show", "abc:t_x.py"): (128, b"", b"fatal: path does not exist\n"),
          ("ls-tree", "--name-only", "abc", "--", "t_x.py"): (0, b"", b"")})
    assert case_history.cases_at("abc", "t_x.py") == {}


def test_cases_at_raises_oserror_naming_the_command_when_the_revision_cannot_be_read(case_history, runs):
    runs({("show", "nope:t_x.py"): (128, b"", b"fatal: bad object\n  nope\n")})
    with pytest.raises(OSError, match=r"^git show nope:t_x\.py failed: fatal: bad object nope$"):
        case_history.cases_at("nope", "t_x.py")
