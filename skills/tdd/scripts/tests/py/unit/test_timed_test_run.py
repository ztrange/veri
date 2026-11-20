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


def test_issue_4335_main_hands_the_declared_quiet_commands_output_to_the_caller_unchanged_and_returns_its_status(
        tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run):
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: quiet test files: pytest -q --no-header -rf\n")
    monkeypatch.chdir(tmp_path)
    output = b"FAILED t.py::x - boom\n1 failed, 3 passed\n"

    def run(line, **kwargs):
        handle = kwargs.get("stdout")
        if hasattr(handle, "write"):
            handle.write(output)
            handle.flush()
        else:
            os.write(1, output)
        return (1, "", "")

    fake_processes.answers({"sh": run})
    events.refuse_event_sh()

    code = timed_test_run.main(["changed", "t.py u.py", "sh", "-c", 'pytest -q --no-header -rf "$@"', "sh",
                                "t.py", "u.py"])

    out, err = capfd.readouterr()
    saved = list((tmp_path / ".tdd" / "test-runs").iterdir())
    assert (code, out, err) == (1, output.decode(), "")
    assert [p.read_bytes() for p in saved] == [output]
    assert [(r["tier"], r["status"]) for r in events.records()] == [("changed", "1")]


def test_issue_4335_main_follows_a_quiet_commands_exit_2_with_one_line_calling_it_a_broken_run_never_a_test_failure(
        tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run):
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: quiet test files: pytest -q --no-header -rf\n")
    monkeypatch.chdir(tmp_path)
    output = b"ERROR: file or directory not found: t.py\n"

    def run(line, **kwargs):
        handle = kwargs.get("stdout")
        if hasattr(handle, "write"):
            handle.write(output)
            handle.flush()
        else:
            os.write(1, output)
        return (2, "", "")

    fake_processes.answers({"sh": run})
    events.refuse_event_sh()

    code = timed_test_run.main(["changed", "t.py", "sh", "-c", 'pytest -q --no-header -rf "$@"', "sh", "t.py"])

    out, err = capfd.readouterr()
    assert (code, err) == (2, "")
    assert out.startswith(output.decode())
    added = out[len(output.decode()):].splitlines()
    assert len(added) == 1
    assert added[0].startswith("timed-test-run.sh:")
    assert "broke the run" in added[0] and "exit 2" in added[0] and "no test answer" in added[0]
    assert "fail" not in added[0].lower()


def test_issue_4335_main_prints_a_foreign_trees_changed_run_as_its_exit_code_last_20_lines_and_saved_path(
        tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run):
    monkeypatch.chdir(tmp_path)
    readings = [100.9, 102.1]
    monkeypatch.setattr(timed_test_run.time, "time", lambda: readings.pop(0))
    lines = [f"line {n:02d}" for n in range(25)]
    lines[0] = "FAILED tests/test_x.py::test_early - AssertionError: boom"
    lines[1] = "ERROR tests/test_y.py::test_err - fixture 'db' not found"
    lines[2] = "===== 1 failed, 3 passed, 1 error in 0.40s ====="
    output = ("\n".join(lines) + "\n").encode()

    def run(line, **kwargs):
        kwargs["stdout"].write(output)
        kwargs["stdout"].flush()
        return (1, "", "")

    fake_processes.answers({"npm": run})
    events.refuse_event_sh()

    code = timed_test_run.main(["changed", "a.test.js", "npm", "test", "--", "a.test.js"])

    out, err = capfd.readouterr()
    saved = list((tmp_path / ".tdd" / "test-runs").iterdir())
    assert (code, err, [p.read_bytes() for p in saved]) == (1, "", [output])
    assert out.splitlines() == [
        "timed-test-run.sh: tier changed, exit 1, 2s",
        *lines[-20:],
        f"full output: {pathlib.Path.cwd() / '.tdd' / 'test-runs' / saved[0].name}",
    ]


@pytest.mark.parametrize("command", [["sh", "-c", "other", "sh", "a", "b"], ["npm", "test", "--", "a", "b"]])
def test_issue_4335_main_gives_a_changed_run_of_another_command_the_20_line_tail_in_a_tree_declaring_a_quiet_command(
        command, tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run):
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: quiet test files: pytest -q --no-header -rf\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(timed_test_run.time, "time", lambda: 100.5)
    lines = [f"line {n:02d}" for n in range(25)]
    output = ("\n".join(lines) + "\n").encode()

    def run(line, **kwargs):
        kwargs["stdout"].write(output)
        kwargs["stdout"].flush()
        return (1, "", "")

    fake_processes.answers({command[0]: run})
    events.refuse_event_sh()

    code = timed_test_run.main(["changed", "a b", *command])

    out, err = capfd.readouterr()
    saved = list((tmp_path / ".tdd" / "test-runs").iterdir())
    assert (code, err) == (1, "")
    assert out.splitlines() == [
        "timed-test-run.sh: tier changed, exit 1, 0s",
        *lines[-20:],
        f"full output: {pathlib.Path.cwd() / '.tdd' / 'test-runs' / saved[0].name}",
    ]


def test_issue_4335_main_gives_a_changed_run_in_veris_own_tree_the_bounded_report_not_the_tail(
        tmp_path, monkeypatch, capfd, fake_processes, events, timed_test_run):
    (tmp_path / "skills" / "tdd" / "scripts" / "tests" / "py").mkdir(parents=True)
    output = b"FAILED t.py::test_x - boom\n= 1 failed, 3 passed in 0.20s =\n"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(timed_test_run.time, "time", lambda: 100.5)

    def run(line, **kwargs):
        kwargs["stdout"].write(output)
        kwargs["stdout"].flush()
        return (1, "", "")

    fake_processes.answers({"make": run})
    events.refuse_event_sh()

    code = timed_test_run.main(["changed", "t.py", "make", "test", "TESTS=t.py"])

    out, err = capfd.readouterr()
    saved = list((tmp_path / ".tdd" / "test-runs").iterdir())
    assert (code, err) == (1, "")
    assert out.splitlines() == [
        "timed-test-run.sh: tier changed, exit 1, 0s, 3 passed, 1 failed, 0 error",
        "FAILED t.py::test_x - boom",
        f"full output: {pathlib.Path.cwd() / '.tdd' / 'test-runs' / saved[0].name}",
    ]


RECORD = "4\n2026-11-19 10:00:00 +0000\n0123456\n1.00 1.00 1.00\n2 9 0\n4 10 0\nidle all 10\nidle fast 3\n"


@pytest.mark.parametrize("tier, seconds, record, stretch", [
    ("fast", 7, RECORD, ("fast", "7", "3")),
    ("fast", 6, RECORD, None),
    ("all", 21, RECORD, ("all", "21", "10")),
    ("all", 20, RECORD, None),
    ("changed", 100, RECORD, None),
    ("target", 100, RECORD, None),
    ("fast", 100, "4\n2026-11-19 10:00:00 +0000\n0123456\n1.00 1.00 1.00\n2 9 0\n4 10 0\n", None),
], ids=["fast-past-2x", "fast-at-2x", "all-past-2x", "all-at-2x", "changed", "target", "no-idle-lines"])
def test_4456_a_fast_or_all_run_past_twice_its_tiers_idle_line_writes_a_test_stretch_event_after_its_test_run(
        tier, seconds, record, stretch, tmp_path, monkeypatch, calls, events, timed_test_run):
    monkeypatch.chdir(tmp_path)
    events.refuse_event_sh()
    pathlib.Path(os.environ["VERI_TEST_CEILING_FILE"]).write_text(record)
    readings = [100, 100 + seconds]
    monkeypatch.setattr(timed_test_run.time, "time", lambda: readings.pop(0))

    code = timed_test_run.main([tier, "a", "make", "test", "TESTS=a"])

    records = events.records()
    stretches = [(r["tier"], r["seconds"], r["idle"]) for r in records if r["event"] == "test-stretch"]
    assert (code, [r["event"] for r in records][0], stretches) == (7, "test-run", [stretch] if stretch else [])
