"""In-process cases for veri/preserve_attempt.py, the module preserve-attempt.sh is a shim over."""
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
def preserve_attempt():
    return importlib.import_module("veri.preserve_attempt")


def fake_processes(monkeypatch):
    """Every subprocess entry point recording each command as one line, its program by basename."""
    calls = []

    def record(args, *_, **__):
        calls.append(" ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]]))
        return subprocess.CompletedProcess(args, 0, "", "")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, record)
    return calls


def test_main_refuses_missing_or_empty_arguments_with_its_usage_line_and_no_git_call(
        monkeypatch, capsys, preserve_attempt):
    calls = fake_processes(monkeypatch)

    answers = []
    for argv in ([], ["409", "3", "develop-green"], ["409", "3", "develop-green", ""]):
        code = preserve_attempt.main(argv)
        captured = capsys.readouterr()
        answers.append((argv, code, captured.out, captured.err))

    usage = "usage: preserve-attempt.sh <issue> <step> <phase> <attempt> [<mark>]\n"
    assert calls == []
    assert answers == [
        ([], 2, "", usage),
        (["409", "3", "develop-green"], 2, "", usage),
        (["409", "3", "develop-green", ""], 2, "", usage),
    ]
