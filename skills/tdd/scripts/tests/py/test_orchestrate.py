"""In-process cases for veri/orchestrate.py, the module orchestrate.sh is a shim over."""
import importlib
import io
import os
import pathlib
import subprocess
import sys

import pytest

from conftest import SCRIPTS


@pytest.fixture
def orchestrate():
    return importlib.import_module("veri.orchestrate")


def _boundaries(monkeypatch, solvable):
    """Fake solvable-issues.sh answering <solvable> = (exit code, stdout) and the conductor launch;
    return the lists of asks and launches they record."""
    asks, launches = [], []

    def fake_run(args, *rest, **kwargs):
        if pathlib.Path(args[0]).name != "solvable-issues.sh":
            raise AssertionError("unexpected subprocess.run call: %r" % (args,))
        asks.append(list(args))
        stdout = solvable[1]
        if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
            stdout = stdout.encode()
        return subprocess.CompletedProcess(args, solvable[0], stdout, None)

    def fake_popen(args, *rest, **kwargs):
        launches.append(list(args))
        raise AssertionError("no conductor should launch: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    return asks, launches


def test_a_bad_budget_refuses_before_any_ask_and_a_solvable_answer_of_1_or_3_ends_the_run_with_its_exit_code(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)

    monkeypatch.setenv("VERI_CONDUCTOR_CTX_BUDGET", "120k")
    asks, launches = _boundaries(monkeypatch, (0, "7\n"))
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (
        2, "", "orchestrate.sh: VERI_CONDUCTOR_CTX_BUDGET must be a whole number of tokens: 120k\n")
    assert (asks, launches) == ([], [])

    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET")
    asks, launches = _boundaries(monkeypatch, (1, ""))
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (
        2, "", "orchestrate.sh: solvable-issues.sh exited 1; no answer about the solvable set\n")
    assert len(asks) == 1 and launches == []

    asks, launches = _boundaries(monkeypatch, (3, ""))
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (0, "", "")
    assert len(asks) == 1 and launches == []


class _FakeConductor:
    def __init__(self, pid):
        self.pid = pid
        self.stdout = io.BytesIO(b"")
        self.returncode = 0

    def poll(self):
        return 0

    def wait(self, timeout=None):
        return 0


def _passes(monkeypatch, answers, park_on_launch):
    """Fake solvable-issues.sh answering each (exit code, stdout) of <answers> in turn, a conductor
    launch whose stream ends at once after calling park_on_launch(<n>, <issue>), and the stop;
    return the lists of asks and launches they record."""
    asks, launches = [], []
    answers = list(answers)

    def fake_run(args, *rest, **kwargs):
        if pathlib.Path(args[0]).name != "solvable-issues.sh":
            raise AssertionError("unexpected subprocess.run call: %r" % (args,))
        asks.append(list(args))
        if not answers:
            raise AssertionError("solvable-issues.sh asked once too often")
        rc, stdout = answers.pop(0)
        if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
            stdout = stdout.encode()
        return subprocess.CompletedProcess(args, rc, stdout, None)

    def fake_popen(args, *rest, **kwargs):
        launches.append(list(args))
        park_on_launch(len(launches), args[1])
        return _FakeConductor(4000 + len(launches))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(os, "killpg", lambda pid, sig: None)
    monkeypatch.setattr(os, "kill", lambda pid, sig: None)
    return asks, launches


def test_selection_takes_the_first_whole_unparked_line_per_pass_reports_and_skips_parked_issues_and_relaunches_unparked_ones(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    parked = tmp_path / ".tdd" / "parked"
    (parked / "5.md").mkdir(parents=True)
    (tmp_path / "target").write_text("")
    solvable = os.path.join(orchestrate.SCRIPTS, "solvable-issues.sh")
    conductor = os.path.join(orchestrate.SCRIPTS, "run-conductor.sh")

    def park(n, issue):
        if n == 2:
            (parked / ("%s.md" % issue)).write_text("")
        elif n == 3:
            (parked / ("%s.md" % issue)).symlink_to(tmp_path / "target")

    asks, launches = _passes(monkeypatch, [
        (0, "5\n6 x\n9\n\n\n"), (0, "5\n6 x\n9\n\n"), (0, "5\n6 x\n9\n"), (0, "5\n6 x\n9\n")], park)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (0, "parked 6 x\nparked 9\n", "")
    assert asks == [[solvable]] * 4
    assert launches == [[conductor, "6 x"], [conductor, "6 x"], [conductor, "9"]]

    asks, launches = _passes(monkeypatch, [(0, "7\n"), (2, "")], lambda n, issue: None)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (
        2, "", "orchestrate.sh: solvable-issues.sh exited 2; no answer about the solvable set\n")
    assert (len(asks), launches) == (2, [[conductor, "7"]])


def test_1129_an_answer_whose_first_line_is_empty_launches_a_conductor_for_the_first_non_empty_unparked_line(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    conductor = os.path.join(orchestrate.SCRIPTS, "run-conductor.sh")
    asks, launches = _passes(monkeypatch, [(0, "\n7\n8\n"), (3, "")], lambda n, issue: None)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err, len(asks), launches) == (0, "", "", 2, [[conductor, "7"]])


def test_1129_an_empty_line_between_a_parked_issue_and_an_unparked_one_is_skipped_and_the_unparked_one_launched(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    (tmp_path / ".tdd" / "parked").mkdir(parents=True)
    (tmp_path / ".tdd" / "parked" / "5.md").write_text("")
    conductor = os.path.join(orchestrate.SCRIPTS, "run-conductor.sh")
    asks, launches = _passes(monkeypatch, [(0, "5\n\n7\n"), (3, "")], lambda n, issue: None)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err, len(asks), launches) == (0, "", "", 2, [[conductor, "7"]])


def test_1129_an_answer_whose_every_line_is_empty_or_parked_ends_the_run_with_exit_0_and_no_launch(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    (tmp_path / ".tdd" / "parked").mkdir(parents=True)
    (tmp_path / ".tdd" / "parked" / "5.md").write_text("")
    (tmp_path / ".tdd" / "parked" / "6.md").write_text("")
    asks, launches = _passes(monkeypatch, [(0, "\n5\n\n6\n\n")], lambda n, issue: None)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err, len(asks), launches) == (0, "", "", 1, [])


def test_a_conductor_launches_as_a_new_session_leader_with_signals_as_todays_launch_hands_them_and_nothing_else_starts(
        capsys, monkeypatch, tmp_path, orchestrate):
    import signal
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    watched = (signal.SIGINT, signal.SIGQUIT, signal.SIGPIPE, signal.SIGXFSZ)
    saved = {sig: signal.signal(sig, signal.SIG_DFL) for sig in watched}
    asks, _ = _passes(monkeypatch, [(0, "7\n"), (3, "")], lambda n, issue: None)
    calls = []

    def spy_popen(args, *rest, **kwargs):
        calls.append((list(args), rest, dict(kwargs), {sig: signal.getsignal(sig) for sig in watched}))
        return _FakeConductor(4001)

    monkeypatch.setattr(subprocess, "Popen", spy_popen)
    try:
        code = orchestrate.main([])
        after = {sig: signal.getsignal(sig) for sig in watched}
    finally:
        for sig, handler in saved.items():
            signal.signal(sig, handler)
    out, err = capsys.readouterr()
    assert (code, out, err) == (0, "", "")
    conductor = os.path.join(orchestrate.SCRIPTS, "run-conductor.sh")
    [(argv, rest, kwargs, dispositions)] = calls
    unchanged = {key: kwargs.pop(key, None) for key in ("stderr", "cwd", "env")}
    assert (argv, rest, kwargs, unchanged) == (
        [conductor, "7"], (),
        {"start_new_session": True, "stdin": subprocess.DEVNULL, "stdout": subprocess.PIPE,
         "restore_signals": False},
        {"stderr": None, "cwd": None, "env": None})
    assert dispositions == {signal.SIGINT: signal.SIG_IGN, signal.SIGQUIT: signal.SIG_IGN,
                            signal.SIGPIPE: signal.SIG_DFL, signal.SIGXFSZ: signal.SIG_DFL}
    assert after == {sig: signal.SIG_DFL for sig in watched}
    assert asks == [[os.path.join(orchestrate.SCRIPTS, "solvable-issues.sh")]] * 2


def test_a_conductor_that_cannot_start_prints_one_line_sends_no_stop_and_exits_2(
        capsys, monkeypatch, tmp_path, orchestrate):
    import errno
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    _passes(monkeypatch, [(0, "7\n"), (0, "7\n"), (3, "")], lambda n, issue: None)
    launches, stops = [], []

    def failing_popen(args, *rest, **kwargs):
        launches.append(list(args))
        raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), args[0])

    monkeypatch.setattr(subprocess, "Popen", failing_popen)
    monkeypatch.setattr(os, "killpg", lambda pid, sig: stops.append(("killpg", pid, sig)))
    monkeypatch.setattr(os, "kill", lambda pid, sig: stops.append(("kill", pid, sig)))
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    conductor = os.path.join(orchestrate.SCRIPTS, "run-conductor.sh")
    assert (code, out, err) == (2, "", "orchestrate.sh: cannot start %s: %s\n" % (conductor, os.strerror(errno.ENOENT)))
    assert stops == []
    assert launches == [[conductor, "7"]]


def test_every_conductor_is_stopped_by_sigterm_to_its_group_else_its_pid_silently_and_never_waited_for(
        capsys, monkeypatch, tmp_path, orchestrate):
    import signal
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    asks, _ = _passes(monkeypatch, [(0, "7\n")] * 4 + [(3, "")], lambda n, issue: None)
    stops = []
    pids = iter(range(4001, 4005))

    class Running(_FakeConductor):
        def poll(self):
            return None

        def wait(self, timeout=None):
            raise AssertionError("waited for conductor %d" % self.pid)

    killpg_raises = {4002: ProcessLookupError, 4003: ProcessLookupError, 4004: PermissionError}
    kill_raises = {4002: ProcessLookupError, 4003: PermissionError, 4004: PermissionError}

    def fake_killpg(pid, sig):
        stops.append(("killpg", pid, sig))
        if pid in killpg_raises:
            raise killpg_raises[pid]()

    def fake_kill(pid, sig):
        stops.append(("kill", pid, sig))
        if pid in kill_raises:
            raise kill_raises[pid]()

    monkeypatch.setattr(subprocess, "Popen", lambda args, *rest, **kwargs: Running(next(pids)))
    monkeypatch.setattr(os, "killpg", fake_killpg)
    monkeypatch.setattr(os, "kill", fake_kill)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (0, "", "")
    term = signal.SIGTERM
    assert stops[:6] == [("killpg", 4001, term), ("killpg", 4002, term), ("kill", 4002, term),
                         ("killpg", 4003, term), ("kill", 4003, term), ("killpg", 4004, term)]
    assert stops[6:] in ([], [("kill", 4004, term)])
    assert len(asks) == 5


class _Stream:
    """A conductor's stdout over <lines>, snapshotting <out>'s flushed text at each line asked for."""

    def __init__(self, lines, out, snapshots):
        self.lines, self.out, self.snapshots = list(lines), out, snapshots

    def __iter__(self):
        return self

    def __next__(self):
        line = self.readline()
        if not line:
            raise StopIteration
        return line

    def readline(self, *args):
        self.snapshots.append(self.out.flushed)
        return self.lines.pop(0) if self.lines else b""

    def close(self):
        pass


class _Out:
    def __init__(self):
        self.pending, self.flushed = "", ""

    def write(self, text):
        self.pending += text
        return len(text)

    def flush(self):
        self.flushed, self.pending = self.flushed + self.pending, ""


def test_the_watch_prints_each_assistant_lines_cache_read_plus_creation_and_stops_on_a_user_line_over_budget_after_step_done(
        capsys, monkeypatch, tmp_path, orchestrate):
    import signal
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_CONDUCTOR_CTX_BUDGET", "100")
    asks, _ = _passes(monkeypatch, [(0, "7\n"), (0, "8\n"), (3, "")], lambda n, issue: None)
    out, snapshots, stops = _Out(), [], []

    def usage(read, creation):
        return '"cache_read_input_tokens":%d,"cache_creation_input_tokens":%d' % (read, creation)

    streams = [[
        b'{"type":"assistant","message":{"usage":{%s}}}\n' % usage(10, 5).encode(),
        b'{"type":"assistant","message":{"usage":{"cache_read_input_tokens":999}}}\n',
        b'{"type":"result","usage":{%s}}\n' % usage(999, 1).encode(),
        b'{"type":"user","usage":{%s}}\n' % usage(1, 1).encode(),
        b'{"type":"assistant","usage":{"cache_creation_input_tokens":60,"cache_read_input_tokens":40},'
        b'"x":{%s}}\n' % usage(1000, 2000).encode(),
        b'{"type":"assistant","input":"bash event.sh step-done 3","usage":{%s}}\n' % usage(30, 70).encode(),
        b'{"type":"user","x":{"type":"assistant","usage":{%s}}}\n' % usage(50, 60).encode(),
        b'{"type":"user","content":"ok"}\n',
        b'{"type":"assistant","usage":{%s}}\n' % usage(60, 50).encode(),
        b'{"type":"assistant","input":"bash event.sh step-done 4"}\n',
        b'{"type":"user","content":"done"}\n',
        b'{"type":"assistant","usage":{%s}}\n' % usage(1, 1).encode(),
    ], [
        b'{"type":"assistant","usage":{%s}}\n' % usage(3, 4).encode(),
        b'{"type":"assistant","usage":{%s}}' % usage(8, 9).encode(),
    ]]
    pids = iter((4001, 4002))

    def fake_popen(args, *rest, **kwargs):
        conductor = _FakeConductor(next(pids))
        conductor.stdout = _Stream(streams.pop(0), out, snapshots)
        return conductor

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(os, "killpg", lambda pid, sig: stops.append((pid, sig)))
    monkeypatch.setattr(sys, "stdout", out)
    code = orchestrate.main([])
    _, err = capsys.readouterr()
    assert (code, out.flushed + out.pending, err) == (
        0, "context 7 15\ncontext 7 100\ncontext 7 100\ncontext 7 110\ncontext 7 110\ncontext 8 7\n", "")
    assert out.pending == ""
    assert snapshots[1] == "context 7 15\n"
    assert stops == [(4001, signal.SIGTERM), (4002, signal.SIGTERM)]
    assert len(asks) == 3


def test_the_budget_reads_as_bash_does_unset_or_empty_120000(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)

    def step_done(read):
        return (b'{"type":"assistant","input":"bash event.sh step-done 1",'
                b'"usage":{"cache_read_input_tokens":%d,"cache_creation_input_tokens":0}}\n' % read)

    stream = b"".join(step_done(n) + b'{"type":"user","content":"ok"}\n' for n in (32768, 50000, 120000, 120001))
    stream += b'{"type":"assistant","usage":{"cache_read_input_tokens":1,"cache_creation_input_tokens":1}}\n'

    def run(budget):
        if budget is None:
            monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
        else:
            monkeypatch.setenv("VERI_CONDUCTOR_CTX_BUDGET", budget)
        _passes(monkeypatch, [(0, "7\n"), (3, "")], lambda n, issue: None)

        def fake_popen(args, *rest, **kwargs):
            conductor = _FakeConductor(4001)
            conductor.stdout = io.BytesIO(stream)
            return conductor

        monkeypatch.setattr(subprocess, "Popen", fake_popen)
        code = orchestrate.main([])
        out, err = capsys.readouterr()
        return code, out, err

    assert run(None) == (0, "context 7 32768\ncontext 7 50000\ncontext 7 120000\ncontext 7 120001\n", "")
    assert run("") == (0, "context 7 32768\ncontext 7 50000\ncontext 7 120000\ncontext 7 120001\n", "")


def test_1250_an_unset_or_empty_stop_timeout_bounds_the_drain_at_10_seconds_and_a_positive_one_as_given(
        capsys, monkeypatch, tmp_path, orchestrate):
    import signal
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)

    def run(timeout):
        if timeout is None:
            monkeypatch.delenv("VERI_CONDUCTOR_STOP_TIMEOUT", raising=False)
        else:
            monkeypatch.setenv("VERI_CONDUCTOR_STOP_TIMEOUT", timeout)
        _passes(monkeypatch, [(0, "7\n"), (3, "")], lambda n, issue: None)
        timers = []
        monkeypatch.setattr(signal, "setitimer", lambda which, seconds: timers.append((which, seconds)))
        code = orchestrate.main([])
        out, err = capsys.readouterr()
        assert (code, out, err) == (0, "", "")
        return timers

    assert run(None) == [(signal.ITIMER_REAL, 10.0), (signal.ITIMER_REAL, 0)]
    assert run("") == [(signal.ITIMER_REAL, 10.0), (signal.ITIMER_REAL, 0)]
    assert run("0.5") == [(signal.ITIMER_REAL, 0.5), (signal.ITIMER_REAL, 0)]


def test_a_leading_zero_budget_reads_as_decimal_so_0100000_stops_a_conductor_over_100000_not_over_32768_1127(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_CONDUCTOR_CTX_BUDGET", "0100000")
    _passes(monkeypatch, [(0, "7\n"), (3, "")], lambda n, issue: None)
    stream = b"".join(
        b'{"type":"assistant","input":"bash event.sh step-done 1",'
        b'"usage":{"cache_read_input_tokens":%d,"cache_creation_input_tokens":0}}\n'
        b'{"type":"user","content":"ok"}\n' % read for read in (50000, 100001, 120000))

    def fake_popen(args, *rest, **kwargs):
        conductor = _FakeConductor(4001)
        conductor.stdout = io.BytesIO(stream)
        return conductor

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (0, "context 7 50000\ncontext 7 100001\n", "")


def test_a_08_budget_stops_a_conductor_over_8_tokens_with_no_value_too_great_for_base_line_1127(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_CONDUCTOR_CTX_BUDGET", "08")
    _passes(monkeypatch, [(0, "7\n"), (3, "")], lambda n, issue: None)
    stream = b"".join(
        b'{"type":"assistant","input":"bash event.sh step-done 1",'
        b'"usage":{"cache_read_input_tokens":%d,"cache_creation_input_tokens":0}}\n'
        b'{"type":"user","content":"ok"}\n' % read for read in (8, 9, 20))

    def fake_popen(args, *rest, **kwargs):
        conductor = _FakeConductor(4001)
        conductor.stdout = io.BytesIO(stream)
        return conductor

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (0, "context 7 8\ncontext 7 9\n", "")


def test_stdout_carries_only_context_and_parked_lines_and_a_closed_stdout_raises_broken_pipe_out_of_the_next_context_write(
        capsys, monkeypatch, tmp_path, orchestrate):
    import re
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_CONDUCTOR_CTX_BUDGET", "100")
    parked = tmp_path / ".tdd" / "parked"
    parked.mkdir(parents=True)

    def park(n, issue):
        if n == 1:
            (parked / ("%s.md" % issue)).write_text("")

    _passes(monkeypatch, [(0, "7\n"), (0, "7\n8\n"), (3, "")], lambda n, issue: None)
    usage = b'"cache_read_input_tokens":%d,"cache_creation_input_tokens":%d'
    streams = [
        b'{"type":"assistant","usage":{%s}}\n' % (usage % (60, 10))
        + b'{"type":"assistant","input":"bash event.sh step-done 1","usage":{%s}}\n' % (usage % (90, 20))
        + b'{"type":"user","content":"ok"}\n'
        + b'{"type":"assistant","usage":{%s}}\n' % (usage % (1, 1)),
        b'{"type":"result","usage":{%s}}\n' % (usage % (5, 5))
        + b'{"type":"assistant","usage":{%s}}\n' % (usage % (3, 4)),
    ]
    stops = []
    pids = iter((4001, 4002))

    def fake_popen(args, *rest, **kwargs):
        conductor = _FakeConductor(next(pids))
        park(conductor.pid - 4000, args[1])
        conductor.stdout = io.BytesIO(streams.pop(0))
        return conductor

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(os, "killpg", lambda pid, sig: stops.append(pid))
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (0, "context 7 70\ncontext 7 110\nparked 7\ncontext 8 7\n", "")
    assert all(re.fullmatch(r"(context [0-9]+ [0-9]+|parked [0-9]+)", line) for line in out.splitlines())
    assert stops == [4001, 4002]

    _passes(monkeypatch, [(0, "9\n"), (3, "")], lambda n, issue: None)
    first = b'{"type":"assistant","usage":{%s}}\n' % (usage % (1, 2))
    stream = io.BytesIO(first + b'{"type":"assistant","usage":{%s}}\n' % (usage % (3, 4)))

    def closed_popen(args, *rest, **kwargs):
        conductor = _FakeConductor(4003)
        conductor.stdout = stream
        return conductor

    monkeypatch.setattr(subprocess, "Popen", closed_popen)
    read_end, write_end = os.pipe()
    os.close(read_end)
    closed = os.fdopen(write_end, "w")
    monkeypatch.setattr(sys, "stdout", closed)
    try:
        with pytest.raises(BrokenPipeError):
            orchestrate.main([])
        assert stream.tell() == len(first)
    finally:
        monkeypatch.setattr(sys, "stdout", sys.__stdout__)
        try:
            closed.close()
        except BrokenPipeError:
            pass


def test_1128_a_missing_run_conductor_ends_the_run_with_exit_2_one_stderr_line_naming_it_and_the_reason_and_no_further_launch(
        capsys, monkeypatch, tmp_path, orchestrate):
    import errno
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    _passes(monkeypatch, [(0, "7\n"), (0, "7\n"), (3, "")], lambda n, issue: None)
    launches = []

    def missing_popen(args, *rest, **kwargs):
        launches.append(list(args))
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args[0])

    monkeypatch.setattr(subprocess, "Popen", missing_popen)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    conductor = os.path.join(orchestrate.SCRIPTS, "run-conductor.sh")
    lines = err.splitlines()
    assert (code, out, len(lines), launches) == (2, "", 1, [[conductor, "7"]])
    assert "run-conductor.sh" in lines[0] and os.strerror(errno.ENOENT) in lines[0]


def test_1128_a_run_conductor_that_is_not_executable_ends_the_run_with_exit_2_one_stderr_line_naming_it_and_the_reason_and_no_further_launch(
        capsys, monkeypatch, tmp_path, orchestrate):
    import errno
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    _passes(monkeypatch, [(0, "7\n"), (0, "7\n"), (3, "")], lambda n, issue: None)
    launches = []

    def unexecutable_popen(args, *rest, **kwargs):
        launches.append(list(args))
        raise PermissionError(errno.EACCES, os.strerror(errno.EACCES), args[0])

    monkeypatch.setattr(subprocess, "Popen", unexecutable_popen)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    conductor = os.path.join(orchestrate.SCRIPTS, "run-conductor.sh")
    lines = err.splitlines()
    assert (code, out, len(lines), launches) == (2, "", 1, [[conductor, "7"]])
    assert "run-conductor.sh" in lines[0] and os.strerror(errno.EACCES) in lines[0]


def test_1128_after_a_failed_conductor_launch_solvable_issues_is_asked_no_further_time(
        capsys, monkeypatch, tmp_path, orchestrate):
    import errno
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    asks, _ = _passes(monkeypatch, [(0, "7\n"), (0, "7\n"), (3, "")], lambda n, issue: None)

    def missing_popen(args, *rest, **kwargs):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args[0])

    monkeypatch.setattr(subprocess, "Popen", missing_popen)
    orchestrate.main([])
    capsys.readouterr()
    assert asks == [[os.path.join(orchestrate.SCRIPTS, "solvable-issues.sh")]]


def test_1128_a_conductor_that_starts_and_exits_with_its_issue_still_listed_and_unparked_is_relaunched_after_a_new_ask(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    asks, launches = _passes(monkeypatch, [(0, "7\n"), (0, "7\n"), (3, "")], lambda n, issue: None)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    solvable = os.path.join(orchestrate.SCRIPTS, "solvable-issues.sh")
    conductor = os.path.join(orchestrate.SCRIPTS, "run-conductor.sh")
    assert (code, out, err, asks, launches) == (
        0, "", "", [[solvable]] * 3, [[conductor, "7"], [conductor, "7"]])
