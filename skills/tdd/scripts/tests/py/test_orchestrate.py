"""In-process cases for veri/orchestrate.py, the module orchestrate.sh is a shim over."""
import importlib
import io
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


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

    asks, launches = _passes(monkeypatch, [(0, "\n7\n")], park)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (0, "", "")
    assert (len(asks), launches) == (1, [])

    asks, launches = _passes(monkeypatch, [(0, "7\n"), (2, "")], lambda n, issue: None)
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (
        2, "", "orchestrate.sh: solvable-issues.sh exited 2; no answer about the solvable set\n")
    assert (len(asks), launches) == (2, [[conductor, "7"]])


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
    assert dispositions == {sig: signal.SIG_IGN for sig in watched}
    assert after == {sig: signal.SIG_DFL for sig in watched}
    assert asks == [[os.path.join(orchestrate.SCRIPTS, "solvable-issues.sh")]] * 2
