"""In-process cases for veri/refactor_touched.py, the module refactor-touched.sh is a shim over."""
import importlib
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: refactor-touched.sh <commit> | --issue <base>\n"


@pytest.fixture
def refactor_touched():
    return importlib.import_module("veri.refactor_touched")


def fake_processes(monkeypatch):
    """Every subprocess entry point recording its command; none starts a process."""
    calls = []

    def fake(args, *rest, **kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "", "")

    for entry in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, entry, fake)
    return calls


def test_main_with_no_commit_or_no_base_returns_2_with_the_usage_line_alone_and_no_process(
        monkeypatch, capsys, refactor_touched):
    calls = fake_processes(monkeypatch)

    for argv in ([], ["--issue"]):
        code = refactor_touched.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err) == (argv, 2, "", USAGE)

    assert calls == []


def test_main_with_an_unresolvable_commit_returns_2_naming_it_then_the_usage_line_and_runs_no_diff(
        monkeypatch, capsys, refactor_touched):
    sha = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    calls = []

    def fake(args, *rest, **kwargs):
        calls.append(list(args))
        code = 1 if list(args)[:4] == ["git", "rev-parse", "--verify", "--quiet"] else 0
        return subprocess.CompletedProcess(args, code, "", "")

    for entry in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, entry, fake)

    code = refactor_touched.main([sha])
    captured = capsys.readouterr()

    assert (code, captured.out, captured.err) == (
        2, "", f"refactor-touched: cannot resolve commit '{sha}'\n" + USAGE)
    assert [c for c in calls if c[:2] == ["git", "diff"]] == []
