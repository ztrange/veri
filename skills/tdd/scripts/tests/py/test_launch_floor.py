"""In-process cases for veri/launch_floor.py, the bash and Python floors leaf-launchable.sh refuses on."""
import importlib
import pathlib
import shutil
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def launch_floor():
    return importlib.import_module("veri.launch_floor")


def fake_bash(monkeypatch, path, major, version):
    """shutil.which finding bash at <path>, and a bash there printing <major> then <version>, one per line."""
    calls = []

    def fake_which(cmd, mode=None, path_=None, **kwargs):
        return path if cmd == "bash" else None

    def answer(args, kwargs):
        calls.append((list(args), kwargs.get("env")))
        out = "%s\n%s\n" % (major, version)
        if kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding"):
            return out
        return out.encode()

    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess(args, 0, answer(args, kwargs), "" if kwargs.get("text") else b"")

    def fake_check_output(args, **kwargs):
        return answer(args, kwargs)

    def no_popen(args, **kwargs):
        raise AssertionError("unexpected process: %r" % (args,))

    monkeypatch.setattr(shutil, "which", fake_which)
    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    monkeypatch.setattr(subprocess, "Popen", no_popen)
    return calls


def test_bash_refusal_asks_the_bash_on_path_once_without_bash_env_or_env_and_refuses_a_major_below_5_naming_its_version_and_path(
        capsys, monkeypatch, launch_floor):
    monkeypatch.delenv("VERI_BASH_MAJOR", raising=False)
    monkeypatch.setenv("BASH_ENV", "/planted/bash_env")
    monkeypatch.setenv("ENV", "/planted/env")
    answers = []
    for major, version in (("5", "5.2.37(1)-release"), ("3", "3.2.57(1)-release")):
        calls = fake_bash(monkeypatch, "/opt/old/bin/bash", major, version)
        code = launch_floor.bash_refusal("some-prefix")
        captured = capsys.readouterr()
        assert len(calls) == 1
        args, env = calls[0]
        assert args[0] == "/opt/old/bin/bash" and args[1] == "-c"
        assert "BASH_VERSINFO[0]" in args[2] and "BASH_VERSION" in args[2]
        assert env is not None and "BASH_ENV" not in env and "ENV" not in env
        answers.append((code, captured.out, captured.err))
    assert answers == [
        (0, "", ""),
        (2, "", "some-prefix: veri needs bash 5 or newer; this is bash 3.2.57(1)-release (/opt/old/bin/bash). "
                "Install it with `brew install bash` (it lands ahead of /bin/bash on PATH), "
                "or your package manager on Linux.\n"),
    ]
