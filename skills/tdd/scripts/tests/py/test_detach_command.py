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
