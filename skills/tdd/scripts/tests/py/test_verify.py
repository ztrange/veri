"""In-process cases for veri/verify.py, the module verify.sh is a shim over."""
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

USAGE = (b"usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file>"
         b" <test-path> [<target-test-id>]")


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


@pytest.mark.parametrize("argv", [[], ["green", "spec"], ["--step", "x", "green"]])
def test_main_with_fewer_than_three_positionals_returns_2_with_the_usage_line_alone_and_starts_no_process(
        argv, tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes(monkeypatch)
    verify = importlib.import_module("veri.verify")

    code = verify.main(list(argv))

    captured = capfdbinary.readouterr()
    assert len(USAGE) == 112
    assert (code, captured.out, captured.err, calls) == (2, b"", USAGE + b"\n", [])


@pytest.mark.parametrize("argv, flag", [(["--step"], b"--step"), (["--step", ""], b"--step"),
                                        (["--fast-cmd", "", "green", "s", "t"], b"--fast-cmd")])
def test_main_with_a_flag_missing_its_value_returns_2_naming_the_flag_then_the_usage_line_and_starts_no_process(
        argv, flag, tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes(monkeypatch)
    verify = importlib.import_module("veri.verify")

    code = verify.main(list(argv))

    captured = capfdbinary.readouterr()
    assert (code, captured.out, captured.err, calls) == (
        2, b"", b"verify: " + flag + b" needs a value\n" + USAGE + b"\n", [])


@pytest.mark.parametrize("builder, expected", [(1, 1), (5, 2), (FileNotFoundError, 2)])
def test_main_returns_the_builders_refusal_mapped_into_the_contract_with_its_stderr_and_launches_no_leaf(
        builder, expected, tmp_path, monkeypatch, capfdbinary):
    monkeypatch.chdir(tmp_path)
    launched = []
    builder_err = b"build-verify-prompt: unknown phase 'bogus'\n"

    def fake(args, *_, **kwargs):
        name = os.path.basename(str(args[0]))
        launched.append(name)
        if name != "build-verify-prompt.sh":
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if builder is FileNotFoundError:
            raise FileNotFoundError(2, "No such file or directory", str(args[0]))
        if kwargs.get("stderr") is None:
            os.write(2, builder_err)
            return subprocess.CompletedProcess(args, builder, b"", None)
        return subprocess.CompletedProcess(args, builder, b"", builder_err)

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, fake)
    verify = importlib.import_module("veri.verify")

    code = verify.main(["bogus", "spec.md", "tests/x.test.sh"])

    captured = capfdbinary.readouterr()
    passed_through = builder is FileNotFoundError or builder_err in captured.err
    assert (code, captured.out, passed_through, "build-verify-prompt.sh" in launched,
            "supervise.sh" in launched) == (expected, b"", True, True, False)
