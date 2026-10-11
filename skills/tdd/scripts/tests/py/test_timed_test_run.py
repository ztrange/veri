"""In-process cases for veri/timed_test_run.py, the module timed-test-run.sh is a shim over."""
import importlib
import re
import subprocess

import pytest

USAGE = "usage: timed-test-run.sh <tier> <suites> <cmd> [args …]\n"


@pytest.fixture
def timed_test_run():
    return importlib.import_module("veri.timed_test_run")


@pytest.fixture
def calls(monkeypatch):
    """subprocess.run, call and Popen recording each argv; the command exits 7."""
    record = []

    def fake_run(args, *rest, **kwargs):
        record.append([str(a) for a in args])
        return subprocess.CompletedProcess(args, 7)

    def fake_call(args, *rest, **kwargs):
        record.append([str(a) for a in args])
        return 7

    class FakePopen:
        def __init__(self, args, *rest, **kwargs):
            record.append([str(a) for a in args])
            self.args = args
            self.returncode = 7
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


def test_main_refuses_every_short_or_empty_argument_shape_and_passes_a_7_through_with_one_event(tmp_path, monkeypatch, capfd, calls, events, timed_test_run):
    monkeypatch.chdir(tmp_path)
    events.through()
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
    assert (calls, events.records()) == ([], [])

    code = timed_test_run.main(["fast", "", "sh", "-c", "exit 7"])
    assert code == 7
    records = events.records()
    assert len(records) == 1
    assert re.fullmatch(r"[0-9]+", records[0].pop("seconds"))
    assert records == [{"issue": "", "actor": "", "phase": "", "step": "", "event": "test-run", "attempt": "",
                        "skill_commit": "", "tier": "fast", "suites": "", "status": "7"}]


def test_main_runs_the_command_inheriting_everything_then_records_whole_second_seconds_and_status_through_the_sibling_event_sh(tmp_path, monkeypatch, events, timed_test_run):
    log = []
    readings = [100.9, 102.1]

    def clock():
        reading = readings.pop(0)
        log.append(("clock", reading))
        return reading

    def fake_call(args, *rest, **kwargs):
        log.append(("call", list(args), rest, kwargs))
        return 7

    def fake_run(args, *rest, **kwargs):
        log.append(("call", list(args), rest, kwargs))
        return subprocess.CompletedProcess(args, 7)

    class FakePopen:
        def __init__(self, args, *rest, **kwargs):
            log.append(("call", list(args), rest, kwargs))
            self.args = args
            self.returncode = 7
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

    monkeypatch.setattr(subprocess, "call", fake_call)
    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", FakePopen)
    monkeypatch.setattr(timed_test_run.time, "time", clock)
    events.through()

    inherited = {"stdin", "stdout", "stderr", "env", "cwd", "shell", "executable", "close_fds", "pass_fds"}
    for tier, suites in (("a=b", "x\ny"), ("fast", "")):
        log.clear()
        (tmp_path / tier).mkdir()
        monkeypatch.chdir(tmp_path / tier)
        readings[:] = [100.9, 102.1]
        assert timed_test_run.main([tier, suites, "sh", "-c", "exit 7"]) == 7
        assert [entry[:2] for entry in log] == [
            ("clock", 100.9),
            ("call", ["sh", "-c", "exit 7"]),
            ("clock", 102.1),
        ]
        assert events.records() == [{"issue": "", "actor": "", "phase": "", "step": "", "event": "test-run",
                                     "attempt": "", "skill_commit": "", "tier": tier, "suites": suites,
                                     "seconds": "2", "status": "7"}]
        command = log[1]
        assert command[2] == ()
        assert {key: value for key, value in command[3].items()
                if key in inherited and value is not None and value is not False
                and not (key == "close_fds" and value is True)} == {}


def test_main_returns_the_command_status_unmapped_and_records_it_127_not_found_126_not_executable_128_plus_n_for_a_signal(tmp_path, monkeypatch, capfd, events, timed_test_run):
    outcomes = {
        "true": 0,
        "seven": 7,
        "nosuchcmd": FileNotFoundError(2, "No such file or directory", "nosuchcmd"),
        "/etc/hosts": PermissionError(13, "Permission denied", "/etc/hosts"),
        "int": -2,
        "kill": -9,
        "pipe": -13,
        "term": -15,
    }
    def returncode_for(args):
        outcome = outcomes[str(args[0])]
        if isinstance(outcome, OSError):
            raise outcome
        return outcome

    def fake_call(args, *rest, **kwargs):
        return returncode_for(args)

    def fake_run(args, *rest, **kwargs):
        return subprocess.CompletedProcess(args, returncode_for(args))

    class FakePopen:
        def __init__(self, args, *rest, **kwargs):
            self.args = args
            self.returncode = returncode_for(args)
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

    monkeypatch.setattr(subprocess, "call", fake_call)
    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", FakePopen)
    events.through()

    observed = []
    for command in outcomes:
        (tmp_path / command.strip("/").replace("/", "-")).mkdir()
        monkeypatch.chdir(tmp_path / command.strip("/").replace("/", "-"))
        try:
            code = timed_test_run.main(["fast", "", command])
        except Exception as raised:
            code = f"raised {type(raised).__name__}"
        observed.append((command, code, [record["status"] for record in events.records()]))
        capfd.readouterr()
    assert observed == [
        ("true", 0, ["0"]),
        ("seven", 7, ["7"]),
        ("nosuchcmd", 127, ["127"]),
        ("/etc/hosts", 126, ["126"]),
        ("int", 130, ["130"]),
        ("kill", 137, ["137"]),
        ("pipe", 141, ["141"]),
        ("term", 143, ["143"]),
    ]


def test_main_returns_the_command_status_when_event_sh_exits_non_zero(tmp_path, monkeypatch, capfd, events, timed_test_run):
    monkeypatch.chdir(tmp_path)
    events.unappendable()

    def fake_call(args, *rest, **kwargs):
        return 3

    def fake_run(args, *rest, **kwargs):
        return subprocess.CompletedProcess(args, 3)

    monkeypatch.setattr(subprocess, "call", fake_call)
    monkeypatch.setattr(subprocess, "run", fake_run)
    events.through()

    try:
        code = timed_test_run.main(["fast", "", "sh", "-c", "exit 3"])
    except Exception as raised:
        code = f"raised {type(raised).__name__}"
    capfd.readouterr()
    assert (code, events.records()) == (3, [])
