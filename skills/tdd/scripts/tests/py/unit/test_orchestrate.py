"""In-process cases for veri/orchestrate.py, the module orchestrate.sh is a shim over."""
import importlib
import io
import os
import pathlib
import subprocess
import sys

import pytest

from conftest import SCRIPTS, listed, listed_in_turn


@pytest.fixture
def orchestrate():
    return importlib.import_module("veri.orchestrate")


def _served(monkeypatch, orchestrate, answers, touch=None):
    """Serve each (exit code, stdout) of <answers> in turn, the last repeating, as the solvable listing;
    <touch> maps the request number to paths touched as it is answered."""
    module = sys.modules[orchestrate.solvable_in_scope.__module__]
    requests = []

    def solvable(label, priority):
        requests.append(None)
        for path in (touch or {}).get(len(requests), ()):
            pathlib.Path(path).touch()
        code, stdout = answers[min(len(requests), len(answers)) - 1]
        return (code, listed(code, stdout) if code in (0, 3) else [])

    monkeypatch.setattr(module, "solvable", solvable)


def _boundaries(monkeypatch, orchestrate, solvable):
    """Serve <solvable> = (exit code, stdout) as the listing, fake the conductor launch and return its launches."""
    launches = []

    def fake_popen(args, *rest, **kwargs):
        launches.append(list(args))
        raise AssertionError("no conductor should launch: %r" % (args,))

    _served(monkeypatch, orchestrate, [solvable])
    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    return launches


def test_a_bad_budget_refuses_before_any_launch_and_a_listing_with_no_labelled_open_issue_or_an_unreadable_one_ends_the_run(
        capfd, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)

    monkeypatch.setenv("VERI_CONDUCTOR_CTX_BUDGET", "120k")
    launches = _boundaries(monkeypatch, orchestrate, (0, "7\n"))
    code = orchestrate.main([])
    out, err = capfd.readouterr()
    assert (code, out, err) == (
        2, "", "orchestrate.sh: VERI_CONDUCTOR_CTX_BUDGET must be a whole number of tokens: 120k\n")
    assert launches == []

    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET")
    launches = _boundaries(monkeypatch, orchestrate, (2, ""))
    code = orchestrate.main([])
    out, err = capfd.readouterr()
    assert (code, out) == (2, "")
    assert err.endswith("orchestrate.sh: solvable-issues.sh exited 2; no answer about the solvable set\n")
    assert launches == []

    launches = _boundaries(monkeypatch, orchestrate, (3, ""))
    code = orchestrate.main([])
    out, err = capfd.readouterr()
    assert (code, out, err) == (0, "", "")
    assert launches == []


class _FakeConductor:
    def __init__(self, pid):
        self.pid = pid
        self.stdout = io.BytesIO(b"")
        self.returncode = 0

    def poll(self):
        return 0

    def wait(self, timeout=None):
        return 0


def _passes(monkeypatch, orchestrate, answers, park_on_launch, listing=None):
    """Serve each (exit code, stdout) of <answers> in turn as the listing, fake a conductor launch
    whose stream ends at once after calling park_on_launch(<n>, <issue>), and the stop;
    return the list of launches."""
    launches = []
    if listing:
        _served(monkeypatch, orchestrate, answers)
    else:
        _served(monkeypatch, orchestrate, answers)

    def fake_popen(args, *rest, **kwargs):
        launches.append(list(args))
        park_on_launch(len(launches), args[1])
        return _FakeConductor(4000 + len(launches))

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(os, "killpg", lambda pid, sig: None)
    monkeypatch.setattr(os, "kill", lambda pid, sig: None)
    return launches


@pytest.mark.process("gh and git started for real behind a listing, solvable-issues.sh refused")
def test_1354_a_refused_start_of_solvable_issues_sh_changes_no_answer_the_run_launches_and_ends_as_ever(
        capfd, monkeypatch, tmp_path, orchestrate, listing):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    conductor = os.path.join(orchestrate.SCRIPTS, "run-conductor.sh")
    launches = _passes(monkeypatch, orchestrate, [(0, "7\n"), (3, "")], lambda n, issue: None, listing=listing)
    start = subprocess.run

    def refusing(args, *rest, **kwargs):
        if os.path.basename(args[0]) == "solvable-issues.sh":
            raise OSError("starting a process is refused")
        return start(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", refusing)
    code = orchestrate.main([])
    out, err = capfd.readouterr()
    assert (code, out, err, launches) == (0, "", "", [[conductor, "7"]])


@pytest.mark.parametrize("name", ["VERI_LABEL", "VERI_PRIORITY_LABEL"])
def test_1515_an_empty_label_is_a_selection_that_could_not_answer_and_ends_the_run_with_exit_2_before_any_launch(
        name, capfd, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    monkeypatch.setenv(name, "")
    launches = _boundaries(monkeypatch, orchestrate, (0, "7\n"))
    code = orchestrate.main([])
    out, err = capfd.readouterr()
    assert (code, out, err, launches) == (
        2, "",
        "solvable-issues: %s is set but empty: name a label or leave it unset\n"
        "orchestrate.sh: solvable-issues.sh exited 2; no answer about the solvable set\n" % name, [])


def test_selection_takes_the_first_whole_unparked_line_per_pass_reports_and_skips_parked_issues_and_relaunches_unparked_ones(
        capfd, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    parked = tmp_path / ".tdd" / "parked"
    (parked / "5.md").mkdir(parents=True)
    (tmp_path / "target").write_text("")
    conductor = os.path.join(orchestrate.SCRIPTS, "run-conductor.sh")

    def park(n, issue):
        if n == 2:
            (parked / ("%s.md" % issue)).write_text("")
        elif n == 3:
            (parked / ("%s.md" % issue)).symlink_to(tmp_path / "target")

    launches = _passes(monkeypatch, orchestrate, [
        (0, "5\n6 x\n9\n\n\n"), (0, "5\n6 x\n9\n\n"), (0, "5\n6 x\n9\n"), (0, "5\n6 x\n9\n")], park)
    code = orchestrate.main([])
    out, err = capfd.readouterr()
    assert (code, out, err) == (0, "parked 6 x\nparked 9\n", "")
    assert launches == [[conductor, "6 x"], [conductor, "6 x"], [conductor, "9"]]

    launches = _passes(monkeypatch, orchestrate, [(0, "7\n"), (2, "")], lambda n, issue: None)
    code = orchestrate.main([])
    out, err = capfd.readouterr()
    assert (code, out) == (2, "")
    assert err.endswith("orchestrate.sh: solvable-issues.sh exited 2; no answer about the solvable set\n")
    assert launches == [[conductor, "7"]]


def test_1129_an_answer_whose_first_line_is_empty_launches_a_conductor_for_the_first_non_empty_unparked_line(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    conductor = os.path.join(orchestrate.SCRIPTS, "run-conductor.sh")
    launches = _passes(monkeypatch, orchestrate, [(0, "\n7\n8\n"), (3, "")], lambda n, issue: None)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err, launches) == (0, "", "", [[conductor, "7"]])


def test_1129_an_empty_line_between_a_parked_issue_and_an_unparked_one_is_skipped_and_the_unparked_one_launched(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    (tmp_path / ".tdd" / "parked").mkdir(parents=True)
    (tmp_path / ".tdd" / "parked" / "5.md").write_text("")
    conductor = os.path.join(orchestrate.SCRIPTS, "run-conductor.sh")
    launches = _passes(monkeypatch, orchestrate, [(0, "5\n\n7\n"), (3, "")], lambda n, issue: None)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err, launches) == (0, "", "", [[conductor, "7"]])


def test_1129_an_answer_whose_every_line_is_empty_or_parked_ends_the_run_with_exit_0_and_no_launch(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    (tmp_path / ".tdd" / "parked").mkdir(parents=True)
    (tmp_path / ".tdd" / "parked" / "5.md").write_text("")
    (tmp_path / ".tdd" / "parked" / "6.md").write_text("")
    launches = _passes(monkeypatch, orchestrate, [(0, "\n5\n\n6\n\n")], lambda n, issue: None)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err, launches) == (0, "", "", [])


def test_a_conductor_launches_as_a_new_session_leader_with_signals_as_todays_launch_hands_them_and_nothing_else_starts(
        capsys, monkeypatch, tmp_path, orchestrate):
    import signal
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    watched = (signal.SIGINT, signal.SIGQUIT, signal.SIGPIPE, signal.SIGXFSZ)
    saved = {sig: signal.signal(sig, signal.SIG_DFL) for sig in watched}
    _passes(monkeypatch, orchestrate, [(0, "7\n"), (3, "")], lambda n, issue: None)
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


def test_a_conductor_that_cannot_start_prints_one_line_sends_no_stop_and_exits_2(
        capsys, monkeypatch, tmp_path, orchestrate):
    import errno
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    _passes(monkeypatch, orchestrate, [(0, "7\n"), (0, "7\n"), (3, "")], lambda n, issue: None)
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
    _passes(monkeypatch, orchestrate, [(0, "7\n")] * 4 + [(3, "")], lambda n, issue: None)
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
    _passes(monkeypatch, orchestrate, [(0, "7\n"), (0, "8\n"), (3, "")], lambda n, issue: None)
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
        _passes(monkeypatch, orchestrate, [(0, "7\n"), (3, "")], lambda n, issue: None)

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
        _passes(monkeypatch, orchestrate, [(0, "7\n"), (3, "")], lambda n, issue: None)
        timers = []
        monkeypatch.setattr(signal, "setitimer", lambda which, seconds: timers.append((which, seconds)))
        code = orchestrate.main([])
        out, err = capsys.readouterr()
        assert (code, out, err) == (0, "", "")
        return timers

    assert run(None) == [(signal.ITIMER_REAL, 10.0), (signal.ITIMER_REAL, 0)]
    assert run("") == [(signal.ITIMER_REAL, 10.0), (signal.ITIMER_REAL, 0)]
    assert run("0.5") == [(signal.ITIMER_REAL, 0.5), (signal.ITIMER_REAL, 0)]


def test_1313_a_stop_timeout_too_great_for_setitimer_refuses_with_exit_2_one_line_naming_it_and_its_value_before_any_ask(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    monkeypatch.setenv("VERI_CONDUCTOR_STOP_TIMEOUT", "1e12")
    launches = _boundaries(monkeypatch, orchestrate, (3, ""))
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, len(err.splitlines()), "VERI_CONDUCTOR_STOP_TIMEOUT" in err, "1e12" in err,
            "Traceback" in err, launches) == (2, "", 1, True, True, False, [])


def test_1313_a_stop_timeout_above_the_macos_setitimer_ceiling_of_100000000_refuses_before_any_ask_and_the_header_states_it(
        capsys, monkeypatch, tmp_path, orchestrate):
    import signal
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    monkeypatch.setenv("VERI_CONDUCTOR_STOP_TIMEOUT", "100000001")
    launches = _boundaries(monkeypatch, orchestrate, (3, ""))
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, len(err.splitlines()), "VERI_CONDUCTOR_STOP_TIMEOUT" in err, "100000001" in err,
            "Traceback" in err, launches) == (2, "", 1, True, True, False, [])

    monkeypatch.setenv("VERI_CONDUCTOR_STOP_TIMEOUT", "100000000")
    _passes(monkeypatch, orchestrate, [(0, "7\n"), (3, "")], lambda n, issue: None)
    timers = []
    monkeypatch.setattr(signal, "setitimer", lambda which, seconds: timers.append((which, seconds)))
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err, timers[0]) == (0, "", "", (signal.ITIMER_REAL, 100000000.0))

    header = "\n".join((pathlib.Path(__file__).resolve().parents[3] / "orchestrate.sh").read_text().splitlines()[:20])
    assert "100000000" in header


def test_1313_a_budget_that_is_not_a_whole_number_refuses_with_exit_2_one_line_naming_it_and_its_value_before_any_ask(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_STOP_TIMEOUT", raising=False)
    for value in ("-1", "1.5", "1_0", " 7", "1e5"):
        monkeypatch.setenv("VERI_CONDUCTOR_CTX_BUDGET", value)
        launches = _boundaries(monkeypatch, orchestrate, (3, ""))
        code = orchestrate.main([])
        out, err = capsys.readouterr()
        assert (value, code, out, err.splitlines(), launches) == (
            value, 2, "",
            ["orchestrate.sh: VERI_CONDUCTOR_CTX_BUDGET must be a whole number of tokens: " + value], [])


def test_a_leading_zero_budget_reads_as_decimal_so_0100000_stops_a_conductor_over_100000_not_over_32768_1127(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_CONDUCTOR_CTX_BUDGET", "0100000")
    _passes(monkeypatch, orchestrate, [(0, "7\n"), (3, "")], lambda n, issue: None)
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
    _passes(monkeypatch, orchestrate, [(0, "7\n"), (3, "")], lambda n, issue: None)
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

    _passes(monkeypatch, orchestrate, [(0, "7\n"), (0, "7\n8\n"), (3, "")], lambda n, issue: None)
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

    _passes(monkeypatch, orchestrate, [(0, "9\n"), (3, "")], lambda n, issue: None)
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
    _passes(monkeypatch, orchestrate, [(0, "7\n"), (0, "7\n"), (3, "")], lambda n, issue: None)
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
    _passes(monkeypatch, orchestrate, [(0, "7\n"), (0, "7\n"), (3, "")], lambda n, issue: None)
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


def test_1128_after_a_failed_conductor_launch_an_unreadable_listing_is_never_met_and_the_run_ends_with_the_launch_line_alone(
        capfd, monkeypatch, tmp_path, orchestrate):
    import errno
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    _passes(monkeypatch, orchestrate, [(0, "7\n"), (2, "")], lambda n, issue: None)

    def missing_popen(args, *rest, **kwargs):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args[0])

    monkeypatch.setattr(subprocess, "Popen", missing_popen)
    code = orchestrate.main([])
    out, err = capfd.readouterr()
    assert (code, out, err.count("\n"), "JSONDecodeError" in err) == (2, "", 1, False)


def test_1128_a_conductor_that_starts_and_exits_with_its_issue_still_listed_and_unparked_is_relaunched_while_the_listing_still_names_it(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    launches = _passes(monkeypatch, orchestrate, [(0, "7\n"), (0, "7\n"), (3, "")], lambda n, issue: None)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    conductor = os.path.join(orchestrate.SCRIPTS, "run-conductor.sh")
    assert (code, out, err, launches) == (0, "", "", [[conductor, "7"], [conductor, "7"]])


def _orchestrated(work, monkeypatch, orchestrate, run_cli, answers, conductor, env,
                  killpg=lambda pid, sig: None):
    launches = []
    _served(monkeypatch, orchestrate, answers)

    def popen(args, *rest, **kwargs):
        launches.append([os.path.basename(args[0])] + list(args[1:]))
        return conductor(4000 + len(launches), args[1])

    monkeypatch.setattr(subprocess, "Popen", popen)
    monkeypatch.setattr(os, "killpg", killpg)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    monkeypatch.delenv("VERI_CONDUCTOR_STOP_TIMEOUT", raising=False)
    code, out, err = run_cli(orchestrate, [], env=env, cwd=work)
    return code, out, err, launches


_HEARTBEAT = '{"type":"system","subtype":"heartbeat"}'
_USER = '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'


def _assistant(read, creation, command=None):
    content = ('"content":[{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"%s"}}],' % command
               if command else "")
    return ('{"type":"assistant","message":{"role":"assistant",%s"usage":{"input_tokens":5,'
            '"cache_creation_input_tokens":%d,"cache_read_input_tokens":%d,"output_tokens":30}}}'
            % (content, creation, read))


def _step_done(issue, read, creation):
    return _assistant(read, creation, "VERI_ISSUE=%s VERI_ACTOR=conductor $S/event.sh step-done" % issue)


def test_main_launches_per_solvable_issue_reports_context_and_stops_over_budget_only_after_the_next_step_done_result_then_relaunches(
        tmp_path, monkeypatch, orchestrate, run_cli):
    def orchestrated(name, answers, streams, budget=None):
        work = tmp_path / name
        work.mkdir()
        streams = [list(s) for s in streams]
        stops, conductors = [], {}

        class Conductor:
            def __init__(self, pid, lines):
                self.pid, self.lines, self.read = pid, [(l + "\n").encode() for l in lines], 0
                self.stdout = self
                self.returncode = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self.read == len(self.lines):
                    raise StopIteration
                self.read += 1
                return self.lines[self.read - 1]

            def close(self):
                pass

            def poll(self):
                return 0

            def wait(self, timeout=None):
                return 0

        def launch(pid, issue):
            conductors[pid] = Conductor(pid, streams.pop(0))
            return conductors[pid]

        def killpg(pid, sig):
            stops.append((conductors[pid].read, len(conductors[pid].lines)))

        env = {} if budget is None else {"VERI_CONDUCTOR_CTX_BUDGET": budget}
        return _orchestrated(work, monkeypatch, orchestrate, run_cli, answers, launch, env,
                             killpg) + (stops,)

    observed = {
        "launches per solvable issue": orchestrated(
            "basic", [(0, "101\n102\n"), (0, "102\n"), (3, "")], [[], []]),
        "solvable-issues.sh exits 2": orchestrated("broken", [(2, "")], []),
        "context per assistant event, none from the result": orchestrated("streaming", [(0, "301\n"), (3, "")], [[
            '{"type":"system","subtype":"init","session_id":"s1"}',
            _assistant(50000, 3438),
            _USER,
            _assistant(60000, 2000),
            '{"type":"result","subtype":"success","is_error":false,"usage":{"input_tokens":10,'
            '"cache_creation_input_tokens":5438,"cache_read_input_tokens":110000,"output_tokens":165}}',
        ]]),
        "over budget mid-step": orchestrated("budget", [(0, "401\n"), (3, "")], [[
            _assistant(150000, 0), _step_done(401, 150000, 100), _USER, _HEARTBEAT, _HEARTBEAT,
        ]], "100000"),
        "step-done under the default, later crossing": orchestrated("underbudget", [(0, "501\n"), (3, "")], [[
            _step_done(501, 110000, 0), _USER, _assistant(150000, 0, "true"), _USER, _HEARTBEAT,
        ]]),
        "over budget at the step-done call": orchestrated("atresult", [(0, "601\n"), (3, "")], [[
            _step_done(601, 150000, 100), _HEARTBEAT, _USER, _HEARTBEAT,
        ]], "100000"),
        "never crosses": orchestrated("never", [(0, "701\n"), (3, "")], [[
            _step_done(701, 60000, 0), _USER, _step_done(701, 99000, 100), _USER, _HEARTBEAT,
        ]], "100000"),
        "unset budget crossing 120000": orchestrated("defaultbudget", [(0, "901\n"), (3, "")], [[
            _assistant(120000, 1), _step_done(901, 120000, 1), _USER, _HEARTBEAT,
        ]]),
        "relaunched after a stop": orchestrated("relaunch", [(0, "1001\n"), (0, "1001\n"), (3, "")], [[
            _step_done(1001, 150000, 100), _USER, _HEARTBEAT,
        ], []], "100000"),
    }

    broken = observed["solvable-issues.sh exits 2"]
    observed["solvable-issues.sh exits 2"] = broken[:2] + (broken[2].splitlines()[-1] + "\n",) + broken[3:]
    conductor = "run-conductor.sh"
    assert observed == {
        "launches per solvable issue": (0, "", "", [[conductor, "101"], [conductor, "102"]], [(0, 0), (0, 0)]),
        "solvable-issues.sh exits 2": (
            2, "", "orchestrate.sh: solvable-issues.sh exited 2; no answer about the solvable set\n", [], []),
        "context per assistant event, none from the result": (
            0, "context 301 53438\ncontext 301 62000\n", "", [[conductor, "301"]], [(5, 5)]),
        "over budget mid-step": (
            0, "context 401 150000\ncontext 401 150100\n", "", [[conductor, "401"]], [(3, 5)]),
        "step-done under the default, later crossing": (
            0, "context 501 110000\ncontext 501 150000\n", "", [[conductor, "501"]], [(5, 5)]),
        "over budget at the step-done call": (0, "context 601 150100\n", "", [[conductor, "601"]], [(3, 4)]),
        "never crosses": (0, "context 701 60000\ncontext 701 99100\n", "", [[conductor, "701"]], [(5, 5)]),
        "unset budget crossing 120000": (
            0, "context 901 120001\ncontext 901 120001\n", "", [[conductor, "901"]], [(3, 4)]),
        "relaunched after a stop": (
            0, "context 1001 150100\n", "", [[conductor, "1001"], [conductor, "1001"]], [(2, 3), (0, 0)]),
    }


def test_main_refuses_a_bad_budget_or_stop_timeout_relaunches_an_unfinished_conductor_and_skips_a_parked_one(
        tmp_path, monkeypatch, orchestrate, run_cli):
    ledger = "# Plan\n- [x] first step\n- [ ] second step\n"

    def orchestrated(name, answers, env, on_launch=lambda work, issue: None, issue_ledger=None):
        work = tmp_path / name
        work.mkdir()
        if issue_ledger:
            (work / ".tdd").mkdir()
            (work / ".tdd" / ("issue-%s.md" % issue_ledger)).write_text(ledger)

        def launch(pid, issue):
            on_launch(work, issue)
            return _FakeConductor(pid)

        code, out, err, launches = _orchestrated(
            work, monkeypatch, orchestrate, run_cli, answers, launch, env)
        kept = (work / ".tdd" / ("issue-%s.md" % issue_ledger)).read_text() if issue_ledger else None
        return code, out, err, launches, kept

    code, out, err, launches, _ = orchestrated("budget", [(0, "801\n")], {"VERI_CONDUCTOR_CTX_BUDGET": "120k"})
    assert (code, out, err, launches) == (
        2, "", "orchestrate.sh: VERI_CONDUCTOR_CTX_BUDGET must be a whole number of tokens: 120k\n", [])

    refusals = {}
    for value in ("abc", "nan", "inf", "0", "-1"):
        code, out, err, launches, _ = orchestrated(
            "stop-timeout" + value, [(0, "803\n")], {"VERI_CONDUCTOR_STOP_TIMEOUT": value})
        lines = err.splitlines()
        refusals[value] = (code, out, launches, len(lines),
                           "VERI_CONDUCTOR_STOP_TIMEOUT" in err, value in err, "Traceback" in err)
    assert refusals == {value: (2, "", [], 1, True, True, False) for value in ("abc", "nan", "inf", "0", "-1")}

    conductor = "run-conductor.sh"
    assert orchestrated("exitzero", [(0, "1101\n1102\n"), (0, "1101\n1102\n"), (0, "1102\n"), (3, "")], {},
                        issue_ledger="1101") == (
        0, "", "", [[conductor, "1101"], [conductor, "1101"], [conductor, "1102"]], ledger)

    def park(work, issue):
        if issue == "1201":
            (work / ".tdd" / "parked").mkdir()
            (work / ".tdd" / "parked" / "1201.md").write_text("Which test command should this run use?\n")

    assert orchestrated("parked", [(0, "1201\n1202\n"), (0, "1201\n1202\n"), (3, "")], {},
                        on_launch=park, issue_ledger="1201") == (
        0, "parked 1201\n", "", [[conductor, "1201"], [conductor, "1202"]], ledger)


@pytest.mark.process("a conductor's own session, signal dispositions, stdin, stderr and the SIGTERM it receives")
def test_a_conductor_leads_a_new_session_with_stdin_dev_null_orchestrates_stderr_sigint_and_sigquit_ignored_sigpipe_and_sigxfsz_fatal_and_is_sigtermed_at_the_stop(
        tmp_path, monkeypatch, orchestrate, run_cli):
    marks = tmp_path / "marks"
    stub = tmp_path / "run-conductor.sh"
    stub.write_text("""#!/usr/bin/env bash
{ printf 'argv %s:' "$#"; printf ' [%s]' "$@"; echo; } >> "$MARKS"
trap -p >> "$MARKS"
python3 -c 'import os, sys
pid, outer = int(sys.argv[1]), int(sys.argv[2])
print("new session led by its pid" if os.getsid(0) == pid != outer else "session %d, pid %d, outer %d" % (os.getsid(0), pid, outer))
print("stdin /dev/null" if os.path.samestat(os.fstat(0), os.stat("/dev/null")) else "stdin not /dev/null")' $$ "$OUTER_SID" >> "$MARKS"
echo "conductor $1 on stderr" >&2
exec 2> /dev/null
yes | dd bs=1 count=1 of=/dev/null
echo "yes ${PIPESTATUS[0]}" >> "$MARKS"
bash -c 'ulimit -f 0; echo x > "$1"' _ "$MARKS.big"
echo "xfsz $?" >> "$MARKS"
trap 'echo "TERM to $$" >> "$MARKS"; exit 0' TERM
exec > /dev/null
i=0
while [ $i -lt 400 ]; do sleep 0.01; i=$((i + 1)); done
echo "never stopped" >> "$MARKS"
""")
    stub.chmod(0o755)
    real_popen, launched = subprocess.Popen, []
    _served(monkeypatch, orchestrate, [(0, "1301\n"), (3, "")])

    def popen(args, *rest, **kwargs):
        launched.append(real_popen([str(stub)] + list(args[1:]), *rest, **kwargs))
        launched.append(os.path.basename(args[0]))
        return launched[0]

    monkeypatch.setattr(subprocess, "Popen", popen)
    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
    monkeypatch.delenv("VERI_CONDUCTOR_STOP_TIMEOUT", raising=False)
    own_stdin = tmp_path / "stdin"
    own_stdin.write_text("orchestrate's own stdin\n")
    saved_stdin = os.dup(0)
    try:
        with open(own_stdin) as f:
            os.dup2(f.fileno(), 0)
        code, out, err = run_cli(orchestrate, [], env={"MARKS": str(marks), "OUTER_SID": str(os.getsid(0))},
                                 cwd=tmp_path)
    finally:
        os.dup2(saved_stdin, 0)
        os.close(saved_stdin)
    conductor, name = launched
    conductor.wait(timeout=10)
    assert (code, out, err, name) == (0, "", "conductor 1301 on stderr\n", "run-conductor.sh")
    assert marks.read_text().splitlines() == [
        "argv 1: [1301]", "trap -- '' SIGINT", "trap -- '' SIGQUIT", "new session led by its pid",
        "stdin /dev/null", "yes 141", "xfsz 153", "TERM to %d" % conductor.pid]


@pytest.mark.process("SIGTERM to a conductor's process group and the drain of its stdout until EOF or VERI_CONDUCTOR_STOP_TIMEOUT")
def test_1126_1246_a_conductor_stopped_over_budget_gets_sigterm_to_its_group_whose_writer_after_it_ends_143_not_141_and_a_group_holding_its_stdout_past_the_stop_timeout_does_not_hang_the_run(
        tmp_path, monkeypatch, orchestrate, run_cli):
    import signal
    marks = tmp_path / "marks"
    stubs = {
        "1355": """#!/usr/bin/env bash
exec 2> /dev/null
(stopped=0
 trap 'stopped=1' TERM
 i=0
 while [ $stopped -eq 0 ] && [ $i -lt 400 ]; do echo '%(heartbeat)s'; sleep 0.01; i=$((i + 1)); done
 [ $stopped -eq 1 ] || { echo "writer never sent SIGTERM" >> "$MARKS"; exit 0; }
 i=0
 while [ $i -lt 1000 ] && [ ! -e "$MARKS.release" ]; do sleep 0.01; i=$((i + 1)); done
 echo '%(heartbeat)s'
 trap - TERM
 kill -TERM $BASHPID) &
writer=$!
trap '' TERM
echo '%(step_done)s'
echo '%(user)s'
wait $writer
echo "writer $?" >> "$MARKS"
exec > /dev/null
i=0
while [ $i -lt 1000 ] && [ ! -e "$MARKS.done" ]; do sleep 0.01; i=$((i + 1)); done
""" % {"heartbeat": _HEARTBEAT, "step_done": _step_done("1355", 150000, 100), "user": _USER},
        "1356": """#!/usr/bin/env bash
trap '' TERM
(i=0
 while [ $i -lt 1000 ] && [ ! -e "$MARKS.asked" ]; do sleep 0.01; i=$((i + 1)); done
 if [ $i -lt 1000 ]; then echo "asked again while the group held its stdout"; else echo "not asked again while the group held its stdout"; fi >> "$MARKS") &
echo '%(step_done)s'
echo '%(user)s'
wait $!
exec > /dev/null
i=0
while [ $i -lt 1000 ] && [ ! -e "$MARKS.done" ]; do sleep 0.01; i=$((i + 1)); done
""" % {"step_done": _step_done("1356", 150000, 100), "user": _USER},
    }
    for issue, text in stubs.items():
        stub = tmp_path / ("conductor-%s.sh" % issue)
        stub.write_text(text)
        stub.chmod(0o755)
    real_popen, real_setitimer, real_killpg = subprocess.Popen, signal.setitimer, os.killpg

    def orchestrated(issue, stop_timeout):
        launched, stops = [], []
        _served(monkeypatch, orchestrate, [(0, issue + "\n"), (3, "")],
                touch={2: [tmp_path / "marks.release", tmp_path / "marks.asked"]})

        def popen(args, *rest, **kwargs):
            launched.append(real_popen([str(tmp_path / ("conductor-%s.sh" % args[1]))], *rest, **kwargs))
            return launched[-1]

        def setitimer(which, seconds):
            real_setitimer(which, seconds)
            (tmp_path / "marks.release").touch()

        def killpg(pid, sig):
            stops.append((pid, sig))
            real_killpg(pid, sig)

        for mark in ("marks", "marks.release", "marks.asked", "marks.done"):
            (tmp_path / mark).unlink(missing_ok=True)
        monkeypatch.setattr(subprocess, "Popen", popen)
        monkeypatch.setattr(signal, "setitimer", setitimer)
        monkeypatch.setattr(os, "killpg", killpg)
        monkeypatch.setenv("VERI_CONDUCTOR_CTX_BUDGET", "100000")
        if stop_timeout is None:
            monkeypatch.delenv("VERI_CONDUCTOR_STOP_TIMEOUT", raising=False)
        else:
            monkeypatch.setenv("VERI_CONDUCTOR_STOP_TIMEOUT", stop_timeout)
        code, out, err = run_cli(orchestrate, [], env={"MARKS": str(marks)}, cwd=tmp_path)
        conductor = launched[0]
        running = "conductor running at exit" if conductor.poll() is None else "conductor gone at exit"
        (tmp_path / "marks.done").touch()
        conductor.wait(timeout=20)
        return (code, out, err, running, stops == [(conductor.pid, signal.SIGTERM)],
                marks.read_text().splitlines())

    assert orchestrated("1355", None) == (
        0, "context 1355 150100\n", "", "conductor running at exit", True, ["writer 143"])
    assert orchestrated("1356", "0.1") == (
        0, "context 1356 150100\n", "", "conductor running at exit", True,
        ["asked again while the group held its stdout"])


def test_1130_a_run_from_a_symlinked_scripts_directory_launches_through_it_and_reads_parked_in_the_working_directory_and_a_closed_or_gone_stdout_sigterms_the_group_reads_no_listing_again_and_exits_2_with_one_line(
        tmp_path, monkeypatch, orchestrate, run_cli):
    import importlib.util
    import signal
    import types
    realskill = tmp_path / "realskill"
    (realskill / ".tdd" / "parked").mkdir(parents=True)
    (realskill / ".tdd" / "parked" / "1402.md").write_text("")
    (realskill / "veri").symlink_to(SCRIPTS / "veri")
    (realskill / "solvable-issues.sh").symlink_to(SCRIPTS / "solvable-issues.sh")
    link = tmp_path / "link"
    link.symlink_to(realskill)
    elsewhere = tmp_path / "elsewhere"
    (elsewhere / ".tdd" / "parked").mkdir(parents=True)
    (elsewhere / ".tdd" / "parked" / "1401.md").write_text("")
    spec = importlib.util.spec_from_file_location("linked_orchestrate", link / "veri" / "orchestrate.py")
    linked = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(linked)

    def orchestrated(module, answers, stream, cwd, stdout):
        events = []

        def popen(args, *rest, **kwargs):
            events.append(("launch",) + tuple(args))
            conductor = _FakeConductor(4000 + len(events))
            conductor.stdout = io.BytesIO(stream)
            return conductor

        _served(monkeypatch, orchestrate, answers)
        monkeypatch.setattr(subprocess, "Popen", popen)
        monkeypatch.setattr(os, "killpg", lambda pid, sig: events.append(("killpg", pid, sig)))
        monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET", raising=False)
        monkeypatch.delenv("VERI_CONDUCTOR_STOP_TIMEOUT", raising=False)
        monkeypatch.setattr(sys, "stdout", stdout)
        try:
            code, out, err = run_cli(types.SimpleNamespace(main=module._main_stdout_gone_exits_2), [], cwd=cwd)
        finally:
            monkeypatch.setattr(sys, "stdout", sys.__stdout__)
        return code, out, err, events

    assert orchestrated(linked, [(0, "1401\n1402\n"), (0, "1401\n")], b"", elsewhere, sys.stdout) == (
        0, "", "", [("launch", str(link / "run-conductor.sh"), "1402"), ("killpg", 4001, signal.SIGTERM)])

    gone = "orchestrate.sh: stdout is gone: its reader has exited\n"
    line = (_assistant(1000, 0) + "\n").encode()
    read_end, write_end = os.pipe()
    os.close(read_end)
    broken = os.fdopen(write_end, "w")
    try:
        observed = {
            "a pipe whose reader has exited": orchestrated(
                orchestrate, [(0, "1601\n1602\n"), (2, "")], line, tmp_path, broken),
            "closed": orchestrated(orchestrate, [(0, "1701\n1702\n"), (2, "")], line, tmp_path, None),
        }
    finally:
        try:
            broken.close()
        except BrokenPipeError:
            pass
    launch = str(SCRIPTS / "run-conductor.sh")
    assert observed == {
        "a pipe whose reader has exited": (
            2, "", gone, [("launch", launch, "1601"), ("killpg", 4001, signal.SIGTERM)]),
        "closed": (2, "", gone, [("launch", launch, "1701"), ("killpg", 4001, signal.SIGTERM)]),
    }
