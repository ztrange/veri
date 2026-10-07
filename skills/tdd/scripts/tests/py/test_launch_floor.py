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


def test_bash_refusal_with_veri_bash_major_set_starts_no_probe_and_names_that_value_in_place_of_the_version(
        capsys, monkeypatch, launch_floor):
    monkeypatch.delenv("BASH_ENV", raising=False)
    monkeypatch.delenv("ENV", raising=False)

    def refusal(value):
        return ("some-prefix: veri needs bash 5 or newer; this is bash %s (/opt/bin/bash). "
                "Install it with `brew install bash` (it lands ahead of /bin/bash on PATH), "
                "or your package manager on Linux.\n" % value)

    answers = []
    for value in ("abc", "5.1", " 5", "3", "05", "08", "09", ""):
        monkeypatch.setenv("VERI_BASH_MAJOR", value)
        if value:
            calls = fake_bash(monkeypatch, "/opt/bin/bash", "5", "5.2.37(1)-release")
        else:
            calls = fake_bash(monkeypatch, "/opt/bin/bash", "3", "3.2.57(1)-release")
        code = launch_floor.bash_refusal("some-prefix")
        captured = capsys.readouterr()
        answers.append((value, len(calls), code, captured.out, captured.err))
    assert answers == [
        ("abc", 0, 2, "", refusal("abc")),
        ("5.1", 0, 2, "", refusal("5.1")),
        (" 5", 0, 2, "", refusal(" 5")),
        ("3", 0, 2, "", refusal("3")),
        ("05", 0, 0, "", ""),
        ("08", 0, 0, "", ""),
        ("09", 0, 0, "", ""),
        ("", 1, 2, "", refusal("3.2.57(1)-release")),
    ]


def test_bash_refusal_with_no_bash_on_path_or_a_probe_that_fails_or_prints_no_number_refuses_naming_what_it_got(
        capsys, monkeypatch, launch_floor):
    monkeypatch.delenv("VERI_BASH_MAJOR", raising=False)

    def refusal(version, path):
        return ("some-prefix: veri needs bash 5 or newer; this is bash %s (%s). "
                "Install it with `brew install bash` (it lands ahead of /bin/bash on PATH), "
                "or your package manager on Linux.\n" % (version, path))

    def fake(path, status, out):
        def fake_which(cmd, mode=None, path_=None, **kwargs):
            return path if cmd == "bash" else None

        def output(kwargs):
            if path is None:
                raise AssertionError("unexpected process: no bash on PATH")
            if kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding"):
                return out
            return out.encode()

        def fake_run(args, **kwargs):
            return subprocess.CompletedProcess(args, status, output(kwargs), "" if kwargs.get("text") else b"")

        def fake_check_output(args, **kwargs):
            got = output(kwargs)
            if status:
                raise subprocess.CalledProcessError(status, args, output=got)
            return got

        def no_popen(args, **kwargs):
            raise AssertionError("unexpected process: %r" % (args,))

        monkeypatch.setattr(shutil, "which", fake_which)
        monkeypatch.setattr(subprocess, "run", fake_run)
        monkeypatch.setattr(subprocess, "check_output", fake_check_output)
        monkeypatch.setattr(subprocess, "Popen", no_popen)

    answers = []
    for path, status, out in ((None, 0, ""),
                              ("/opt/bin/bash", 1, "5\n5.2.37(1)-release\n"),
                              ("/opt/bin/bash", 0, "\nfive-ish\n"),
                              ("/opt/bin/bash", 0, "")):
        fake(path, status, out)
        code = launch_floor.bash_refusal("some-prefix")
        captured = capsys.readouterr()
        answers.append((code, captured.out, captured.err))
    assert answers == [
        (2, "", refusal("", "")),
        (2, "", refusal("5.2.37(1)-release", "/opt/bin/bash")),
        (2, "", refusal("five-ish", "/opt/bin/bash")),
        (2, "", refusal("", "/opt/bin/bash")),
    ]


def test_python_refusal_reads_the_floor_from_the_lib_beside_the_module_and_refuses_below_it_the_veri_python_version_else_the_running_interpreters(
        capsys, monkeypatch, tmp_path):
    import importlib.util
    import platform

    source = (SCRIPTS / "veri" / "launch_floor.py").read_text()

    plants = []

    def planted(floor):
        plants.append(floor)
        root = tmp_path / ("plant-%d" % len(plants))
        (root / "veri").mkdir(parents=True)
        (root / "lib").mkdir()
        (root / "veri" / "launch_floor.py").write_text(source)
        (root / "lib" / "venv-python.sh").write_text(
            "#!/usr/bin/env bash\n# planted\nVENV_FLOOR=%s\n\nvenv_dir() {\n  :\n}\n" % floor)
        spec = importlib.util.spec_from_file_location("planted_launch_floor_%d" % len(plants),
                                                      str(root / "veri" / "launch_floor.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def no_venv(args, **kwargs):
        return subprocess.CompletedProcess(args, 1, "" if kwargs.get("text") else b"", "")

    def no_popen(args, **kwargs):
        raise FileNotFoundError(2, "No such file or directory", args[0])

    monkeypatch.setenv("VERI_VENV", str(tmp_path / "no-venv"))
    monkeypatch.setattr(subprocess, "run", no_venv)
    monkeypatch.setattr(subprocess, "call", lambda args, **kwargs: 1)
    monkeypatch.setattr(subprocess, "Popen", no_popen)

    def refusal(floor, version):
        return "some-prefix: veri needs Python %s or newer; the python3 on PATH is version %s.\n" % (floor, version)

    answers = []
    for floor, env_version, running in (("3.12", "3.11.9", "3.13.0"),
                                        ("3.12", "3.12.0", "3.9.6"),
                                        ("3.13", "3.12.5", "3.13.0"),
                                        ("3.13", "3.13.0", "3.9.6"),
                                        ("3.12", None, "3.11.2"),
                                        ("3.12", None, "3.12.1"),
                                        ("3.13", None, "3.12.1")):
        module = planted(floor)
        if env_version is None:
            monkeypatch.delenv("VERI_PYTHON_VERSION", raising=False)
        else:
            monkeypatch.setenv("VERI_PYTHON_VERSION", env_version)
        monkeypatch.setattr(platform, "python_version", lambda running=running: running)
        code = module.python_refusal("some-prefix")
        captured = capsys.readouterr()
        answers.append((floor, env_version, running, code, captured.out, captured.err))
    assert answers == [
        ("3.12", "3.11.9", "3.13.0", 2, "", refusal("3.12", "3.11.9")),
        ("3.12", "3.12.0", "3.9.6", 0, "", ""),
        ("3.13", "3.12.5", "3.13.0", 2, "", refusal("3.13", "3.12.5")),
        ("3.13", "3.13.0", "3.9.6", 0, "", ""),
        ("3.12", None, "3.11.2", 2, "", refusal("3.12", "3.11.2")),
        ("3.12", None, "3.12.1", 0, "", ""),
        ("3.13", None, "3.12.1", 2, "", refusal("3.13", "3.12.1")),
    ]
