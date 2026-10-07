"""In-process cases for veri/detach.py, the launcher detach-command.sh's module starts its command through."""
import importlib
import pathlib
import signal
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def detach():
    return importlib.import_module("veri.detach")


def test_start_runs_argv_through_one_popen_in_a_new_session_with_the_given_stdio_inherited_fds_and_dispositions_and_returns_its_pid_unwaited(
        tmp_path, monkeypatch, detach):
    spawned = []
    touched = []

    class FakePopen:
        pid = 4242

        def __init__(self, args, **kwargs):
            spawned.append((args, kwargs))

        def __getattr__(self, name):
            if name in ("wait", "communicate", "poll", "kill", "terminate"):
                touched.append(name)
                return lambda *a, **k: None
            raise AttributeError(name)

    monkeypatch.setattr(subprocess, "Popen", FakePopen)
    argv = ["sh", "-c", "exit 0", ".tdd/x.exit", "true"]
    with open(tmp_path / "in", "w") as stdin, open(tmp_path / "out", "w") as out:
        pid = detach.start(argv, stdin=stdin, stdout=out, stderr=out)

        assert (pid, touched, len(spawned)) == (4242, [], 1)
        args, kwargs = spawned[0]
        assert args == argv
        assert {k: kwargs.get(k) for k in
                ("start_new_session", "stdin", "stdout", "stderr", "close_fds", "restore_signals")} == {
            "start_new_session": True, "stdin": stdin, "stdout": out, "stderr": out,
            "close_fds": False, "restore_signals": False}

    dispositions = {}
    monkeypatch.setattr(signal, "signal", lambda signum, handler: dispositions.__setitem__(signum, handler))
    kwargs["preexec_fn"]()
    assert dispositions == {signal.SIGPIPE: signal.SIG_DFL, signal.SIGINT: signal.SIG_IGN,
                            signal.SIGQUIT: signal.SIG_IGN, signal.SIGXFSZ: signal.SIG_IGN}
