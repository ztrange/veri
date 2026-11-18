"""In-process cases for veri/timed_test_run.py, the module timed-test-run.sh is a shim over."""
import importlib
import json
import os
import pathlib
import re
import pytest


USAGE = "usage: timed-test-run.sh <tier> <suites> <cmd> [args …]\n"


@pytest.fixture
def timed_test_run():
    return importlib.import_module("veri.timed_test_run")


class Calls(list):
    """Each argv as strings; status maps argv to the exit code (or raises), log takes full call tuples."""
    status = staticmethod(lambda args: 7)
    log = None


@pytest.fixture
def calls(fake_processes):
    """Every way subprocess starts a process, recording each argv; the command exits 7 unless status says otherwise."""
    record = Calls()
    fake = None

    def answer(line, **kwargs):
        args = fake.argvs[-1]
        rest = fake.rests[-1]
        record.append([str(a) for a in args])
        if record.log is not None:
            record.log.append(("call", list(args), rest, kwargs))
        return (record.status(args), "", "")

    fake = fake_processes.answers({"": answer})
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


def test_main_runs_the_command_inheriting_its_stdin_environment_and_directory_then_records_whole_second_seconds_and_status_in_a_test_run_event(tmp_path, monkeypatch, calls, events, timed_test_run):
    log = []
    readings = [100.9, 102.1]

    def clock():
        reading = readings.pop(0)
        log.append(("clock", reading))
        return reading

    calls.log = log
    monkeypatch.setattr(timed_test_run.time, "time", clock)
    events.refuse_event_sh()

    inherited = {"stdin", "env", "cwd", "shell", "executable", "close_fds", "pass_fds"}
    for tier, suites in (("target", "a=b\ny"), ("fast", "")):
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


def test_main_returns_the_command_status_unmapped_and_records_it_127_not_found_126_not_executable_128_plus_n_for_a_signal(tmp_path, monkeypatch, capfd, calls, events, timed_test_run):
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

    calls.status = returncode_for
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


def test_main_returns_the_command_status_when_the_event_cannot_be_appended(tmp_path, monkeypatch, capfd, calls, events, timed_test_run):
    monkeypatch.chdir(tmp_path)
    events.unappendable()

    calls.status = lambda args: 3
    events.refuse_event_sh()

    try:
        code = timed_test_run.main(["fast", "", "sh", "-c", "exit 3"])
    except Exception as raised:
        code = f"raised {type(raised).__name__}"
    capfd.readouterr()
    assert (code, events.records()) == (3, [])


def test_issue_1702_main_refuses_a_changed_tier_bare_make_test_with_exit_2_naming_it_running_nothing_and_recording_no_event(
        tmp_path, monkeypatch, capfd, calls, events, timed_test_run):
    monkeypatch.chdir(tmp_path)
    events.refuse_event_sh()

    code = timed_test_run.main(["changed", "ledger-steps", "make", "test"])

    err = capfd.readouterr().err
    assert (code, "make test" in err, calls, events.records()) == (2, True, [], [])


@pytest.mark.parametrize("tier", ["fast", "target", "all"])
def test_issue_1702_main_runs_and_records_a_bare_make_test_on_the_fast_target_and_all_tiers_without_refusal(
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
def test_issue_1702_main_runs_and_records_a_changed_tier_command_that_names_its_suites_or_is_not_make_test(
        command, tmp_path, monkeypatch, capfd, calls, events, timed_test_run):
    monkeypatch.chdir(tmp_path)
    events.refuse_event_sh()

    code = timed_test_run.main(["changed", "a b", *command])

    err = capfd.readouterr().err
    assert (code, err, calls, [(r["tier"], r["status"]) for r in events.records()]) == (
        7, "", [command], [("changed", "7")])


@pytest.mark.parametrize("tier", ["affected", "full", "Fast"])
def test_issue_4333_main_refuses_a_tier_outside_fast_changed_all_target_with_exit_2_naming_it_and_the_four_running_nothing_and_recording_no_event(
        tier, tmp_path, monkeypatch, capfd, calls, events, timed_test_run):
    monkeypatch.chdir(tmp_path)
    events.refuse_event_sh()

    code = timed_test_run.main([tier, "a b", "make", "test", "TESTS=a b"])

    out, err = capfd.readouterr()
    lines = err.splitlines()
    assert (code, out, len(lines), calls, events.records()) == (2, "", 1, [], []), err
    assert all(word in lines[0] for word in (repr(tier), "fast", "changed", "all", "target")), err


def test_issue_4333_main_saves_the_whole_output_under_dot_tdd_test_runs_and_prints_a_bounded_report_of_counts_ten_failing_cases_the_cut_and_the_path(
        tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run):
    monkeypatch.chdir(tmp_path)
    readings = [100.9, 102.1]
    monkeypatch.setattr(timed_test_run.time, "time", lambda: readings.pop(0))
    traceback = ["Traceback (most recent call last):"]
    traceback += [f'  File "deep.py", line {n}, in frame_{n}\n    descend()' for n in range(200)]
    traceback += ["E   AssertionError: boom"]
    failing = [f"FAILED tests/test_x.py::test_case_{n:02d} - AssertionError: boom {n:02d}" for n in range(14)]
    failing[0] += " " + "x" * 1000
    failing += ["ERROR tests/test_y.py::test_err - fixture 'db' not found"]
    output = "\n".join(["=" * 30 + " test session starts " + "=" * 30, "collected 25 items", "",
                        "=" * 35 + " FAILURES " + "=" * 35, "_" * 20 + " test_case_00 " + "_" * 20, *traceback,
                        "=" * 27 + " short test summary info " + "=" * 27, *failing,
                        "=" * 20 + " 14 failed, 10 passed, 1 error in 2.10s " + "=" * 20, ""]).encode()

    def run(line, **kwargs):
        handle = kwargs.get("stdout")
        if hasattr(handle, "write"):
            handle.write(output)
            handle.flush()
        else:
            os.write(1, output)
        return (1, "", "")

    fake_processes.answers({"make": run})
    events.refuse_event_sh()

    code = timed_test_run.main(["fast", "", "make", "unit"])

    out, err = capfd.readouterr()
    saved = list((tmp_path / ".tdd" / "test-runs").iterdir())
    assert (code, err, len(saved)) == (1, "", 1), out
    assert saved[0].read_bytes() == output
    assert out.splitlines() == [
        "timed-test-run.sh: tier fast, exit 1, 2s, 10 passed, 14 failed, 1 error",
        failing[0][:300],
        *failing[1:10],
        "\u2026 5 more failing cases cut",
        f"full output: {pathlib.Path.cwd() / '.tdd' / 'test-runs' / saved[0].name}",
    ]
    assert not any(word in out for word in ("Traceback", "frame_", "descend", "E   ")), out
    assert [(r["tier"], r["status"]) for r in events.records()] == [("fast", "1")]


def _read_events(directory):
    path = directory / ".tdd" / "events.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.is_file() else []


@pytest.mark.parametrize("argv", [[], ["all"], ["all", ""], ["all", "", ""], ["", "", "true"]])
def test_cli_refuses_fewer_than_three_arguments_an_empty_tier_or_an_empty_cmd_with_exit_2_and_the_usage_line_alone(
        argv, tmp_path, run_cli, timed_test_run):
    code, out, err = run_cli(timed_test_run, argv, cwd=tmp_path)

    assert (code, out, err, _read_events(tmp_path)) == (2, "", USAGE, [])


def _report_of(output, tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run):
    """Runs a fake `make unit` that writes output and exits 1, returning (code, stdout lines, stderr)."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(timed_test_run.time, "time", lambda: 100.5)

    def run(line, **kwargs):
        kwargs["stdout"].write(output)
        kwargs["stdout"].flush()
        return (1, "", "")

    fake_processes.answers({"make": run})
    events.refuse_event_sh()
    code = timed_test_run.main(["fast", "", "make", "unit"])
    out, err = capfd.readouterr()
    return code, out.splitlines(), err


def test_issue_4333_main_runs_twice_in_one_tree_saving_each_output_under_its_own_name(
        tmp_path, monkeypatch, capfd, calls, events, timed_test_run):
    monkeypatch.chdir(tmp_path)
    readings = [100.2, 101.7, 200.0, 203.4]
    monkeypatch.setattr(timed_test_run.time, "time", lambda: readings.pop(0))
    events.refuse_event_sh()

    codes = [timed_test_run.main(["fast", "", "sh", "-c", "exit 7"]) for _ in range(2)]

    err = capfd.readouterr().err
    saved = sorted(p.name for p in (tmp_path / ".tdd" / "test-runs").iterdir())
    assert (codes, err, saved) == ([7, 7], "", [f"100-fast-{os.getpid()}.log", f"200-fast-{os.getpid()}.log"])
    assert [r["status"] for r in events.records()] == ["7", "7"]


def test_issue_4333_cli_exits_2_naming_test_runs_when_it_cannot_create_the_directory_running_nothing(
        tmp_path, run_cli, calls, events, timed_test_run):
    (tmp_path / ".tdd").write_text("a file, not a directory\n")
    events.refuse_event_sh()

    code, out, err = run_cli(timed_test_run, ["fast", "", "sh", "-c", "exit 0"], cwd=tmp_path)

    assert (code, out, len(err.splitlines()), calls) == (2, "", 1, []), err
    assert "test-runs" in err, err


def test_issue_4333_report_prints_exactly_ten_failing_cases_with_no_cut_line(
        tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run):
    failing = [f"FAILED t.py::test_{n} - boom" for n in range(10)]
    output = "\n".join([*failing, "= 10 failed in 0.50s ="]).encode()

    code, lines, err = _report_of(output, tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run)

    assert (code, err, lines[1:-1]) == (1, "", failing)


def test_issue_4333_report_reads_counts_from_the_last_summary_line_only(
        tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run):
    output = b"= 1 passed in 0.10s =\n= 3 passed, 2 failed in 0.20s =\nlog: 9 passed earlier\n\xff\xfe\n"

    code, lines, err = _report_of(output, tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run)

    assert (code, err, lines[0]) == (1, "", "timed-test-run.sh: tier fast, exit 1, 0s, 3 passed, 2 failed, 0 error")


def test_issue_4333_report_reads_a_summary_of_errors_alone(
        tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run):
    output = b"ERROR t.py - ImportError\n===== 2 errors in 0.30s =====\n"

    code, lines, err = _report_of(output, tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run)

    assert (code, err, lines[:2]) == (1, "", ["timed-test-run.sh: tier fast, exit 1, 0s, 0 passed, 0 failed, 2 error",
                                              "ERROR t.py - ImportError"])


def test_issue_4333_report_says_counts_not_found_when_no_pytest_summary_line_is_in_the_output(
        tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run):
    output = b"FAILED-LOGIN is not a case\nmake: *** [unit] Error 1\n"

    code, lines, err = _report_of(output, tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run)

    assert (code, err, lines[:-1]) == (1, "", ["timed-test-run.sh: tier fast, exit 1, 0s, counts not found"])
