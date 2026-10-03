"""In-process cases for veri/push_branch.py, the module push-branch.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def push_branch():
    return importlib.import_module("veri.push_branch")


def fake_processes(monkeypatch, answer):
    """subprocess.run recording each command as one line, its program by basename;
    <answer>(line) -> (exit code, merged output)."""
    calls = []

    def fake_run(args, **kwargs):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        calls.append(line)
        code, out = answer(line)
        return subprocess.CompletedProcess(args, code, out, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def test_main_with_one_retry_runs_a_failed_push_to_its_push_failed_event(monkeypatch, capsys, push_branch):
    def answer(line):
        if line == "git push --set-upstream origin HEAD":
            return 128, "fatal: unable to access origin\n"
        return 0, ""

    calls = fake_processes(monkeypatch, answer)
    monkeypatch.setenv("VERI_PUSH_RETRIES", "1")
    monkeypatch.delenv("VERI_PUSH_BACKOFF", raising=False)

    code = push_branch.main([])

    captured = capsys.readouterr()
    assert calls == [
        "git push --set-upstream origin HEAD",
        "sleep 2",
        "git push --set-upstream origin HEAD",
        "event.sh push-failed error=fatal: unable to access origin attempts=2",
    ]
    assert (code, captured.out, captured.err) == (
        0, "", "push-branch.sh: push failed after 2 attempts; the branch is not on the remote\n")
