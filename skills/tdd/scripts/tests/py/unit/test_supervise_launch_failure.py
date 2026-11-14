"""A leaf that cannot be launched leaves no placeholder in the supervisor's started list (#3771)."""
import pytest

from veri import supervise


def test_a_failing_popen_raises_and_leaves_started_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(supervise, "now", lambda: "1000")
    monkeypatch.setattr(supervise, "awake_seconds", lambda: 1000.0)

    def refuse(*_args, **_kwargs):
        raise FileNotFoundError("no sh")

    monkeypatch.setattr(supervise.subprocess, "Popen", refuse)
    started = []
    leaf_env = {"PYTEST_LEG_LOCK_WAIT_MARKER": str(tmp_path / "wait")}
    watch = (False, 1, 1, 1, 1, None)

    with pytest.raises(FileNotFoundError):
        supervise.attempt_once(started, "exp-leaf", ["true"], str(tmp_path / "log"), str(tmp_path / "rc"),
                               leaf_env, None, watch)

    assert started == []


def test_signals_arriving_during_launch_are_held_then_kill_the_leaf_and_exit_2(tmp_path, monkeypatch):
    import signal

    monkeypatch.setattr(supervise, "now", lambda: "1000")
    monkeypatch.setattr(supervise, "awake_seconds", lambda: 1000.0)
    killed = []
    monkeypatch.setattr(supervise, "kill_tree", lambda leaf, _poll: killed.append(leaf))

    class Exited(BaseException):
        pass

    def fake_exit(code):
        raise Exited(code)

    monkeypatch.setattr(supervise.os, "_exit", fake_exit)
    leaf = object()
    killed_during_launch = []

    def launching(*_args, **_kwargs):
        signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)
        signal.getsignal(signal.SIGHUP)(signal.SIGHUP, None)
        killed_during_launch.extend(killed)
        return leaf

    monkeypatch.setattr(supervise.subprocess, "Popen", launching)
    exitfile = tmp_path / "exit"
    started = []
    saved = {sig: signal.getsignal(sig) for sig in supervise.TRAPPED}
    try:
        supervise.trap(started, str(exitfile), 1, set())
        with pytest.raises(Exited) as raised:
            supervise.attempt_once(started, "exp-leaf", ["true"], str(tmp_path / "log"), str(tmp_path / "rc"),
                                   {"PYTEST_LEG_LOCK_WAIT_MARKER": str(tmp_path / "wait")}, None,
                                   (False, 1, 1, 1, 1, None))
    finally:
        for sig, handler in saved.items():
            signal.signal(sig, handler)

    assert killed_during_launch == []
    assert killed == [leaf]
    assert raised.value.args == (2,)
    assert exitfile.read_text().strip() == "2"
