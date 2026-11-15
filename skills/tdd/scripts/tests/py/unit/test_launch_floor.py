"""In-process cases for veri/launch_floor.py, the bash and Python floors leaf-launchable.sh refuses on."""
import importlib
import shutil
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.fixture
def launch_floor():
    return importlib.import_module("veri.launch_floor")


def fake_bash(monkeypatch, fake_processes, path, major, version):
    """shutil.which finding bash at <path>, and a bash there printing <major> then <version>, one per line.

    Returns the probes made, each (argv, env)."""
    fake = fake_processes.answers({"bash": (0, "%s\n%s\n" % (major, version), "")})
    monkeypatch.setattr(shutil, "which", lambda cmd, mode=None, path_=None, **kwargs: path if cmd == "bash" else None)

    class Probes:
        def __len__(self):
            return len(fake.seen)

        def __getitem__(self, index):
            argv, kwargs = fake.seen[index]
            return argv, kwargs.get("env")

    return Probes()


def test_bash_refusal_asks_the_bash_on_path_once_without_bash_env_or_env_and_refuses_a_major_below_5_naming_its_version_and_path(
        capsys, monkeypatch, launch_floor, fake_processes):
    monkeypatch.delenv("VERI_BASH_MAJOR", raising=False)
    monkeypatch.setenv("BASH_ENV", "/planted/bash_env")
    monkeypatch.setenv("ENV", "/planted/env")
    answers = []
    for major, version in (("5", "5.2.37(1)-release"), ("3", "3.2.57(1)-release")):
        calls = fake_bash(monkeypatch, fake_processes, "/opt/old/bin/bash", major, version)
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
        capsys, monkeypatch, launch_floor, fake_processes):
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
            calls = fake_bash(monkeypatch, fake_processes, "/opt/bin/bash", "5", "5.2.37(1)-release")
        else:
            calls = fake_bash(monkeypatch, fake_processes, "/opt/bin/bash", "3", "3.2.57(1)-release")
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
        capsys, monkeypatch, launch_floor, fake_processes):
    monkeypatch.delenv("VERI_BASH_MAJOR", raising=False)

    def refusal(version, path):
        return ("some-prefix: veri needs bash 5 or newer; this is bash %s (%s). "
                "Install it with `brew install bash` (it lands ahead of /bin/bash on PATH), "
                "or your package manager on Linux.\n" % (version, path))

    def fake(path, status, out):
        monkeypatch.setattr(shutil, "which", lambda cmd, mode=None, path_=None, **kwargs: path if cmd == "bash" else None)
        fake_processes.answers({} if path is None else {"bash": (status, out, "")})

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
        capsys, monkeypatch, tmp_path, fake_processes):
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

    monkeypatch.setenv("VERI_VENV", str(tmp_path / "no-venv"))
    fake_processes.answers({}, default=(1, "", ""))

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


def test_python_refusal_parses_the_version_as_the_lib_does_major_before_the_first_dot_minor_up_to_the_second(
        capsys, monkeypatch, tmp_path, launch_floor, fake_processes):
    import platform

    monkeypatch.setenv("VERI_VENV", str(tmp_path / "no-venv"))
    fake_processes.answers({}, default=(1, "", ""))
    monkeypatch.setattr(platform, "python_version", lambda: "3.13.0")

    answers = []
    for value in ("3", "unknown", "3.x", "3.12rc1", " 3.11", "3.08", ""):
        monkeypatch.setenv("VERI_PYTHON_VERSION", value)
        code = launch_floor.python_refusal("some-prefix")
        captured = capsys.readouterr()
        answers.append((value, code, captured.out, captured.err))
    assert answers == [
        ("3", 2, "", "some-prefix: veri needs Python 3.12 or newer; the python3 on PATH is version 3.\n"),
        ("unknown", 0, "", ""),
        ("3.x", 0, "", ""),
        ("3.12rc1", 0, "", ""),
        (" 3.11", 0, "", ""),
        ("3.08", 0, "", ""),
        ("", 0, "", ""),
    ]


def test_python_refusal_hint_asks_the_venv_interpreter_with_version_info_and_names_the_venv_only_when_it_exits_0(
        capsys, monkeypatch, tmp_path, launch_floor, fake_processes):
    import os
    import platform

    statuses = {}

    def answer(line, **kwargs):
        program = fake.argvs[-1][0]
        if not os.path.exists(program):
            raise FileNotFoundError(2, "No such file or directory", program)
        if not os.access(program, os.X_OK):
            raise PermissionError(13, "Permission denied", program)
        return statuses[program], "", ""

    fake = fake_processes.answers({}, default=answer)
    monkeypatch.setattr(platform, "python_version", lambda: "3.13.0")

    def interpreter(venv, status=None, executable=True):
        python = venv / "bin" / "python3"
        python.parent.mkdir(parents=True)
        python.write_text("#!/bin/sh\n")
        if executable:
            python.chmod(0o755)
        statuses[str(python)] = status
        return str(python)

    meets = tmp_path / "meets"
    interpreter(meets, 0)
    below = tmp_path / "below"
    interpreter(below, 1)
    inert = tmp_path / "inert"
    interpreter(inert, executable=False)
    home = tmp_path / "home"
    default = home / ".veri-tools" / "venv"
    interpreter(default, 0)
    monkeypatch.setenv("HOME", str(home))

    refusal = "some-prefix: veri needs Python 3.12 or newer; the python3 on PATH is version 3.11.9.\n"

    def hint(venv):
        return "some-prefix: the environment at %s meets it; put %s/bin first on PATH.\n" % (venv, venv)

    answers = []
    for venv, version in ((str(meets), "3.11.9"),
                          (str(below), "3.11.9"),
                          (str(tmp_path / "missing"), "3.11.9"),
                          (str(inert), "3.11.9"),
                          ("", "3.11.9"),
                          (str(meets), "3.12.0")):
        monkeypatch.setenv("VERI_VENV", venv)
        monkeypatch.setenv("VERI_PYTHON_VERSION", version)
        del fake.seen[:]
        code = launch_floor.python_refusal("some-prefix")
        captured = capsys.readouterr()
        asked = []
        for args, kwargs in fake.seen:
            assert any("version_info" in arg for arg in args[1:])
            assert kwargs.get("stderr") == subprocess.DEVNULL
            assert kwargs.get("stdout") is None and not kwargs.get("capture_output")
            asked.append(args[0])
        answers.append((venv, version, code, asked, captured.out, captured.err))

    def python3(venv):
        return [os.path.join(str(venv), "bin", "python3")]

    unrunnable = [answers[2][3], answers[3][3]]
    assert unrunnable[0] in ([], python3(tmp_path / "missing"))
    assert unrunnable[1] in ([], python3(inert))
    assert answers == [
        (str(meets), "3.11.9", 2, python3(meets), "", refusal + hint(meets)),
        (str(below), "3.11.9", 2, python3(below), "", refusal),
        (str(tmp_path / "missing"), "3.11.9", 2, unrunnable[0], "", refusal),
        (str(inert), "3.11.9", 2, unrunnable[1], "", refusal),
        ("", "3.11.9", 2, python3(default), "", refusal + hint(default)),
        (str(meets), "3.12.0", 0, [], "", ""),
    ]


def test_python_refusal_when_the_running_interpreter_is_the_venv_python3_below_the_floor_names_the_environment_and_advises_reinstalling_it_not_path_2106(
        capsys, monkeypatch, tmp_path, launch_floor, fake_processes):
    import os

    venv = str(tmp_path / "venv")
    monkeypatch.setenv("VERI_VENV", venv)
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.9.6")
    monkeypatch.setattr("sys.executable", os.path.join(venv, "bin", "python3"))
    fake_processes.answers({}, default=(1, "", ""))

    code = launch_floor.python_refusal("some-prefix")
    captured = capsys.readouterr()

    assert code == 2 and captured.out == ""
    assert venv in captured.err and "3.9.6" in captured.err
    assert "make install-dev" in captured.err and "remov" in captured.err
    assert "python3 on PATH" not in captured.err
    assert "first on PATH" not in captured.err
