"""In-process cases for veri/stop_run.py, the module stop-run.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = b"usage: stop-run.sh [--mode at-ledger|at-leaf|now] <issue> | --all\n"


@pytest.fixture
def stop_run():
    return importlib.import_module("veri.stop_run")


def fake_processes(monkeypatch, answers):
    """subprocess.run answering each argv tuple in <answers> with (exit code, stdout bytes); every call recorded."""
    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        if tuple(args) not in answers:
            raise AssertionError("unexpected command: %r" % (args,))
        code, stdout = answers[tuple(args)]
        if kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding"):
            stdout = stdout.decode()
        return subprocess.CompletedProcess(args, code, stdout, None)

    def refused(*args, **kwargs):
        calls.append(list(args[0]) if args else kwargs)
        raise AssertionError("unexpected process: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    for name in ("Popen", "call", "check_call", "check_output", "getoutput", "getstatusoutput"):
        monkeypatch.setattr(subprocess, name, refused)
    return calls


def test_main_refuses_no_issue_and_a_non_integer_and_stops_a_live_run_or_answers_3_for_a_dead_one(
        monkeypatch, tmp_path, capsysbinary, stop_run):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes(monkeypatch, {
        ("git", "worktree", "list", "--porcelain"): (0, b"worktree %s\nHEAD abc\n" % os.fsencode(tmp_path)),
    })
    live = {"4242": True}

    def fake_kill(pid, sig):
        if not live.get(str(pid)):
            raise ProcessLookupError(3, "No such process")

    monkeypatch.setattr(os, "kill", fake_kill)

    assert stop_run.main([]) == 2
    assert capsysbinary.readouterr() == (b"", b"stop-run: name an issue, or --all\n" + USAGE)
    assert calls == []

    assert stop_run.main(["ten"]) == 2
    assert capsysbinary.readouterr() == (b"", b"stop-run: <issue> must be a positive integer: 'ten'\n" + USAGE)
    assert calls == []

    run = tmp_path / ".tdd" / "wt" / "5"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "conductor.pid").write_bytes(b"4242\n")
    assert stop_run.main(["5"]) == 0
    assert capsysbinary.readouterr() == (os.fsencode(run) + b"\n", b"")
    assert (run / ".tdd" / "stop").read_bytes() == b"at-ledger\n"

    (run / ".tdd" / "stop").unlink()
    live["4242"] = False
    assert stop_run.main(["5"]) == 3
    assert capsysbinary.readouterr()[0] == b""
    assert not (run / ".tdd" / "stop").exists()


def test_main_accepts_a_mode_stop_modes_lists_and_writes_it_to_the_runs_stop_file(
        monkeypatch, tmp_path, capsysbinary, stop_run):
    import stop_modes
    monkeypatch.setattr(stop_modes, "STOP_MODES", ("at-ledger", "at-leaf", "now", "at-step"))
    monkeypatch.chdir(tmp_path)
    fake_processes(monkeypatch, {
        ("git", "worktree", "list", "--porcelain"): (0, b"worktree %s\nHEAD abc\n" % os.fsencode(tmp_path)),
    })
    monkeypatch.setattr(os, "kill", lambda pid, sig: None)
    run = tmp_path / ".tdd" / "wt" / "5"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "conductor.pid").write_bytes(b"4242\n")

    assert stop_run.main(["--mode", "at-step", "5"]) == 0
    assert (run / ".tdd" / "stop").read_bytes() == b"at-step\n"
