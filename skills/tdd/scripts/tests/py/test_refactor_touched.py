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
