"""In-process cases for veri/detach_command.py, the module detach-command.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys
import time

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: detach-command.sh start <name> <cmd> [args…] | wait <name> [max-seconds]\n"


@pytest.fixture
def detach_command():
    return importlib.import_module("veri.detach_command")


def test_main_refuses_bad_arguments_starts_once_writing_the_pid_and_waits_with_0_to_3(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    launches = []

    class FakePopen:
        pid = 4242

        def __init__(self, args, **kwargs):
            launches.append(args)

    monkeypatch.setattr(subprocess, "Popen", FakePopen)
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

    for argv in ([], ["start", "x"], ["bogus", "x"]):
        code = detach_command.main(argv)
        assert (argv, code, capsys.readouterr(), launches) == (argv, 2, ("", USAGE), [])

    code = detach_command.main(["start", "x", "true"])
    assert (code, capsys.readouterr(), len(launches)) == (0, ("", ""), 1)
    assert (tmp_path / ".tdd" / "x.pid").read_text() == "4242\n"

    (tmp_path / ".tdd" / "x.pid").unlink()
    (tmp_path / ".tdd" / "x.exit").write_text("7\n")
    code = detach_command.main(["wait", "x"])
    assert (code, capsys.readouterr().out) == (1, "7\n")

    (tmp_path / ".tdd" / "x.exit").unlink()
    code = detach_command.main(["wait", "x"])
    assert code == 2

    (tmp_path / ".tdd" / "x.pid").write_text("4242\n")
    monkeypatch.setattr(os, "kill", lambda pid, signum: None)
    code = detach_command.main(["wait", "x", "0"])
    assert code == 3


def test_start_removes_a_stale_exit_truncates_out_overwrites_pid_in_place_and_prints_nothing(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    at_launch = []

    class FakePopen:
        pid = 4242

        def __init__(self, args, **kwargs):
            at_launch.append(((tdd / "x.exit").exists(), (tdd / "x.out").read_text()))

    monkeypatch.setattr(subprocess, "Popen", FakePopen)

    (tdd / "x.exit").write_text("7\n")
    (tdd / "x.out").write_text("old output\n")
    (tdd / "x.pid").write_text("99999999\n")
    inodes = ((tdd / "x.out").stat().st_ino, (tdd / "x.pid").stat().st_ino)

    code = detach_command.main(["start", "x", "true"])
    assert (code, capsys.readouterr()) == (0, ("", ""))
    assert at_launch == [(False, "")]
    assert ((tdd / "x.out").stat().st_ino, (tdd / "x.pid").stat().st_ino) == inodes
    assert ((tdd / "x.pid").read_text(), (tdd / "x.exit").exists()) == ("4242\n", False)

    code = detach_command.main(["start", "x", "true"])
    assert (code, capsys.readouterr(), at_launch[1:]) == (0, ("", ""), [(False, "")])


def test_start_launches_the_exit_recording_wrapper_through_detach_with_dev_null_in_and_out_for_both_streams(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    launches = []

    class FakePopen:
        pid = 4242

        def __init__(self, args, stdin, stdout, stderr, **kwargs):
            null = stdin == subprocess.DEVNULL or (
                hasattr(stdin, "fileno") and os.fstat(stdin.fileno()).st_rdev == os.stat(os.devnull).st_rdev)
            for stream, text in ((stdout, b"out "), (stderr, b"err")):
                if hasattr(stream, "fileno"):
                    os.write(stream.fileno(), text)
            launches.append((args, null))

    monkeypatch.setattr(subprocess, "Popen", FakePopen)

    code = detach_command.main(["start", "x", "printf", "%s", "a b"])
    wrapper = '"$@"; rc=$?; echo "$rc" > "$0.tmp"; mv "$0.tmp" "$0"'
    assert launches == [(["sh", "-c", wrapper, ".tdd/x.exit", "printf", "%s", "a b"], True)]
    assert ((tdd / "x.out").read_text(), code, capsys.readouterr()) == ("out err", 0, ("", ""))


def test_start_with_no_tdd_directory_raises_naming_the_out_file_launching_nothing_and_creating_no_file(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    launches = []
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: launches.append(args))

    with pytest.raises(FileNotFoundError) as raised:
        detach_command.main(["start", "x", "true"])
    assert (raised.value.filename, launches, list(tmp_path.iterdir())) == (".tdd/x.out", [], [])


def test_main_refuses_start_alone_and_an_empty_mode_like_no_arguments_touching_nothing(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    for name, text in (("x.exit", "7\n"), ("x.out", "old\n"), ("x.pid", "99\n"), (".exit", "5\n")):
        (tdd / name).write_text(text)
    before = {path.name: (path.read_text(), path.stat().st_mtime_ns) for path in tdd.iterdir()}
    launches = []
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: launches.append(args))

    for argv in ([], ["start"], ["", "x"]):
        code = detach_command.main(argv)
        assert (argv, code, capsys.readouterr(), launches) == (argv, 2, ("", USAGE), [])
    after = {path.name: (path.read_text(), path.stat().st_mtime_ns) for path in tdd.iterdir()}
    assert (after, sorted(p.name for p in tmp_path.iterdir())) == (before, [".tdd"])


def test_wait_refuses_a_max_seconds_not_all_ascii_digits_before_reading_any_file_but_not_an_empty_one(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "x.exit").write_text("0\n")
    (tdd / "x.pid").write_text("4242\n")
    kills = []
    monkeypatch.setattr(os, "kill", lambda pid, signum: kills.append(pid))
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

    for max_seconds in ("abc", "1.5", "10+5", "-1", " 5"):
        code = detach_command.main(["wait", "x", max_seconds])
        assert (max_seconds, code, capsys.readouterr(), kills) == (max_seconds, 2, ("", USAGE), [])

    code = detach_command.main(["wait", "x", ""])
    assert (code != 2, capsys.readouterr().err) == (True, "")


def test_wait_answers_a_recorded_code_over_a_dead_pid_and_rechecks_the_exit_file_after_a_dead_pid(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "x.pid").write_text("4242\n")
    (tdd / "x.exit").write_text("5\n")

    def dead(pid, signum):
        raise ProcessLookupError

    monkeypatch.setattr(os, "kill", dead)
    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    code = detach_command.main(["wait", "x", "0"])
    assert (code, capsys.readouterr()) == (1, ("5\n", ""))

    (tdd / "x.exit").unlink()

    def records_then_dies(pid, signum):
        (tdd / "x.exit").write_text("4\n")
        raise ProcessLookupError

    monkeypatch.setattr(os, "kill", records_then_dies)
    code = detach_command.main(["wait", "x", "0"])
    assert (code, capsys.readouterr()) == (1, ("4\n", ""))


def test_wait_answers_a_recorded_code_over_a_dead_pid_before_probing_the_pid(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "x.pid").write_text("4242\n")
    (tdd / "x.exit").write_text("6\n")
    kills = []

    def dead(pid, signum):
        kills.append((pid, signum))
        raise ProcessLookupError

    monkeypatch.setattr(os, "kill", dead)
    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    code = detach_command.main(["wait", "x", "0"])
    assert (code, capsys.readouterr(), kills) == (1, ("6\n", ""), [])


def test_wait_reads_the_exit_file_as_test_f_and_cat_do_stripping_trailing_newlines_and_following_a_symlink(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "x.pid").write_text("4242\n")

    def dead(pid, signum):
        raise ProcessLookupError

    monkeypatch.setattr(os, "kill", dead)
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

    (tdd / "x.exit").write_text(" 7 \n\n")
    code = detach_command.main(["wait", "x", "0"])
    assert (code, capsys.readouterr()) == (1, (" 7 \n", ""))

    (tdd / "x.exit").write_text("0\n\n")
    code = detach_command.main(["wait", "x", "0"])
    assert (code, capsys.readouterr()) == (0, ("", ""))

    (tdd / "x.exit").unlink()
    (tmp_path / "recorded").write_text("3\n")
    (tdd / "x.exit").symlink_to(tmp_path / "recorded")
    code = detach_command.main(["wait", "x", "0"])
    assert (code, capsys.readouterr()) == (1, ("3\n", ""))

    (tdd / "x.exit").unlink()
    (tdd / "x.exit").mkdir()
    code = detach_command.main(["wait", "x", "0"])
    assert (code, capsys.readouterr()) == (2, ("", ""))


def test_wait_reads_a_missing_empty_unparsable_esrch_or_eperm_pid_file_as_dead_answering_2_silently(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

    def alive(pid, signum):
        return None

    def esrch(pid, signum):
        raise ProcessLookupError

    def eperm(pid, signum):
        raise PermissionError

    for label, pid_text, kill in (("missing", None, alive), ("empty", "", alive),
                                  ("abc", "abc\n", alive), ("1_2", "1_2\n", alive),
                                  ("ESRCH", "4242\n", esrch), ("EPERM", "4242\n", eperm)):
        if pid_text is not None:
            (tdd / "x.pid").write_text(pid_text)
        monkeypatch.setattr(os, "kill", kill)
        code = detach_command.main(["wait", "x", "0"])
        assert (label, code, capsys.readouterr(), (tdd / "x.exit").exists()) == (
            label, 2, ("", ""), False)

    kills = []
    (tdd / "x.pid").write_text("-4242\n")
    monkeypatch.setattr(os, "kill", lambda pid, signum: kills.append((pid, signum)))
    code = detach_command.main(["wait", "x", "0"])
    assert (code, capsys.readouterr(), kills) == (3, ("", ""), [(-4242, 0)])


def test_wait_parses_the_pid_file_as_bash_kill_does_blanks_a_plus_and_leading_zeros_passing_0_and_negatives_on(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

    for pid_text, pid in ((" +007 \t\n", 7), ("\t 0 \n", 0), (" -0012\n", -12)):
        kills = []
        (tdd / "x.pid").write_text(pid_text)
        monkeypatch.setattr(os, "kill", lambda pid, signum: kills.append((pid, signum)))
        code = detach_command.main(["wait", "x", "0"])
        assert (pid_text, code, capsys.readouterr(), kills) == (pid_text, 3, ("", ""), [(pid, 0)])


def test_wait_takes_an_absent_or_empty_max_as_60_makes_one_round_for_0_and_ignores_arguments_past_max(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "x.pid").write_text("4242\n")
    monkeypatch.delenv("VERI_POLL", raising=False)
    now = [1000.0]
    sleeps, kills = [], []

    def fake_sleep(seconds):
        sleeps.append(float(seconds))
        now[0] += float(seconds)

    monkeypatch.setattr(time, "time", lambda: now[0])
    monkeypatch.setattr(time, "sleep", fake_sleep)
    monkeypatch.setattr(os, "kill", lambda pid, signum: kills.append((pid, signum)))

    for label, rest, rounds in (("absent", [], 61), ("empty", [""], 61), ("0", ["0"], 1),
                                ("past max", ["2", "junk", "-x"], 3)):
        sleeps.clear()
        kills.clear()
        code = detach_command.main(["wait", "x", *rest])
        assert (label, code, capsys.readouterr(), len(kills), sleeps) == (
            label, 3, ("", ""), rounds, [1.0] * (rounds - 1))


def test_wait_counts_whole_wall_clock_seconds_as_bash_seconds_does_so_10_9_to_11_0_is_1(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "x.pid").write_text("4242\n")
    monkeypatch.delenv("VERI_POLL", raising=False)
    clock = iter([10.9, 11.0, 12.0, 13.0])
    sleeps, kills = [], []
    monkeypatch.setattr(time, "time", lambda: next(clock))
    monkeypatch.setattr(time, "sleep", lambda seconds: sleeps.append(float(seconds)))
    monkeypatch.setattr(os, "kill", lambda pid, signum: kills.append((pid, signum)))

    code = detach_command.main(["wait", "x", "1"])
    assert (code, capsys.readouterr(), kills, sleeps) == (3, ("", ""), [(4242, 0)], [])


def test_wait_reads_a_leading_zero_max_as_bash_octal_so_010_is_8_and_08_09_never_time_out_writing_stderr_each_round(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    monkeypatch.delenv("VERI_POLL", raising=False)
    now = [1000.0]
    sleeps, kills = [], []

    def fake_sleep(seconds):
        sleeps.append(float(seconds))
        now[0] += float(seconds)

    def alive_until_100th(pid, signum):
        kills.append(pid)
        if len(kills) == 100:
            (tdd / "x.exit").write_text("0\n")

    monkeypatch.setattr(time, "time", lambda: now[0])
    monkeypatch.setattr(time, "sleep", fake_sleep)
    monkeypatch.setattr(os, "kill", alive_until_100th)

    for max_seconds, code_wanted, rounds, err_lines in (("010", 3, 9, 0), ("08", 0, 100, 100),
                                                        ("09", 0, 100, 100)):
        (tdd / "x.pid").write_text("4242\n")
        (tdd / "x.exit").unlink(missing_ok=True)
        sleeps.clear()
        kills.clear()
        code = detach_command.main(["wait", "x", max_seconds])
        out, err = capsys.readouterr()
        lines = err.splitlines()
        assert (max_seconds, code, out, len(lines), all(lines), len(kills), sleeps) == (
            max_seconds, code_wanted, "", err_lines, True, rounds, [1.0] * (rounds if code_wanted == 0 else rounds - 1))


def test_wait_sleeps_veri_poll_seconds_between_rounds_1_when_unset_or_empty_and_0_05_or_0_as_given(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "x.pid").write_text("4242\n")
    now = [1000.0]
    sleeps = []

    def fake_sleep(seconds):
        sleeps.append(float(seconds))
        now[0] += 1

    monkeypatch.setattr(time, "time", lambda: now[0])
    monkeypatch.setattr(time, "sleep", fake_sleep)
    monkeypatch.setattr(os, "kill", lambda pid, signum: None)

    for poll, slept in ((None, 1.0), ("", 1.0), ("0.05", 0.05), ("0", 0.0)):
        if poll is None:
            monkeypatch.delenv("VERI_POLL", raising=False)
        else:
            monkeypatch.setenv("VERI_POLL", poll)
        sleeps.clear()
        code = detach_command.main(["wait", "x", "2"])
        assert (poll, code, capsys.readouterr(), sleeps) == (poll, 3, ("", ""), [slept, slept])


def test_wait_polls_with_no_pause_for_a_veri_poll_not_a_non_negative_decimal_writing_one_stderr_line_each_round(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    sleeps, kills = [], []

    def finish_on_5th(pid, signum):
        kills.append(pid)
        if len(kills) == 5:
            (tdd / "x.exit").write_text("0\n")

    monkeypatch.setattr(time, "time", lambda: 1000.0)
    monkeypatch.setattr(time, "sleep", lambda seconds: sleeps.append(seconds))
    monkeypatch.setattr(os, "kill", finish_on_5th)

    for poll in ("abc", "-1"):
        monkeypatch.setenv("VERI_POLL", poll)
        (tdd / "x.pid").write_text("4242\n")
        (tdd / "x.exit").unlink(missing_ok=True)
        sleeps.clear()
        kills.clear()
        code = detach_command.main(["wait", "x"])
        out, err = capsys.readouterr()
        lines = err.splitlines()
        assert (poll, code, out, len(lines), all(lines), len(kills), sleeps) == (
            poll, 0, "", 5, True, 5, [])


def test_wait_sleeps_a_leading_dot_veri_poll_as_sleep_reads_it_with_nothing_on_stderr(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "x.pid").write_text("4242\n")
    now = [1000.0]
    sleeps = []

    def fake_time():
        now[0] += 1
        return now[0]

    monkeypatch.setattr(time, "time", fake_time)
    monkeypatch.setattr(time, "sleep", lambda seconds: sleeps.append(float(seconds)))
    monkeypatch.setattr(os, "kill", lambda pid, signum: None)
    monkeypatch.setenv("VERI_POLL", ".5")

    code = detach_command.main(["wait", "x", "2"])
    assert (code, capsys.readouterr(), sleeps) == (3, ("", ""), [0.5])
