"""In-process cases for veri/run_conductor.py, the module run-conductor.sh is a shim over."""
import importlib
import io
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


def fake_pin(monkeypatch, commit, accepted):
    """git faked as a process: no origin, `rev-parse HEAD` resolves to `commit`, `cat-file -e`
    accepts only `accepted`, and `for-each-ref` names a run branch so a kept record stays."""
    calls = []

    def answer(args, *_, **kwargs):
        args = list(args)
        calls.append(args)
        code, out, err = 0, "", ""
        if args[:1] == ["git"] and args[3:] == ["remote", "get-url", "origin"]:
            code, err = 2, "error: No such remote 'origin'\n"
        elif args[:1] == ["git"] and args[3:4] == ["rev-parse"]:
            code, out = (0, commit + "\n") if args[4:] == ["HEAD"] else (128, "")
        elif args[:1] == ["git"] and args[3:5] == ["cat-file", "-e"]:
            code = 0 if args[5:] and args[5] in accepted else 128
        elif args[:1] == ["git"] and "for-each-ref" in args:
            out = "refs/heads/tdd/4242-run\n"
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


def test_main_on_a_pinned_launch_seeds_the_gitignore_only_when_absent_writes_an_unreadable_record_keeps_an_accepted_one_as_given_and_refuses_any_other_with_2(
        tmp_path, monkeypatch, capfdbinary):
    import tempfile
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.setenv("CLAUDE_BIN", "fake-claude")
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch = tmp_path / "tmp"
    scratch.mkdir()
    monkeypatch.setenv("TMPDIR", str(scratch))
    monkeypatch.setattr(tempfile, "tempdir", str(scratch))
    base = str(SCRIPTS.parent)
    commit = "1111111111111111111111111111111111111111"
    accepted = {"1111111^{commit}", "main^{commit}"}
    run_conductor = importlib.import_module("veri.run_conductor")
    refusal = ("run-conductor: recorded skill commit '%s' is not in '" + base
               + "' — refusing to re-pin; set VERI_NEW_SKILL=1 to take the new skill\n")
    scenarios = {
        "fresh": (None, None),
        "own-gitignore": ("mine\n", None),
        "abbreviation": (None, "1111111\n\n"),
        "ref-name": (None, "main\n"),
        "foreign": (None, "2222222\n"),
        "directory": (None, ""),
    }
    answers = {}
    for name, (gitignore, record) in scenarios.items():
        cwd = tmp_path / name
        cwd.mkdir()
        monkeypatch.chdir(cwd)
        path = cwd / ".tdd" / "issue-4242-skill-commit"
        if gitignore is not None or record is not None:
            (cwd / ".tdd").mkdir()
        if gitignore is not None:
            (cwd / ".tdd" / ".gitignore").write_text(gitignore)
        if record == "":
            path.mkdir()
        elif record is not None:
            path.write_text(record)
        calls = fake_pin(monkeypatch, commit, accepted)
        code = run_conductor.main(["4242"])
        captured = capfdbinary.readouterr()
        seed = cwd / ".tdd" / ".gitignore"
        seeded = seed.read_text() if seed.is_file() else None
        kept = path.read_text() if path.is_file() else None
        cat_files = [call[5] for call in calls if call[:1] == ["git"] and call[3:5] == ["cat-file", "-e"]]
        expanded = [call for call in calls if commit in call and call[3:4] != ["rev-parse"]]
        if name in ("foreign", "directory"):
            answers[name] = (code, captured.out, captured.err.decode().splitlines(True)[-1:], kept)
        else:
            answers[name] = (seeded, kept, cat_files,
                             expanded if record else None, b"refusing to re-pin" in captured.err)
    assert answers == {
        "fresh": (".gitignore\nissue-*-skill-commit\n", commit + "\n", [], None, False),
        "own-gitignore": ("mine\n", commit + "\n", [], None, False),
        "abbreviation": (".gitignore\nissue-*-skill-commit\n", "1111111\n\n", ["1111111^{commit}"], [], False),
        "ref-name": (".gitignore\nissue-*-skill-commit\n", "main\n", ["main^{commit}"], [], False),
        "foreign": (2, b"", [refusal % "2222222"], "2222222\n"),
        "directory": (2, b"", [refusal % ""], None),
    }


def fake_event(monkeypatch, calls, event_code):
    """event.sh faked as a process exiting as given, recording its argv, directory and VERI_ISSUE."""
    events = []

    def wrap(started):
        def start(args, *a, **kwargs):
            if list(args)[:1] and str(list(args)[0]).endswith("event.sh"):
                env = kwargs.get("env") if kwargs.get("env") is not None else os.environ
                events.append((list(args), os.path.realpath(kwargs.get("cwd") or os.getcwd()), env.get("VERI_ISSUE")))
                done = subprocess.CompletedProcess(list(args), event_code, b"", b"")
                if started is popen:
                    process = FakeProcess(list(args))
                    process.returncode = event_code
                    process.wait = process.poll = lambda *_, **__: event_code
                    return process
                return done.returncode if started in (call, check_call) else done
            return started(args, *a, **kwargs)
        return start

    run, call, check_call, popen = subprocess.run, subprocess.call, subprocess.check_call, subprocess.Popen
    for name, started in (("run", run), ("call", call), ("check_call", check_call), ("Popen", popen)):
        monkeypatch.setattr(subprocess, name, wrap(started))
    return events


def test_main_with_veri_new_skill_exactly_1_rewrites_a_readable_record_then_runs_the_live_event_sh_in_the_run_worktree_returning_2_on_its_failure_and_logs_nothing_on_a_first_launch_or_any_other_value(
        tmp_path, monkeypatch, capfdbinary):
    import tempfile
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.setenv("CLAUDE_BIN", "fake-claude")
    monkeypatch.delenv("VERI_ISSUE", raising=False)
    scratch = tmp_path / "tmp"
    scratch.mkdir()
    monkeypatch.setenv("TMPDIR", str(scratch))
    monkeypatch.setattr(tempfile, "tempdir", str(scratch))
    commit = "1111111111111111111111111111111111111111"
    run_conductor = importlib.import_module("veri.run_conductor")
    scenarios = {
        "re-pin": ("1", "2222222\n", 0),
        "re-pin-event-fails": ("1", "2222222\n", 1),
        "first-launch": ("1", None, 0),
        "other-value": ("true", "2222222\n", 0),
    }
    answers = {}
    for name, (new_skill, record, event_code) in scenarios.items():
        cwd = tmp_path / name
        cwd.mkdir()
        monkeypatch.chdir(cwd)
        monkeypatch.setenv("VERI_NEW_SKILL", new_skill)
        path = cwd / ".tdd" / "issue-4242-skill-commit"
        if record is not None:
            (cwd / ".tdd").mkdir()
            path.write_text(record)
        calls = fake_pin(monkeypatch, commit, set())
        events = fake_event(monkeypatch, calls, event_code)
        code = run_conductor.main(["4242"])
        capfdbinary.readouterr()
        answers[name] = (path.read_text() if path.is_file() else None,
                         (cwd / ".tdd" / "wt" / "4242").is_dir(), events,
                         code if name in ("re-pin-event-fails", "other-value") else None)
    event = [str(SCRIPTS / "event.sh"), "skill-repin", "commit=" + commit]
    assert answers == {
        "re-pin": (commit + "\n", True,
                   [(event, os.path.realpath(tmp_path / "re-pin" / ".tdd" / "wt" / "4242"), "4242")], None),
        "re-pin-event-fails": (commit + "\n", True,
                               [(event, os.path.realpath(tmp_path / "re-pin-event-fails" / ".tdd" / "wt" / "4242"), "4242")], 2),
        "first-launch": (commit + "\n", False, [], None),
        "other-value": ("2222222\n", False, [], 2),
    }


def fake_snapshot(monkeypatch, calls, archive_code, tar_code):
    """`git archive` and `tar` faked as processes exiting as given, tar dropping a SKILL.md into its
    -C directory, and the launch of fake-claude recorded with the environment it was handed."""
    snapshots, launches = [], []

    def wrap(started):
        def start(args, *a, **kwargs):
            args = list(args)
            if args[:1] == ["git"] and args[3:4] == ["archive"]:
                code = archive_code
                snapshots.append(args)
            elif args[:1] == ["tar"]:
                code = tar_code
                target = args[-1]
                snapshots.append(args[:-1] + [(os.path.dirname(target), os.path.basename(target)[:3],
                                               os.path.isdir(target))])
                if os.path.isdir(target):
                    pathlib.Path(target, "SKILL.md").write_text("# skill\n")
            elif args[:1] == ["fake-claude"]:
                code = 0
                env = kwargs.get("env") if kwargs.get("env") is not None else os.environ
                launches.append({name: env.get(name) for name in
                                 ("VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED")})
            else:
                return started(args, *a, **kwargs)
            calls.append(args)
            if started is popen:
                process = FakeProcess(args)
                process.returncode = code
                process.stdout, process.stdin = io.BytesIO(b""), io.BytesIO()
                process.wait = process.poll = lambda *_, **__: code
                return process
            if started in (call, check_call):
                return code
            return subprocess.CompletedProcess(args, code, b"", b"")
        return start

    run, call, check_call, popen = subprocess.run, subprocess.call, subprocess.check_call, subprocess.Popen
    for name, started in (("run", run), ("call", call), ("check_call", check_call), ("Popen", popen)):
        monkeypatch.setattr(subprocess, name, wrap(started))
    return snapshots, launches


def test_main_snapshots_the_pinned_commit_by_git_archive_into_tar_under_tmpdir_hands_the_launch_the_commit_clone_and_ref_and_removes_the_snapshot_on_every_return_mapping_tar_5_to_2_1_to_1_3_to_3_and_a_failed_archive_to_2(
        tmp_path, monkeypatch, capfdbinary):
    import tempfile
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.setenv("CLAUDE_BIN", "fake-claude")
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    scratch = tmp_path / "tmp"
    scratch.mkdir()
    monkeypatch.setenv("TMPDIR", str(scratch))
    monkeypatch.setattr(tempfile, "tempdir", str(scratch))
    base = str(SCRIPTS.parent)
    commit = "1111111111111111111111111111111111111111"
    run_conductor = importlib.import_module("veri.run_conductor")
    scenarios = {
        "pinned": (0, 0),
        "tar-5": (0, 5),
        "tar-1": (0, 1),
        "tar-3": (0, 3),
        "archive-fails": (128, 0),
    }
    answers = {}
    for name, (archive_code, tar_code) in scenarios.items():
        cwd = tmp_path / name
        cwd.mkdir()
        monkeypatch.chdir(cwd)
        calls = fake_pin(monkeypatch, commit, set())
        snapshots, launches = fake_snapshot(monkeypatch, calls, archive_code, tar_code)
        code = run_conductor.main(["4242"])
        capfdbinary.readouterr()
        answers[name] = (None if name == "pinned" else code, snapshots, launches, sorted(os.listdir(scratch)))
    archive = ["git", "-C", base, "archive", commit, "."]
    tar = ["tar", "-x", "-C", (str(scratch), "tmp", True)]
    assert answers == {
        "pinned": (None, [archive, tar],
                   [{"VERI_SKILL_COMMIT": commit, "VERI_SKILL_CLONE": base, "VERI_SKILL_REF": "HEAD",
                     "VERI_SKILL_UNPINNED": None}], []),
        "tar-5": (2, [archive, tar], [], []),
        "tar-1": (1, [archive, tar], [], []),
        "tar-3": (3, [archive, tar], [], []),
        "archive-fails": (2, [archive, tar], [], []),
    }


def fake_unresolvable(monkeypatch):
    """git faked as a process with no origin and no commit to resolve; fake-claude's launch recorded
    with the environment it was handed."""
    launches = []

    def answer(args, *_, **kwargs):
        args = list(args)
        code, out, err = 128, "", ""
        if args[:1] == ["fake-claude"]:
            env = kwargs.get("env") if kwargs.get("env") is not None else os.environ
            launches.append({name: env.get(name) for name in
                             ("VERI_SKILL_UNPINNED", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF")})
            code = 0
        elif args[:1] == ["git"] and args[3:] == ["remote", "get-url", "origin"]:
            code, err = 2, "error: No such remote 'origin'\n"
        if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
            out, err = out.encode(), err.encode()
        return subprocess.CompletedProcess(args, code, out, err)

    def popen(args, *a, **kwargs):
        done = answer(args, *a, **kwargs)
        process = FakeProcess(list(args))
        process.returncode = done.returncode
        process.stdout, process.stdin = io.BytesIO(b""), io.BytesIO()
        process.wait = process.poll = lambda *_, **__: done.returncode
        process.communicate = lambda *_, **__: (b"", b"")
        return process

    monkeypatch.setattr(subprocess, "run", answer)
    monkeypatch.setattr(subprocess, "call", lambda *a, **k: answer(*a, **k).returncode)
    monkeypatch.setattr(subprocess, "check_call", lambda *a, **k: answer(*a, **k).returncode)
    monkeypatch.setattr(subprocess, "Popen", popen)
    for name in ("system", "fork", "posix_spawn", "posix_spawnp", "execv", "execvp", "execve"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, lambda *args, **__: launches.append(list(args)))
    return launches


def test_main_with_no_resolvable_commit_warns_writes_no_record_or_gitignore_launches_unpinned_from_the_unresolved_skill_directory_and_returns_2_when_its_skill_md_is_unreadable(
        tmp_path, monkeypatch, capfdbinary):
    import importlib.util
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.setenv("CLAUDE_BIN", "fake-claude")
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    answers = {}
    for name in ("readable", "unreadable"):
        real = tmp_path / (name + "-skill")
        (real / "scripts" / "veri").mkdir(parents=True)
        (real / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
        if name == "readable":
            (real / "SKILL.md").write_text("# skill\n")
        else:
            (real / "SKILL.md").mkdir()
        link = tmp_path / (name + "-link")
        link.symlink_to(real)
        spec = importlib.util.spec_from_file_location(
            "run_conductor_" + name, str(link / "scripts" / "veri" / "run_conductor.py"))
        run_conductor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_conductor)
        cwd = tmp_path / name
        cwd.mkdir()
        monkeypatch.chdir(cwd)
        launches = fake_unresolvable(monkeypatch)
        code = run_conductor.main(["4242"])
        captured = capfdbinary.readouterr()
        answers[name] = (code if name == "unreadable" else None, captured.out, captured.err, launches,
                         sorted(str(p.relative_to(cwd)) for p in cwd.rglob("*")
                                if p.name in (".gitignore", "issue-4242-skill-commit")))
    warning = "run-conductor: no skill commit resolvable from '%s' — running unpinned\n"
    assert answers == {
        "readable": (None, b"", (warning % (tmp_path / "readable-link")).encode(),
                     [{"VERI_SKILL_UNPINNED": "1", "VERI_SKILL_COMMIT": None,
                       "VERI_SKILL_CLONE": None, "VERI_SKILL_REF": None}], []),
        "unreadable": (2, b"", (warning % (tmp_path / "unreadable-link")
                                + "run-conductor: cannot read '%s/SKILL.md'\n" % (tmp_path / "unreadable-link")).encode(),
                       [], []),
    }
