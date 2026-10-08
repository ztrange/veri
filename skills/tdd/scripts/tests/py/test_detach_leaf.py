"""In-process cases for veri/detach_leaf.py, the module detach-leaf.sh is a shim over."""
import importlib
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: detach-leaf.sh <cmd> [args…]\n"


@pytest.fixture
def detach_leaf():
    return importlib.import_module("veri.detach_leaf")


def test_main_refuses_no_argument_with_the_usage_line_and_launches_its_argv_once_returning_0_silently(
        monkeypatch, capsys, detach_leaf):
    launches = []

    class FakePopen:
        pid = 4242

        def __init__(self, args, **kwargs):
            launches.append(args)

    monkeypatch.setattr(subprocess, "Popen", FakePopen)

    code = detach_leaf.main([])
    assert (code, capsys.readouterr(), launches) == (2, ("", USAGE), [])

    code = detach_leaf.main(["true"])
    assert (code, capsys.readouterr(), launches) == (0, ("", ""), [["true"]])


def test_main_launches_with_stdin_devnull_inherited_stdout_stderr_and_fds_in_a_new_session_never_waiting(
        monkeypatch, detach_leaf):
    import signal

    launches, calls = [], []

    class FakePopen:
        pid = 4242

        def __init__(self, args, **kwargs):
            launches.append((args, kwargs))

        def __getattr__(self, name):
            if name in ("wait", "communicate", "poll", "kill", "terminate"):
                calls.append(name)
                return lambda *a, **k: None
            raise AttributeError(name)

    monkeypatch.setattr(subprocess, "Popen", FakePopen)

    assert detach_leaf.main(["true"]) == 0
    [(args, kwargs)] = launches
    launch = {key: kwargs.get(key, "unset") for key in
              ("stdin", "stdout", "stderr", "close_fds", "start_new_session", "shell", "executable")}
    assert (args, launch) == (["true"], {
        "stdin": subprocess.DEVNULL, "stdout": None, "stderr": None, "close_fds": False,
        "start_new_session": True, "shell": "unset", "executable": "unset"})

    dispositions = []
    monkeypatch.setattr(signal, "signal", lambda signum, handler: dispositions.append((signum, handler)))
    kwargs["preexec_fn"]()
    assert dict(dispositions) == {
        signal.SIGPIPE: signal.SIG_DFL, signal.SIGINT: signal.SIG_IGN,
        signal.SIGQUIT: signal.SIG_IGN, signal.SIGXFSZ: signal.SIG_IGN}
    assert calls == []
