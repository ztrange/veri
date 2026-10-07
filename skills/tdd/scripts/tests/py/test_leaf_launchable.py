"""In-process cases for veri/leaf_launchable.py, the module leaf-launchable.sh is a shim over."""
import importlib
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def leaf_launchable(monkeypatch, tmp_path):
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.setenv("CLAUDE_BIN", "stub-claude")
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    return importlib.import_module("veri.leaf_launchable")


class FakeProcess:
    def __init__(self, returncode):
        self.returncode = returncode

    def wait(self, timeout=None):
        return self.returncode

    def poll(self):
        return self.returncode

    def communicate(self, input=None, timeout=None):
        return None, None


def fake_probe(monkeypatch, returncode):
    """subprocess answering the leaf probe with <returncode>; any other command fails the case."""
    def check(args):
        if list(args) != ["stub-claude", "--version"]:
            raise AssertionError("unexpected command: %r" % (args,))

    def fake_run(args, **kwargs):
        check(args)
        return subprocess.CompletedProcess(args, returncode)

    def fake_call(args, **kwargs):
        check(args)
        return returncode

    def fake_popen(args, **kwargs):
        check(args)
        return FakeProcess(returncode)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "call", fake_call)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)


def test_main_returns_0_silently_for_a_launching_probe_with_or_without_an_argument_and_2_with_no_stdout_for_a_failing_one(
        capsys, monkeypatch, leaf_launchable):
    answers = []
    fake_probe(monkeypatch, 0)
    for argv in ([], ["extra"]):
        code = leaf_launchable.main(argv)
        captured = capsys.readouterr()
        answers.append((code, captured.out, captured.err))
    fake_probe(monkeypatch, 1)
    code = leaf_launchable.main([])
    captured = capsys.readouterr()
    answers.append((code, captured.out))
    assert answers == [(0, "", ""), (0, "", ""), (2, "")]
    assert all(0 <= answer[0] <= 3 for answer in answers)
