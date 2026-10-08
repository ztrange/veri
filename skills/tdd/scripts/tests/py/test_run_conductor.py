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


class FakeProcess:
    """A started process that has already exited 0, for whatever the module launches past resolution."""

    def __init__(self, args):
        self.args, self.returncode, self.pid = args, 0, 0
        self.stdin = self.stdout = self.stderr = None

    def communicate(self, *_, **__):
        return b"", b""

    def wait(self, *_, **__):
        return 0

    def poll(self):
        return 0


def fake_resolution(monkeypatch, origin, verifies, ls_remote):
    """git faked as a process: fetch succeeds, `rev-parse -q --verify` finds only `verifies`,
    `ls-remote` answers (code, out, err), a plain `rev-parse` resolves nothing."""
    calls = []

    def answer(args, *_, **kwargs):
        args = list(args)
        calls.append(args)
        code, out, err = 1, "", ""
        if args[:1] == ["git"] and args[3:] == ["remote", "get-url", "origin"]:
            code = 0 if origin else 2
            out = "https://example.invalid/skill.git\n" if origin else ""
            err = "" if origin else "error: No such remote 'origin'\n"
        elif args[:1] == ["git"] and args[3:] == ["fetch", "-q", "origin"]:
            code = 0
        elif args[:1] == ["git"] and args[3:6] == ["rev-parse", "-q", "--verify"]:
            code = 0 if args[6:] and args[6] in verifies else 1
        elif args[:1] == ["git"] and args[3:4] == ["ls-remote"]:
            code, out, err = ls_remote
        elif args[:1] == ["git"] and args[3:4] == ["rev-parse"]:
            code, err = 128, "fatal: ambiguous argument\n"
        elif args[:1] == ["fake-claude"]:
            code = 0
        if kwargs.get("stderr") is None and not kwargs.get("capture_output") and err:
            os.write(2, err.encode())
            err = ""
        if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
            out, err = out.encode(), err.encode()
        return subprocess.CompletedProcess(args, code, out, err)

    def check_output(args, *a, **kwargs):
        done = answer(args, *a, **kwargs)
        if done.returncode:
            raise subprocess.CalledProcessError(done.returncode, done.args, done.stdout, done.stderr)
        return done.stdout

    def popen(args, *_, **__):
        calls.append(list(args))
        return FakeProcess(list(args))

    monkeypatch.setattr(subprocess, "run", answer)
    monkeypatch.setattr(subprocess, "call", lambda *a, **k: answer(*a, **k).returncode)
    monkeypatch.setattr(subprocess, "check_call", lambda *a, **k: answer(*a, **k).returncode)
    monkeypatch.setattr(subprocess, "check_output", check_output)
    monkeypatch.setattr(subprocess, "Popen", popen)
    for name in ("system", "fork", "posix_spawn", "posix_spawnp", "execv", "execvp", "execve"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, lambda *args, **__: calls.append(list(args)))
    return calls


def test_main_resolves_the_pin_ref_through_origin_head_else_origins_default_from_ls_remote_symref_refusing_unpinned_with_two_exact_lines_silently_on_a_failed_ls_remote_and_as_head_with_no_origin(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.setenv("CLAUDE_BIN", "fake-claude")
    base = str(SCRIPTS.parent)
    run_conductor = importlib.import_module("veri.run_conductor")
    symref = (0, "ref: refs/heads/trunk\tHEAD\n1111111111111111111111111111111111111111\tHEAD\n", "warning: ls-remote noise\n")
    scenarios = {
        "origin-head": (True, {"refs/remotes/origin/HEAD"}, symref),
        "default": (True, {"refs/remotes/origin/trunk"}, symref),
        "no-default": (True, set(), (0, "1111111111111111111111111111111111111111\tHEAD\n", "warning: ls-remote noise\n")),
        "no-local-default": (True, set(), symref),
        "ls-remote-fails": (True, set(), (128, "", "fatal: unable to access 'origin'\n")),
        "no-origin": (False, set(), symref),
    }
    answers = {}
    for name, (origin, verifies, ls_remote) in scenarios.items():
        cwd = tmp_path / name
        cwd.mkdir()
        monkeypatch.chdir(cwd)
        calls = fake_resolution(monkeypatch, origin, verifies, ls_remote)
        code = run_conductor.main(["4242"])
        captured = capfdbinary.readouterr()
        ls_remotes = [call for call in calls if call[:1] == ["git"] and call[3:4] == ["ls-remote"]]
        resolved = [call[4] for call in calls
                    if call[:1] == ["git"] and call[3:4] == ["rev-parse"] and call[4:5] != ["-q"]][:1]
        if name in ("origin-head", "default", "no-origin"):
            answers[name] = (resolved, len(ls_remotes),
                             b"refusing to run unpinned" in captured.err, b"ls-remote noise" in captured.err)
        else:
            answers[name] = (code, captured.out, captured.err, ls_remotes, resolved)
    ls_remote = [["git", "-C", base, "ls-remote", "--symref", "origin", "HEAD"]]
    assert answers == {
        "origin-head": (["refs/remotes/origin/HEAD"], 0, False, False),
        "default": (["refs/remotes/origin/trunk"], 1, False, False),
        "no-default": (2, b"", (
            "run-conductor: refs/remotes/origin/HEAD is not set in '%s' and origin names no default branch"
            " — refusing to run unpinned\n" % base).encode(), ls_remote, []),
        "no-local-default": (2, b"", (
            "run-conductor: refs/remotes/origin/HEAD is not set in '%s' and origin's default branch 'trunk'"
            " has no refs/remotes/origin/trunk — refusing to run unpinned\n" % base).encode(), ls_remote, []),
        "ls-remote-fails": (2, b"", b"", ls_remote, []),
        "no-origin": (["HEAD"], 0, False, False),
    }
