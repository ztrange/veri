"""In-process cases for the run-state labels veri keeps on an issue: `bailed` and `pr-ready`."""
import importlib
import subprocess

import pytest

DELETE_BAILED = ("gh", "api", "-X", "DELETE", "repos/{owner}/{repo}/issues/42/labels/bailed")


def fake_gh(monkeypatch, answer):
    """subprocess.run answered by <answer>(argv tuple) → (returncode, stdout, stderr); returns the argv tuples run."""
    calls = []

    def fake_run(args, **kwargs):
        args = tuple(str(arg) for arg in args)
        calls.append(args)
        code, out, err = answer(args)
        return subprocess.CompletedProcess(args, code, out, err)

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


@pytest.fixture
def github():
    return importlib.import_module("veri.github")


def test_gh_issue_remove_label_deletes_the_label_from_the_issue(github, monkeypatch):
    calls = fake_gh(monkeypatch, lambda args: (0, "", ""))

    github.gh_issue_remove_label("42", "bailed")

    assert calls == [DELETE_BAILED]


def test_gh_issue_remove_label_raises_no_answer_when_gh_refuses_the_delete(github, monkeypatch):
    fake_gh(monkeypatch, lambda args: (1, "", "HTTP 502: Bad Gateway\n"))

    with pytest.raises(github.NoAnswer):
        github.gh_issue_remove_label("42", "bailed")
