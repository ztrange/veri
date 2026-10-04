"""In-process cases for veri/timed_test_run.py, the module timed-test-run.sh is a shim over."""
import importlib
import os
import pathlib
import re
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: timed-test-run.sh <tier> <suites> <cmd> [args …]\n"


@pytest.fixture
def timed_test_run():
    return importlib.import_module("veri.timed_test_run")


@pytest.fixture
def calls(monkeypatch):
    """subprocess.run, call and Popen recording each argv; the command exits 7, event.sh 0."""
    record = []

    def code_for(args):
        return 0 if os.path.basename(str(args[0])) == "event.sh" else 7

    def fake_run(args, *rest, **kwargs):
        record.append([str(a) for a in args])
        return subprocess.CompletedProcess(args, code_for(args))

    def fake_call(args, *rest, **kwargs):
        record.append([str(a) for a in args])
        return code_for(args)

    class FakePopen:
        def __init__(self, args, *rest, **kwargs):
            record.append([str(a) for a in args])
            self.args = args
            self.returncode = code_for(args)
            self.pid = 0

        def wait(self, timeout=None):
            return self.returncode

        def poll(self):
            return self.returncode

        def communicate(self, input=None, timeout=None):
            return None, None

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "call", fake_call)
    monkeypatch.setattr(subprocess, "Popen", FakePopen)
    return record


def test_main_refuses_every_short_or_empty_argument_shape_and_passes_a_7_through_with_one_event(capfd, calls, timed_test_run):
    refusals = []
    for argv in ([], ["all"], ["all", ""], ["all", "", ""], ["", "", "true"]):
        code = timed_test_run.main(argv)
        refusals.append((argv, code) + capfd.readouterr())
    assert refusals == [
        ([], 2, "", USAGE),
        (["all"], 2, "", USAGE),
        (["all", ""], 2, "", USAGE),
        (["all", "", ""], 2, "", USAGE),
        (["", "", "true"], 2, "", USAGE),
    ]
    assert calls == []

    code = timed_test_run.main(["fast", "", "sh", "-c", "exit 7"])
    assert code == 7
    events = [args for args in calls if os.path.basename(args[0]) == "event.sh"]
    assert len(events) == 1
    assert events[0][1:4] == ["test-run", "tier=fast", "suites="]
    assert re.fullmatch(r"seconds=[0-9]+", events[0][4])
    assert events[0][5:] == ["status=7"]
