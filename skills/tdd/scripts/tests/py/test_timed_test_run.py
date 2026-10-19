"""In-process cases for veri/timed_test_run.py, the module timed-test-run.sh is a shim over."""
import importlib
import json
import os
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
    events.refuse_event_sh()
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


def test_main_runs_the_command_inheriting_everything_then_records_whole_second_seconds_and_status_in_a_test_run_event(tmp_path, monkeypatch, events, timed_test_run):
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
    events.refuse_event_sh()

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
    events.refuse_event_sh()

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


def test_main_returns_the_command_status_when_the_event_cannot_be_appended(tmp_path, monkeypatch, capfd, events, timed_test_run):
    monkeypatch.chdir(tmp_path)
    events.unappendable()

    def fake_call(args, *rest, **kwargs):
        return 3

    def fake_run(args, *rest, **kwargs):
        return subprocess.CompletedProcess(args, 3)

    monkeypatch.setattr(subprocess, "call", fake_call)
    monkeypatch.setattr(subprocess, "run", fake_run)
    events.refuse_event_sh()

    try:
        code = timed_test_run.main(["fast", "", "sh", "-c", "exit 3"])
    except Exception as raised:
        code = f"raised {type(raised).__name__}"
    capfd.readouterr()
    assert (code, events.records()) == (3, [])


@pytest.mark.process("git init making tmp_path a worktree whose subdirectory is the working directory, and a real true run")
def test_issue_1528_main_from_a_subdirectory_of_a_worktree_records_its_test_run_under_dot_tdd_of_the_toplevel(
        tmp_path, monkeypatch, timed_test_run):
    root = tmp_path / "repo"
    cwd = root / "sub"
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    monkeypatch.delenv("VERI_AWAKE_CLOCK", raising=False)

    assert timed_test_run.main(["fast", "", "true"]) == 0

    assert os.listdir(cwd) == []
    lines = (root / ".tdd" / "events.jsonl").read_text().splitlines()
    assert [json.loads(text)["event"] for text in lines] == ["test-run"]


def test_issue_1702_main_refuses_an_affected_tier_bare_make_test_with_exit_2_naming_it_running_nothing_and_recording_no_event(
        tmp_path, monkeypatch, capfd, calls, events, timed_test_run):
    monkeypatch.chdir(tmp_path)
    events.refuse_event_sh()

    code = timed_test_run.main(["affected", "ledger-steps", "make", "test"])

    err = capfd.readouterr().err
    assert (code, "make test" in err, calls, events.records()) == (2, True, [], [])


@pytest.mark.parametrize("tier", ["fast", "full", "all"])
def test_issue_1702_main_runs_and_records_a_bare_make_test_on_the_fast_full_and_all_tiers_without_refusal(
        tier, tmp_path, monkeypatch, capfd, calls, events, timed_test_run):
    monkeypatch.chdir(tmp_path)
    events.refuse_event_sh()

    code = timed_test_run.main([tier, "", "make", "test"])

    err = capfd.readouterr().err
    assert (code, err, calls, [(r["tier"], r["status"]) for r in events.records()]) == (
        7, "", [["make", "test"]], [(tier, "7")])


@pytest.mark.parametrize("command", [
    ["make", "test", "TESTS=a b"],
    ["make", "TESTS=a", "test"],
    ["bash", "t.test.sh"],
])
def test_issue_1702_main_runs_and_records_an_affected_tier_command_that_names_its_suites_or_is_not_make_test(
        command, tmp_path, monkeypatch, capfd, calls, events, timed_test_run):
    monkeypatch.chdir(tmp_path)
    events.refuse_event_sh()

    code = timed_test_run.main(["affected", "a b", *command])

    err = capfd.readouterr().err
    assert (code, err, calls, [(r["tier"], r["status"]) for r in events.records()]) == (
        7, "", [command], [("affected", "7")])


def _read_events(directory):
    path = directory / ".tdd" / "events.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.is_file() else []


@pytest.mark.process("a real sh -c run as the wrapped command")
def test_cli_runs_the_command_and_writes_one_test_run_event_with_tier_suites_and_seconds_exiting_with_its_status(
        tmp_path, run_cli, timed_test_run):
    suites = "skills/tdd/scripts/tests/unit/next-unchecked.test.sh skills/tdd/scripts/tests/event.test.sh"
    env = {"VERI_ISSUE": "342", "VERI_ACTOR": "developer", "VERI_PHASE": "green", "VERI_STEP": "1",
           "VERI_ATTEMPT": "1"}

    code, out, err = run_cli(timed_test_run, ["fast", suites, "sh", "-c", "exit 7"], env=env, cwd=tmp_path)

    records = _read_events(tmp_path)
    assert (code, len(records)) == (7, 1)
    assert (records[0]["event"], records[0]["tier"], records[0]["suites"]) == ("test-run", "fast", suites)
    assert re.fullmatch(r"[0-9]+", records[0]["seconds"])


@pytest.mark.process("a real sh -c run as the wrapped command, once exiting 7 and once exiting 0")
@pytest.mark.parametrize("want", [7, 0])
def test_cli_records_the_commands_own_exit_status_on_the_test_run_event(
        want, tmp_path, run_cli, timed_test_run):
    env = {"VERI_ISSUE": "383", "VERI_ACTOR": "developer", "VERI_PHASE": "red", "VERI_STEP": "1",
           "VERI_ATTEMPT": "1"}

    code, out, err = run_cli(timed_test_run, ["fast", "skills/tdd/scripts/tests/event.test.sh", "sh", "-c",
                                              "exit %d" % want], env=env, cwd=tmp_path)

    assert (code, [r["status"] for r in _read_events(tmp_path)]) == (want, [str(want)])


@pytest.mark.parametrize("argv", [[], ["all"], ["all", ""], ["all", "", ""], ["", "", "true"]])
def test_cli_refuses_fewer_than_three_arguments_an_empty_tier_or_an_empty_cmd_with_exit_2_and_the_usage_line_alone(
        argv, tmp_path, run_cli, timed_test_run):
    code, out, err = run_cli(timed_test_run, argv, cwd=tmp_path)

    assert (code, out, err, _read_events(tmp_path)) == (2, "", USAGE, [])


@pytest.mark.process("a real sh -c run as the wrapped command, from two working directories")
def test_cli_from_another_working_directory_answers_as_in_place_with_its_one_test_run_line_in_that_directory(
        tmp_path, run_cli, timed_test_run):
    env = {"VERI_ISSUE": "804", "VERI_ACTOR": "developer", "VERI_PHASE": "red", "VERI_STEP": "1",
           "VERI_ATTEMPT": "1"}
    argv = ["fast", "x.test.sh", "sh", "-c", "echo out; echo err >&2; exit 5"]
    here, far = tmp_path / "here", tmp_path / "far"
    here.mkdir()
    far.mkdir()

    in_place = run_cli(timed_test_run, argv, env=env, cwd=here)
    from_afar = run_cli(timed_test_run, argv, env=env, cwd=far)

    assert in_place == from_afar == (5, "out\n", "err\n")
    records = _read_events(far)
    assert [(r["event"], r["status"]) for r in records] == [("test-run", "5")]
    assert sorted(p.name for p in tmp_path.iterdir()) == ["far", "here"]
