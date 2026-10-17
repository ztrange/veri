"""Small cases for stop-run.sh's command-line interface, driven in-process through run_cli with git and signals faked."""
import importlib
import os
import signal

import pytest

USAGE_LINE = "usage: stop-run.sh [--mode at-ledger|at-leaf|now] <issue> | --all"


@pytest.fixture
def stop_run():
    return importlib.import_module("veri.stop_run")


@pytest.fixture
def world(monkeypatch, fake_processes):
    """Git names the working directory as the main tree; ps answers per pid; os.kill answers per pid and records each TERM."""
    live, args_of, terms = set(), {}, []

    def answer(line, **_):
        if line == "git worktree list --porcelain":
            return 0, b"worktree %s\nHEAD abc\n" % os.fsencode(os.getcwd()), b""
        if line.startswith("ps -p "):
            pid = line.split()[2]
            return (0, args_of[pid], b"") if pid in args_of else (1, b"", b"")
        raise AssertionError("unexpected command: %s" % line)

    def fake_kill(pid, sig):
        if sig == signal.SIGTERM:
            terms.append(pid)
        if pid not in live:
            raise ProcessLookupError(3, "No such process")

    fake_processes(answer)
    monkeypatch.setattr(os, "kill", fake_kill)
    return live, args_of, terms


def new_run(repo, issue, conductor_pid):
    run = repo / ".tdd" / "wt" / issue
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "conductor.pid").write_bytes(b"%d\n" % conductor_pid)
    return run


def test_stop_run_cli_mode_now_writes_now_as_the_only_line_of_the_stop_file_names_the_run_on_stdout_and_exits_0(
        tmp_path, run_cli, stop_run, world):
    live, args_of, terms = world
    repo = tmp_path.resolve() / "repo"
    run = new_run(repo, "5", 4242)
    (run / ".tdd" / "develop-red.pid").write_bytes(b"4343\n")
    live.update({4242, 4343})
    args_of["4343"] = b"/bin/sh supervise.sh develop-red 5\n"

    code, out, err = run_cli(stop_run, ["--mode", "now", "5"], cwd=repo)

    assert (code, out, err) == (0, str(run) + "\n", "")
    assert (run / ".tdd" / "stop").read_bytes() == b"now\n"


def test_stop_run_cli_a_missing_worktree_a_dead_conductor_and_all_with_no_live_run_each_exit_3_and_write_no_stop_file(
        tmp_path, run_cli, stop_run, world):
    live, args_of, terms = world
    repo = tmp_path.resolve() / "repo"
    dead = new_run(repo, "9", 9009)
    quiet = tmp_path.resolve() / "quiet"
    quiet_dead = new_run(quiet, "9", 9009)

    code, out, err = run_cli(stop_run, ["404"], cwd=repo)
    assert (code, out) == (3, "")
    assert not (repo / ".tdd" / "wt" / "404").exists()

    code, out, err = run_cli(stop_run, ["9"], cwd=repo)
    assert (code, out) == (3, "")
    assert not (dead / ".tdd" / "stop").exists()

    code, out, err = run_cli(stop_run, ["--all"], cwd=quiet)
    assert (code, out) == (3, "")
    assert not (quiet_dead / ".tdd" / "stop").exists()


def test_stop_run_cli_mode_at_ledger_and_at_leaf_write_the_mode_and_signal_nothing(
        tmp_path, run_cli, stop_run, world):
    live, args_of, terms = world
    repo = tmp_path.resolve() / "repo"
    run = new_run(repo, "5", 4242)
    (run / ".tdd" / "develop-red.pid").write_bytes(b"4343\n")
    live.update({4242, 4343})
    args_of["4343"] = b"/bin/sh supervise.sh develop-red 5\n"

    for mode in ("at-ledger", "at-leaf"):
        (run / ".tdd" / "stop").unlink(missing_ok=True)
        code, out, err = run_cli(stop_run, ["--mode", mode, "5"], cwd=repo)

        assert (mode, code, out, err) == (mode, 0, str(run) + "\n", "")
        assert (run / ".tdd" / "stop").read_bytes() == mode.encode() + b"\n"
        assert terms == []


def test_stop_run_cli_never_signals_the_pid_in_the_conductor_pid_file(tmp_path, run_cli, stop_run, world):
    live, args_of, terms = world
    repo = tmp_path.resolve() / "repo"
    run = new_run(repo, "11", 1111)
    live.add(1111)
    args_of["1111"] = b"/bin/sh supervise.sh conductor 11\n"

    code, out, err = run_cli(stop_run, ["--mode", "now", "11"], cwd=repo)

    assert (code, out, err) == (0, str(run) + "\n", "")
    assert (run / ".tdd" / "stop").read_bytes() == b"now\n"
    assert terms == []


def test_stop_run_cli_refuses_an_unknown_mode_with_its_message_first_and_no_argument_with_the_usage_line_last_each_exiting_2(
        tmp_path, run_cli, stop_run, world):
    live, args_of, terms = world
    repo = tmp_path.resolve() / "repo"
    run = new_run(repo, "5", 4242)
    live.add(4242)

    code, out, err = run_cli(stop_run, ["--mode", "bogus", "5"], cwd=repo)
    assert (code, out) == (2, "")
    assert err.split("\n")[0] == "stop-run: unknown mode — want at-ledger, at-leaf or now: 'bogus'"
    assert not (run / ".tdd" / "stop").exists()

    code, out, err = run_cli(stop_run, [], cwd=repo)
    assert (code, out) == (2, "")
    assert err.rstrip("\n").split("\n")[-1] == USAGE_LINE
