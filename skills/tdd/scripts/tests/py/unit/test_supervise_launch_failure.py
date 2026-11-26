"""A signal reaching the supervisor while a leaf launches is held until the leaf exists; one after a launch that
failed is not (#3771, #4303)."""
import pytest
from veri import supervise


def test_signals_arriving_during_launch_are_held_then_kill_the_leaf_and_exit_2(tmp_path, monkeypatch, fake_processes):
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
    killed_during_launch = []

    def launching(_line, **_kwargs):
        signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)
        signal.getsignal(signal.SIGHUP)(signal.SIGHUP, None)
        killed_during_launch.extend(killed)
        return 0, "", ""

    launched = fake_processes.answers({"": launching})
    exitfile = tmp_path / "exit"
    holder = supervise.LeafHolder()
    saved = {sig: signal.getsignal(sig) for sig in supervise.TRAPPED}
    try:
        supervise.trap(holder, str(exitfile), 1, set())
        with pytest.raises(Exited) as raised:
            supervise.attempt_once(holder, "exp-leaf", ["true"], str(tmp_path / "log"), str(tmp_path / "rc"),
                                   {"PYTEST_LEG_LOCK_WAIT_MARKER": str(tmp_path / "wait")}, None,
                                   (False, 1, 1, 1, 1, None))
    finally:
        for sig, handler in saved.items():
            signal.signal(sig, handler)

    assert killed_during_launch == []
    assert killed == launched.popens
    assert len(launched.popens) == 1
    assert raised.value.args == (2,)
    assert exitfile.read_text().strip() == "2"


class Exited(BaseException):
    pass


def trapped_exits(monkeypatch):
    """The trap's kills recorded and its os._exit raised as Exited, with the wall and awake clocks frozen."""
    monkeypatch.setattr(supervise, "now", lambda: "1000")
    monkeypatch.setattr(supervise, "awake_seconds", lambda: 1000.0)
    killed = []
    monkeypatch.setattr(supervise, "kill_tree", lambda leaf, _poll: killed.append(leaf))

    def fake_exit(code):
        raise Exited(code)

    monkeypatch.setattr(supervise.os, "_exit", fake_exit)
    return killed


def test_a_signal_after_a_failed_launch_exits_2_at_once_killing_nothing(tmp_path, monkeypatch, fake_processes):
    import signal

    killed = trapped_exits(monkeypatch)
    fake_processes.answers({"": FileNotFoundError("no sh")})
    exitfile = tmp_path / "exit"
    holder = supervise.LeafHolder()
    saved = {sig: signal.getsignal(sig) for sig in supervise.TRAPPED}
    try:
        supervise.trap(holder, str(exitfile), 1, set())
        with pytest.raises(FileNotFoundError):
            supervise.attempt_once(holder, "exp-leaf", ["true"], str(tmp_path / "log"), str(tmp_path / "rc"),
                                   {"PYTEST_LEG_LOCK_WAIT_MARKER": str(tmp_path / "wait")}, None,
                                   supervise.Watch(False, "1000", "180", "1", 0.0))
        with pytest.raises(Exited) as raised:
            signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)
    finally:
        for sig, handler in saved.items():
            signal.signal(sig, handler)

    assert (killed, raised.value.args, exitfile.read_text().strip()) == ([], (2,), "2")


def test_a_signal_during_a_retrys_launch_is_held_then_kills_only_the_new_leaf(tmp_path, monkeypatch, fake_processes):
    import signal

    killed = trapped_exits(monkeypatch)
    launches = []

    def launching(_line, **_kwargs):
        launches.append(list(killed))
        if len(launches) == 2:
            signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)
            launches.append(list(killed))
        return 0, "", ""

    launched = fake_processes.answers({"": launching})
    exitfile = tmp_path / "exit"
    holder = supervise.LeafHolder()
    watch = supervise.Watch(False, "1000", "180", "1", 0.0)
    args = ("exp-leaf", ["true"], str(tmp_path / "log"), str(tmp_path / "rc"),
            {"PYTEST_LEG_LOCK_WAIT_MARKER": str(tmp_path / "wait")}, None, watch)
    saved = {sig: signal.getsignal(sig) for sig in supervise.TRAPPED}
    try:
        supervise.trap(holder, str(exitfile), 1, set())
        first = supervise.attempt_once(holder, *args)
        with pytest.raises(Exited) as raised:
            supervise.attempt_once(holder, *args)
    finally:
        for sig, handler in saved.items():
            signal.signal(sig, handler)

    assert (first[0], launches, len(launched.popens)) == ("killed-external", [[], [], []], 2)
    assert killed == [launched.popens[1]]
    assert (raised.value.args, exitfile.read_text().strip()) == ((2,), "2")
