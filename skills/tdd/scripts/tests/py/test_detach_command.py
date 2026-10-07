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

    def fake_start(argv, stdin, stdout, stderr):
        null = stdin == subprocess.DEVNULL or (
            hasattr(stdin, "fileno") and os.fstat(stdin.fileno()).st_rdev == os.stat(os.devnull).st_rdev)
        for stream, text in ((stdout, b"out "), (stderr, b"err")):
            if hasattr(stream, "fileno"):
                os.write(stream.fileno(), text)
        launches.append((argv, null))
        return 4242

    monkeypatch.setattr(importlib.import_module("detach"), "start", fake_start)

    code = detach_command.main(["start", "x", "printf", "%s", "a b"])
    wrapper = '"$@"; rc=$?; echo "$rc" > "$0.tmp"; mv "$0.tmp" "$0"'
    assert launches == [(["sh", "-c", wrapper, ".tdd/x.exit", "printf", "%s", "a b"], True)]
    assert ((tdd / "x.out").read_text(), code, capsys.readouterr()) == ("out err", 0, ("", ""))


def test_start_with_no_tdd_directory_raises_naming_the_out_file_launching_nothing_and_creating_no_file(
        tmp_path, monkeypatch, capsys, detach_command):
    monkeypatch.chdir(tmp_path)
    launches = []
    monkeypatch.setattr(importlib.import_module("detach"), "start",
                        lambda *args: launches.append(args) or 4242)

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
    monkeypatch.setattr(importlib.import_module("detach"), "start",
                        lambda *args: launches.append(args) or 4242)

    for argv in ([], ["start"], ["", "x"]):
        code = detach_command.main(argv)
        assert (argv, code, capsys.readouterr(), launches) == (argv, 2, ("", USAGE), [])
    after = {path.name: (path.read_text(), path.stat().st_mtime_ns) for path in tdd.iterdir()}
    assert (after, sorted(p.name for p in tmp_path.iterdir())) == (before, [".tdd"])
