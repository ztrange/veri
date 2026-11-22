"""In-process cases for veri/supervise.py, the module supervise.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import pytest


SCRIPTS = pathlib.Path(__file__).resolve().parents[3]
USAGE = b"usage: supervise.sh <name> <cmd> [args...]\n"


@pytest.fixture
def supervise():
    return importlib.import_module("veri.supervise")


def test_cli_refuses_no_argument_an_empty_name_and_a_name_alone_through_run_cli_with_exit_2_its_usage_line_nothing_on_stdout_and_no_tdd(
        monkeypatch, tmp_path, supervise, run_cli, fake_processes):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes()
    usage = USAGE.decode()

    answers = [(argv, run_cli(supervise, argv, cwd=tmp_path)) for argv in ([], [""], ["develop-red"])]

    assert answers == [
        ([], (2, "", usage)),
        ([""], (2, "", usage)),
        (["develop-red"], (2, "", "supervise: missing <cmd>\n" + usage)),
    ]
    assert calls == []
    assert sorted(os.listdir(tmp_path)) == []


SET_BY_CLEAN_ENV = set()


REAL_WORK_TREE_HASH = importlib.import_module("frozen_record").work_tree_hash


@pytest.fixture(autouse=True)
def work_tree_hashes_to_tree(monkeypatch):
    """A directory that is no git repository hashes to "tree"; a repository, as it really does."""
    for name in ("frozen_record", "tests_frozen"):
        monkeypatch.setattr(importlib.import_module(name), "work_tree_hash",
                            lambda: REAL_WORK_TREE_HASH() if os.path.isdir(".git") else "tree")


def clean_env(monkeypatch, **env):
    """No VERI_* variable but the ones given."""
    for key in list(os.environ):
        if key in SET_BY_CLEAN_ENV:
            monkeypatch.delenv(key)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
        SET_BY_CLEAN_ENV.add(key)


def test_cli_refuses_a_kill_poll_that_is_not_a_number_through_run_cli_with_exit_2_one_stderr_line_naming_it_and_its_value_starting_nothing(
        monkeypatch, tmp_path, supervise, run_cli, fake_processes):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes()
    clean_env(monkeypatch, VERI_TIMEOUT="900")

    answers = [run_cli(supervise, ["develop-red", "true"], env={"VERI_KILL_POLL": value}, cwd=tmp_path)
               for value in ("fast", "1e3")]

    assert answers == [
        (2, "", "supervise: VERI_KILL_POLL must be a non-negative number: fast\n"),
        (2, "", "supervise: VERI_KILL_POLL must be a non-negative number: 1e3\n"),
    ]
    assert calls == []
    assert sorted(os.listdir(tmp_path)) == []


def test_header_names_the_watchdogs_clock_source_and_why_it_pauses_while_the_machine_is_suspended_for_macos_and_linux_472():
    import re
    header = []
    for line in (SCRIPTS / "supervise.sh").read_text().splitlines()[1:]:
        if not line.startswith("#"):
            break
        header.append(re.sub(r"^# ?", "", line))
    text = " ".join(header)
    claims = {
        "clock-source": r"monotonic",
        "macos": r"macOS.{0,200}(suspend|sleep)|(suspend|sleep).{0,200}macOS",
        "linux": r"Linux.{0,200}(suspend|sleep)|(suspend|sleep).{0,200}Linux",
        "pauses-in-suspend": r"(not advance|stop[a-z]* advancing|pause[a-z]*|stand[a-z]* still|stop[a-z]*).{0,160}(suspend|asleep|sleep)",
    }
    assert [name for name, pattern in claims.items() if not re.search(pattern, text)] == []


def test_red_awaits_pass_reads_an_events_log_holding_an_invalid_utf_8_byte_without_raising_and_still_reads_the_launch_and_verdict_lines_after_it(
        supervise, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    log = tmp_path / ".tdd" / "events.jsonl"
    launch = b'{"event": "launch", "phase": "red", "step": 1}\n'
    verdict = b'{"event": "verdict", "phase": "red", "step": 1, "verdict": "PASS"}\n'

    log.write_bytes(b'{"note": "bad \xff byte"}\n' + launch)
    assert supervise.red_awaits_pass("1") is True

    log.write_bytes(b'{"note": "bad \xff byte"}\n' + launch + verdict)
    assert supervise.red_awaits_pass("1") is False


def ps_answering(monkeypatch, supervise, rows):
    def captured(*args):
        assert args[0] == "ps", args
        return subprocess.CompletedProcess(list(args), 0, "".join(f"{row}\n" for row in rows), "")
    monkeypatch.setattr(supervise, "captured", captured)


def test_tree_cpu_seconds_parses_ps_output_counting_a_leafs_descendants_but_not_claude_itself_nor_processes_outside_its_tree_2566(
        monkeypatch, supervise):
    ps_answering(monkeypatch, supervise, [
        "    1     0   9:59:59.00 /sbin/launchd",
        " 4242     1   0:00.10 /bin/sh",
        " 4243  4242  50:00.00 /Users/someone/.local/bin/claude",
        " 4244  4243   0:01.50 /bin/bash",
        " 4245  4244   0:00.40 sleep",
        " 5000     1  12:00.00 claude",
    ])

    assert supervise.tree_cpu_seconds(4242) == pytest.approx(1.9)


def test_tree_cpu_seconds_reads_ps_d_hh_mm_ss_time_as_days_hours_minutes_seconds_alongside_mm_ss_and_hh_mm_ss_2566(
        monkeypatch, supervise):
    ps_answering(monkeypatch, supervise, [
        " 4242     1   0:00.00 /bin/sh",
        " 4244  4242   1-02:03:04 /bin/bash",
        " 4245  4244   01:00:00 make",
        " 4246  4244   2:30.50 python3",
    ])

    assert supervise.tree_cpu_seconds(4242) == pytest.approx(93784 + 3600 + 150.5)


def test_tree_cpu_seconds_skips_a_ps_row_of_fewer_than_four_fields_instead_of_raising_2566(monkeypatch, supervise):
    ps_answering(monkeypatch, supervise, [
        " 4242     1   0:00.00 /bin/sh",
        " 4244  4242   0:01.50 /bin/bash",
        " 4245  4244   0:00.40",
        "",
    ])

    assert supervise.tree_cpu_seconds(4242) == pytest.approx(1.5)


def test_now_with_veri_wall_clock_set_runs_that_command_split_on_spaces_and_returns_its_stdout_through_bin_sh_when_it_is_not_executable_4129(
        monkeypatch, supervise, fake_processes):
    import errno
    fake = fake_processes.answers({
        "clock --at 1000": (0, "1000\n", ""),
        "plain --at 2000": OSError(errno.ENOEXEC, "Exec format error"),
        "sh plain --at 2000": (0, "2000\n", ""),
    }, exact=True)

    readings = []
    for command in ("clock --at 1000", "plain --at 2000"):
        monkeypatch.setenv("VERI_WALL_CLOCK", command)
        readings.append(supervise.now())

    assert (readings, fake.calls) == (["1000", "2000"], ["clock --at 1000", "plain --at 2000", "sh plain --at 2000"])


def test_now_with_veri_wall_clock_unset_or_empty_returns_int_time_time_as_text_4129(monkeypatch, supervise, fake_processes):
    import time
    fake_processes.answers({"date": (0, "5\n", "")})
    monkeypatch.setattr(time, "time", lambda: 1700000000.9)

    monkeypatch.delenv("VERI_WALL_CLOCK", raising=False)
    unset = supervise.now()
    monkeypatch.setenv("VERI_WALL_CLOCK", "")
    empty = supervise.now()

    assert (unset, empty) == ("1700000000", "1700000000")


def test_mtime_of_returns_int_os_stat_st_mtime_as_text_and_now_when_the_file_is_missing_4129(
        monkeypatch, tmp_path, supervise, fake_processes):
    import time
    fake_processes.answers({"stat": (0, "5\n", ""), "date": (0, "5\n", "")})
    log = tmp_path / "develop-red.log"
    log.write_text("")
    os.utime(log, (1234567890.7, 1234567890.7))
    monkeypatch.setattr(time, "time", lambda: 1700000000.2)

    assert (supervise.mtime_of(str(log)), supervise.mtime_of(str(tmp_path / "missing.log"))) == ("1234567890", "1700000000")


def test_now_with_veri_wall_clock_unset_and_mtime_of_an_existing_and_a_missing_file_start_no_process_4129(
        monkeypatch, tmp_path, supervise, fake_processes):
    fake = fake_processes.answers({}, default=(0, "5\n", ""))
    monkeypatch.delenv("VERI_WALL_CLOCK", raising=False)
    log = tmp_path / "develop-red.log"
    log.write_text("")

    supervise.now()
    supervise.mtime_of(str(log))
    supervise.mtime_of(str(tmp_path / "missing.log"))

    assert fake.calls == []


def test_a_red_leafs_edit_to_the_pytest_leg_is_restored_with_a_production_file_restored_event_like_a_veri_module_in_veris_own_tree_4262(
        monkeypatch, tmp_path, supervise, fake_processes):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills/tdd/scripts/tests/py").mkdir(parents=True)
    leg, module = "skills/tdd/scripts/tests/leg/pytest_leg.py", "skills/tdd/scripts/veri/full_run_lock.py"
    for path in (leg, module):
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / path).write_bytes(b"before\n")
    fake_processes.answers({"git ls-files -m -z": (0, f"{leg}\0{module}\0", "")})
    events = []
    monkeypatch.setattr(supervise, "mark", lambda role, env, *fields: events.append(fields))

    before = supervise.production_files()
    for path in (leg, module):
        (tmp_path / path).write_bytes(b"the red leaf's edit\n")
    supervise.restore_production_files(before, "phase=develop-red", {}, "develop-red-1")

    assert [(tmp_path / path).read_bytes() for path in (leg, module)] == [b"before\n", b"before\n"]
    assert events == [("production-file-restored", "name=develop-red-1", f"file={leg}"),
                      ("production-file-restored", "name=develop-red-1", f"file={module}")]


def marker_judged(monkeypatch, supervise, marker, on_kill=lambda: None, started=None):
    """lock_waiting(<marker>) with pid 4343 answering `kill 0` (after `on_kill` runs) and `ps -o lstart=` printing
    `started` for it in both the pinned and the caller's locale, or failing when `started` is None."""
    pid_file = importlib.import_module("veri.pid_file")

    def kill(pid, sig):
        assert (pid, sig) == (4343, 0), "only kill 0 on the marker's pid is expected"
        on_kill()

    monkeypatch.setattr(os, "kill", kill)
    monkeypatch.setattr(pid_file, "ps_field", lambda field, pid: started if (field, int(pid)) == ("lstart", 4343) else None)
    monkeypatch.setattr(pid_file, "caller_start", lambda pid: started if int(pid) == 4343 else None)
    return supervise.lock_waiting(str(marker))


def test_a_lock_wait_marker_its_waiter_removes_after_the_read_reads_as_not_waiting_never_raising_4415(
        monkeypatch, tmp_path, supervise):
    marker = tmp_path / "wait"
    marker.write_text("4343\nMon Nov 16 10:00:00 2026\n")

    assert marker_judged(monkeypatch, supervise, marker, on_kill=lambda: marker.unlink()) is False


def test_a_lock_wait_marker_removed_before_the_read_reads_as_not_waiting_4415(monkeypatch, tmp_path, supervise):
    assert marker_judged(monkeypatch, supervise, tmp_path / "wait", started="Mon Nov 16 10:00:00 2026") is False


def test_a_lock_wait_marker_rewritten_after_the_read_is_judged_by_the_pid_that_was_read_4415(monkeypatch, tmp_path, supervise):
    marker = tmp_path / "wait"
    marker.write_text("4343\nMon Nov 16 10:00:00 2026\n")
    real_open = open

    def open_then_rewrite(file, *args, **kwargs):
        """The reader's one open, after which another marker naming pid 0 is renamed over it."""
        handle = real_open(file, *args, **kwargs)
        (tmp_path / "next").write_text("0\n")
        os.replace(tmp_path / "next", marker)
        return handle

    monkeypatch.setattr(supervise, "open", open_then_rewrite, raising=False)

    assert marker_judged(monkeypatch, supervise, marker, started="Mon Nov 16 10:00:00 2026") is True


def test_a_stream_log_whose_last_tool_use_has_its_tool_result_names_no_in_flight_tool_call_so_the_kill_keeps_todays_reason_4627(
        supervise):
    log = ('{"type":"system","subtype":"init","session_id":"s"}\n'
           '{"type":"assistant","message":{"content":[{"type":"tool_use","id":"toolu_X","name":"Bash",'
           '"input":{"command":"make test"}}]},"session_id":"s"}\n'
           '{"type":"tool_progress","tool_use_id":"toolu_X-heartbeat-3","tool_name":"Bash",'
           '"parent_tool_use_id":"toolu_X","elapsed_time_seconds":870,"heartbeat":true,"session_id":"s","uuid":"u"}\n'
           '{"type":"user","message":{"content":[{"type":"tool_result","tool_use_id":"toolu_X",'
           '"content":"ok"}]},"session_id":"s"}\n')

    assert supervise.in_flight_tool(log) is None


def test_an_in_flight_tool_calls_multi_line_command_is_named_by_its_first_line_only_cut_to_120_characters_4627(supervise):
    import json
    first = "make test TESTS=" + "x" * 200
    use = {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "toolu_X", "name": "Bash",
                                                         "input": {"command": first + "\necho done"}}]}}
    log = json.dumps(use) + "\n"

    assert supervise.in_flight_tool(log) == "Bash: " + first[:120] + "… (0s)"


@pytest.mark.parametrize("tool_input", [["make", "test"], {"command": 7}], ids=["input-a-list", "command-a-number"])
def test_an_in_flight_tool_call_whose_input_is_not_an_object_or_command_not_a_string_is_named_by_its_tool_only_4627(
        supervise, tool_input):
    import json
    use = {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "toolu_X", "name": "Bash",
                                                         "input": tool_input}]}}
    progress = {"type": "tool_progress", "tool_use_id": "toolu_X-heartbeat-3", "tool_name": "Bash",
                "parent_tool_use_id": "toolu_X", "elapsed_time_seconds": 870, "heartbeat": True}
    log = json.dumps(use) + "\n" + json.dumps(progress) + "\n"

    assert supervise.in_flight_tool(log) == "Bash (870s)"
