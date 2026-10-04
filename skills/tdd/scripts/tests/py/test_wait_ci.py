"""In-process cases for veri/wait_ci.py, the module wait-ci.sh is a shim over."""
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

USAGE = "usage: wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha]\n"


@pytest.fixture
def wait_ci():
    return importlib.import_module("veri.wait_ci")


def fake_processes(monkeypatch, answer):
    """subprocess.run and subprocess.Popen recording each command as one line, its program
    by basename; <answer>(line) -> (exit code, stdout, stderr)."""
    calls = []

    def line_of(args):
        return " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])

    def fake_run(args, **kwargs):
        line = line_of(args)
        calls.append(line)
        code, out, err = answer(line)
        return subprocess.CompletedProcess(args, code, out, err)

    def fake_popen(args, *rest, **kwargs):
        calls.append(line_of(args))
        raise AssertionError(f"unexpected Popen: {line_of(args)}")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    return calls


def test_main_refuses_a_missing_or_empty_pr_url_with_its_usage_and_no_process(monkeypatch, capsys, wait_ci):
    calls = fake_processes(monkeypatch, lambda line: (0, "", ""))

    observed = []
    for argv in ([], ["", "60"]):
        code = wait_ci.main(argv)
        captured = capsys.readouterr()
        observed.append((code, captured.out, captured.err))

    assert calls == []
    assert observed == [(2, "", USAGE), (2, "", USAGE)]
