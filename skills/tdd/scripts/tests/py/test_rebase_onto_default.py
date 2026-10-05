"""In-process cases for veri/rebase_onto_default.py, the module rebase-onto-default.sh is a shim over."""
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

PRE = "1111111111111111111111111111111111111111"
ONTO = "2222222222222222222222222222222222222222"


@pytest.fixture
def rebase_onto_default():
    return importlib.import_module("veri.rebase_onto_default")


def fake_git(monkeypatch, **overrides):
    """subprocess.run recording each command as one line, its program by basename, and
    answering each git call from a branch behind origin/main, its stdout only when piped;
    <overrides> maps a line to (exit code, stdout)."""
    answers = {
        "git rev-parse -q --verify --abbrev-ref refs/remotes/origin/HEAD": (0, "origin/main\n"),
        "git fetch -q origin": (0, ""),
        "git ls-remote origin refs/heads/main": (0, f"{ONTO}\trefs/heads/main\n"),
        "git rev-parse origin/main": (0, f"{ONTO}\n"),
        f"git merge-base --is-ancestor {ONTO} HEAD": (1, ""),
        "git rev-parse HEAD": (0, f"{PRE}\n"),
        f"git rebase -q {ONTO}": (0, ""),
    }
    answers.update(overrides)
    calls = []

    def fake_run(args, **kwargs):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        calls.append(line)
        code, out = answers.get(line, (0, ""))
        return subprocess.CompletedProcess(
            args, code, out if kwargs.get("stdout") == subprocess.PIPE else None, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def test_main_exits_2_on_a_failed_fetch_3_when_up_to_date_0_when_rebased_and_ignores_arguments(
        monkeypatch, capsys, rebase_onto_default):
    def run(argv, **overrides):
        calls = fake_git(monkeypatch, **overrides)
        code = rebase_onto_default.main(argv)
        captured = capsys.readouterr()
        assert code in range(0, 4)
        return code, captured.out, calls

    code, out, calls = run([], **{"git fetch -q origin": (1, "")})
    assert (code, out) == (2, "")
    assert [c for c in calls if c.startswith(("git ls-remote origin refs/heads/main",
                                              "git merge-base", "git rebase"))] == []

    up_to_date = {f"git merge-base --is-ancestor {ONTO} HEAD": (0, "")}
    code, out, calls = run([], **up_to_date)
    assert (code, out) == (3, "")
    assert [c for c in calls if c.startswith("git rebase")] == []

    code, out, calls = run([])
    assert (code, out) == (0, f"{PRE}\n{ONTO}\n")
    assert f"git rebase -q {ONTO}" in calls

    assert run(["--bogus"], **up_to_date)[:2] == run([], **up_to_date)[:2] == (3, "")
