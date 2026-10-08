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


def fake_git(monkeypatch, fetch_code, fetch_err):
    """git faked as a process: origin exists, fetch answers as given, nothing else resolves."""
    calls = []

    def answer(args, *_, **kwargs):
        args = list(args)
        calls.append(args)
        code, out, err = 1, "", ""
        if args[:1] == ["git"] and args[3:] == ["remote", "get-url", "origin"]:
            code, out = 0, "https://example.invalid/skill.git\n"
        elif args[:1] == ["git"] and args[3:] == ["fetch", "-q", "origin"]:
            code, err = fetch_code, fetch_err
        elif args[:1] == ["git"] and "ls-remote" in args:
            code = 0
        if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
            out, err = out.encode(), err.encode()
        return subprocess.CompletedProcess(args, code, out, err)

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, answer)
    for name in ("system", "fork", "posix_spawn", "posix_spawnp", "execv", "execvp", "execve"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, answer)
    import time
    monkeypatch.setattr(time, "sleep", lambda *args: calls.append(["time.sleep", *args]))
    return calls


def test_main_fetches_origin_once_drops_a_successful_fetchs_stderr_and_refuses_a_failed_non_lock_fetch_with_its_stderr_then_the_stale_skill_line(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.setenv("VERI_FETCH_RETRY_SLEEP", "0")
    base = str(SCRIPTS.parent)
    run_conductor = importlib.import_module("veri.run_conductor")
    answers = []
    for fetch_code, fetch_err in ((0, "From origin\n * fetched quietly\n"),
                                  (128, "fatal: unable to access 'origin': no route\n")):
        cwd = tmp_path / str(fetch_code)
        cwd.mkdir()
        monkeypatch.chdir(cwd)
        calls = fake_git(monkeypatch, fetch_code, fetch_err)
        code = run_conductor.main(["4242"])
        captured = capfdbinary.readouterr()
        fetches = [call for call in calls if call[3:4] == ["fetch"]]
        sleeps = [call for call in calls if call[:1] in (["sleep"], ["time.sleep"])]
        answers.append((code, captured.out, captured.err, fetches, sleeps,
                        sorted(str(p.relative_to(cwd)) for p in cwd.rglob("*")) if fetch_code else None))
    fetch = ["git", "-C", base, "fetch", "-q", "origin"]
    success, failure = answers
    assert (b"fetched quietly" in success[2], success[3], failure) == (False, [fetch], (
        2, b"",
        b"fatal: unable to access 'origin': no route\n"
        + ("run-conductor: fetch of origin failed in '%s' — refusing to run a skill that may be stale\n" % base).encode(),
        [fetch], [], []))


def fake_locked_fetch(monkeypatch, sleep_code):
    """git faked as a process whose every fetch fails on a ref lock; sleep a process exiting as given."""
    calls = []
    lock = "error: cannot lock ref 'refs/remotes/origin/main': is at 1111111 but expected 2222222\n"

    def answer(args, *_, **kwargs):
        args = list(args)
        calls.append(args)
        code, out, err = 1, "", ""
        if args[:1] == ["git"] and args[3:] == ["remote", "get-url", "origin"]:
            code, out = 0, "https://example.invalid/skill.git\n"
        elif args[:1] == ["git"] and args[3:] == ["fetch", "-q", "origin"]:
            err = lock
        elif args[:1] == ["sleep"]:
            code = sleep_code
        if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
            out, err = out.encode(), err.encode()
        return subprocess.CompletedProcess(args, code, out, err)

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, answer)
    for name in ("system", "fork", "posix_spawn", "posix_spawnp", "execv", "execvp", "execve"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, answer)
    import time
    monkeypatch.setattr(time, "sleep", lambda *args: calls.append(["time.sleep", *args]))
    return calls, lock


def test_main_retries_a_cannot_lock_ref_fetch_through_a_sleep_process_at_most_60_fetches_and_59_sleeps_then_refuses_and_returns_1_when_sleep_fails(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    base = str(SCRIPTS.parent)
    run_conductor = importlib.import_module("veri.run_conductor")
    refusal = "run-conductor: fetch of origin failed in '%s' — refusing to run a skill that may be stale\n" % base
    answers = []
    for retry_sleep, sleep_code in (("7", 0), (None, 0), ("", 1), (None, 1)):
        cwd = tmp_path / ("%s-%d" % (retry_sleep, sleep_code))
        cwd.mkdir()
        monkeypatch.chdir(cwd)
        if retry_sleep is None:
            monkeypatch.delenv("VERI_FETCH_RETRY_SLEEP", raising=False)
        else:
            monkeypatch.setenv("VERI_FETCH_RETRY_SLEEP", retry_sleep)
        calls, lock = fake_locked_fetch(monkeypatch, sleep_code)
        code = run_conductor.main(["4242"])
        captured = capfdbinary.readouterr()
        fetches = [call for call in calls if call[:1] == ["git"] and call[3:4] == ["fetch"]]
        sleeps = [call for call in calls if call[:1] in (["sleep"], ["time.sleep"])]
        answers.append((code, captured.out, captured.err, len(fetches), sleeps, list(cwd.iterdir())))
    assert answers == [
        (2, b"", (lock * 60 + refusal).encode(), 60, [["sleep", "7"]] * 59, []),
        (2, b"", (lock * 60 + refusal).encode(), 60, [["sleep", "1"]] * 59, []),
        (1, b"", lock.encode(), 1, [["sleep", "1"]], []),
        (1, b"", lock.encode(), 1, [["sleep", "1"]], []),
    ]
