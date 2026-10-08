"""In-process cases for veri/run_conductor.py, the module run-conductor.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def fake_processes(monkeypatch):
    """Every process entry point recording each command it is asked to start."""
    calls = []

    def record(args, *_, **__):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, record)
    for name in ("system", "fork", "posix_spawn", "posix_spawnp", "execv", "execvp", "execve"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, record)
    return calls


@pytest.mark.parametrize("argv", [[], [""]])
def test_main_with_no_or_an_empty_issue_returns_2_with_the_usage_line_alone_and_starts_no_process(
        argv, tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    calls = fake_processes(monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")

    code = run_conductor.main(list(argv))

    captured = capfdbinary.readouterr()
    assert (code, captured.out, captured.err, calls) == (2, b"", b"usage: run-conductor.sh <issue>\n", [])


def test_main_refuses_on_bash_before_the_python_floor_and_on_the_floor_before_the_usage_line_with_the_run_conductor_prefix_on_a_module_parsing_as_python_3_9(
        tmp_path, monkeypatch, capfdbinary):
    import ast
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_VENV", str(tmp_path / "no-venv"))
    fake_processes(monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    answers = []
    for major, python in (("3", "3.12.0"), ("3", "3.11.9"), ("5", "3.11.9")):
        monkeypatch.setenv("VERI_BASH_MAJOR", major)
        monkeypatch.setenv("VERI_PYTHON_VERSION", python)
        code = run_conductor.main([])
        captured = capfdbinary.readouterr()
        answers.append((code, captured.out, [line.split(b";")[0] for line in captured.err.splitlines()]))
    module = SCRIPTS / "veri" / "run_conductor.py"
    tree = ast.parse(module.read_text())
    imported = [alias.name for node in tree.body if isinstance(node, ast.Import) for alias in node.names]
    sources = [module] + [SCRIPTS / "veri" / (name + ".py") for name in imported
                          if (SCRIPTS / "veri" / (name + ".py")).exists()]
    unparsable = []
    for source in sources:
        try:
            ast.parse(source.read_text(), feature_version=(3, 9))
        except SyntaxError as error:
            unparsable.append((source.name, str(error)))
    assert (answers, "launch_floor" in imported, unparsable) == ([
        (2, b"", [b"run-conductor: veri needs bash 5 or newer"]),
        (2, b"", [b"run-conductor: veri needs bash 5 or newer"]),
        (2, b"", [b"run-conductor: veri needs Python 3.12 or newer"]),
    ], True, [])
