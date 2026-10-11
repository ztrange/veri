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


def past_the_guards(monkeypatch):
    """The bash and Python floors met, and claude named fake-claude."""
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.setenv("CLAUDE_BIN", "fake-claude")


def scratch_tmpdir(tmp_path, monkeypatch):
    """A directory under tmp_path that TMPDIR and tempfile both name, for the snapshot."""
    import tempfile
    scratch = tmp_path / "tmp"
    scratch.mkdir()
    monkeypatch.setenv("TMPDIR", str(scratch))
    monkeypatch.setattr(tempfile, "tempdir", str(scratch))
    return scratch


@pytest.mark.parametrize("argv", [[], [""]])
def test_main_with_no_or_an_empty_issue_returns_2_with_the_usage_line_alone_and_starts_no_process(
        argv, tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    calls = fake_processes()
    run_conductor = importlib.import_module("veri.run_conductor")

    code = run_conductor.main(list(argv))

    captured = capfdbinary.readouterr()
    assert (code, captured.out, captured.err, calls) == (2, b"", b"usage: run-conductor.sh <issue>\n", [])


def test_main_refuses_on_bash_before_the_python_floor_and_on_the_floor_before_the_usage_line_with_the_run_conductor_prefix_on_a_module_parsing_as_python_3_9(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
    import ast
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_VENV", str(tmp_path / "no-venv"))
    fake_processes()
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


def fake_locked_fetch(monkeypatch, sleep_code,
                      lock="error: cannot lock ref 'refs/remotes/origin/main': is at 1111111 but expected 2222222\n"):
    """git faked as a process whose every fetch fails on a ref lock; sleep a process exiting as given."""
    calls = []

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
        (2, b"", (lock * 60 + "run-conductor: another process holds the ref lock\n" + refusal).encode(), 60, [["sleep", "7"]] * 59, []),
        (2, b"", (lock * 60 + "run-conductor: another process holds the ref lock\n" + refusal).encode(), 60, [["sleep", "1"]] * 59, []),
        (1, b"", lock.encode(), 1, [["sleep", "1"]], []),
        (1, b"", lock.encode(), 1, [["sleep", "1"]], []),
    ]


def test_main_retries_git_2_53_reference_already_exists_fetch_as_a_held_ref_lock_at_most_60_fetches_and_59_sleeps_then_refuses_issue_1306(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.delenv("VERI_FETCH_RETRY_SLEEP", raising=False)
    monkeypatch.chdir(tmp_path)
    base = str(SCRIPTS.parent)
    run_conductor = importlib.import_module("veri.run_conductor")
    refusal = "run-conductor: fetch of origin failed in '%s' — refusing to run a skill that may be stale\n" % base
    calls, lock = fake_locked_fetch(
        monkeypatch, 0, "error: fetching ref refs/remotes/origin/master failed: reference already exists\n")

    code = run_conductor.main(["4242"])

    captured = capfdbinary.readouterr()
    fetches = [call for call in calls if call[:1] == ["git"] and call[3:4] == ["fetch"]]
    sleeps = [call for call in calls if call[:1] in (["sleep"], ["time.sleep"])]
    assert (code, captured.out, captured.err, len(fetches), sleeps, list(tmp_path.iterdir())) == (
        2, b"", (lock * 60 + "run-conductor: another process holds the ref lock\n" + refusal).encode(),
        60, [["sleep", "1"]] * 59, [])


def test_main_refusal_after_git_2_53_reference_already_exists_retries_names_the_ref_lock_as_the_cause_issue_1306(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.delenv("VERI_FETCH_RETRY_SLEEP", raising=False)
    monkeypatch.chdir(tmp_path)
    run_conductor = importlib.import_module("veri.run_conductor")
    calls, lock = fake_locked_fetch(
        monkeypatch, 0, "error: fetching ref refs/remotes/origin/master failed: reference already exists\n")

    code = run_conductor.main(["4242"])

    err = capfdbinary.readouterr().err
    fetches = [call for call in calls if call[:1] == ["git"] and call[3:4] == ["fetch"]]
    assert (code, len(fetches), b"lock" in err) == (2, 60, True), err[-300:]


def test_main_refuses_a_fetch_failing_with_neither_ref_lock_wording_at_once_without_naming_the_ref_lock_issue_1306(
        tmp_path, monkeypatch, capfdbinary):
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.delenv("VERI_FETCH_RETRY_SLEEP", raising=False)
    monkeypatch.chdir(tmp_path)
    run_conductor = importlib.import_module("veri.run_conductor")
    calls = fake_git(monkeypatch, 128, "fatal: couldn't find remote ref refs/heads/main\n")

    code = run_conductor.main(["4242"])

    err = capfdbinary.readouterr().err
    fetches = [call for call in calls if call[:1] == ["git"] and call[3:4] == ["fetch"]]
    sleeps = [call for call in calls if call[:1] in (["sleep"], ["time.sleep"])]
    assert (code, len(fetches), sleeps, b"lock" in err) == (2, 1, [], False), err


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
    past_the_guards(monkeypatch)
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
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
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


def test_main_with_veri_new_skill_exactly_1_rewrites_a_readable_record_then_appends_a_skill_repin_event_in_the_run_worktree_returning_2_on_its_failure_and_logs_nothing_on_a_first_launch_or_any_other_value(
        tmp_path, monkeypatch, capfdbinary, events):
    past_the_guards(monkeypatch)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    commit = "1111111111111111111111111111111111111111"
    run_conductor = importlib.import_module("veri.run_conductor")
    scenarios = {
        "re-pin": ("1", "2222222\n", True),
        "re-pin-event-fails": ("1", "2222222\n", False),
        "first-launch": ("1", None, True),
        "other-value": ("true", "2222222\n", True),
    }
    answers = {}
    for name, (new_skill, record, appendable) in scenarios.items():
        cwd = tmp_path / name
        cwd.mkdir()
        monkeypatch.chdir(cwd)
        monkeypatch.setenv("VERI_NEW_SKILL", new_skill)
        path = cwd / ".tdd" / "issue-4242-skill-commit"
        if record is not None:
            (cwd / ".tdd").mkdir()
            path.write_text(record)
        worktree = cwd / ".tdd" / "wt" / "4242"
        if not appendable:
            events.unappendable(worktree)
        calls = fake_pin(monkeypatch, commit, set())
        events.refuse_event_sh()
        fake_snapshot(monkeypatch, calls, 0, 0)
        code = run_conductor.main(["4242"])
        capfdbinary.readouterr()
        answers[name] = (path.read_text() if path.is_file() else None,
                         worktree.is_dir(), events.records(worktree), events.records(cwd),
                         code)
    repin = {"issue": "4242", "actor": "", "phase": "", "step": "", "event": "skill-repin", "attempt": "",
             "skill_commit": "", "commit": commit}
    assert answers == {
        "re-pin": (commit + "\n", True, [repin], [], 0),
        "re-pin-event-fails": (commit + "\n", True, [], [], 2),
        "first-launch": (commit + "\n", False, [], [], 0),
        "other-value": ("2222222\n", False, [], [], 2),
    }


def test_main_on_a_re_pin_records_the_ambient_veri_context_in_the_skill_repin_event_with_the_argument_as_its_issue(
        tmp_path, monkeypatch, capfdbinary, events):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    commit = "1111111111111111111111111111111111111111"
    run_conductor = importlib.import_module("veri.run_conductor")
    monkeypatch.chdir(tmp_path)
    for name, value in (("VERI_NEW_SKILL", "1"), ("CLAUDE_CODE_SESSION_ID", "sess-1353"), ("VERI_ISSUE", "9999"),
                        ("VERI_ACTOR", "conductor"), ("VERI_PHASE", "red"), ("VERI_STEP", "3"),
                        ("VERI_ATTEMPT", "2"), ("VERI_SKILL_COMMIT", "ambient")):
        monkeypatch.setenv(name, value)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-4242-skill-commit").write_text("2222222\n")
    calls = fake_pin(monkeypatch, commit, set())
    events.refuse_event_sh()
    fake_snapshot(monkeypatch, calls, 0, 0)
    code = run_conductor.main(["4242"])
    capfdbinary.readouterr()
    assert (code, events.records(tmp_path / ".tdd" / "wt" / "4242")) == (0, [
        {"issue": "4242", "actor": "conductor", "phase": "red", "step": "3", "event": "skill-repin", "attempt": "2",
         "skill_commit": "ambient", "commit": commit}])


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
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
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
        answers[name] = (code, snapshots, launches, sorted(os.listdir(scratch)))
    archive = ["git", "-C", base, "archive", commit, "."]
    tar = ["tar", "-x", "-C", (str(scratch), "tmp", True)]
    assert answers == {
        "pinned": (0, [archive, tar],
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
    past_the_guards(monkeypatch)
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
        answers[name] = (code, captured.out, captured.err, launches,
                         sorted(str(p.relative_to(cwd)) for p in cwd.rglob("*")
                                if p.name in (".gitignore", "issue-4242-skill-commit")))
    warning = "run-conductor: no skill commit resolvable from '%s' — running unpinned\n"
    assert answers == {
        "readable": (0, b"", (warning % (tmp_path / "readable-link")).encode(),
                     [{"VERI_SKILL_UNPINNED": "1", "VERI_SKILL_COMMIT": None,
                       "VERI_SKILL_CLONE": None, "VERI_SKILL_REF": None}], []),
        "unreadable": (2, b"", (warning % (tmp_path / "unreadable-link")
                                + "run-conductor: cannot read '%s/SKILL.md'\n" % (tmp_path / "unreadable-link")).encode(),
                       [], []),
    }


def fake_claude_launch(monkeypatch):
    """git faked as a process with no origin and no commit to resolve; every other process recorded
    with its argv, the bytes written to its stdin and the stdout, stderr and session options it was given."""
    launches = []

    def as_bytes(data):
        return data.encode() if isinstance(data, str) else (data or b"")

    def launched(args, kwargs):
        launch = {"argv": list(args), "stdin": as_bytes(kwargs.get("input")),
                  "stdout": kwargs.get("stdout"), "stderr": kwargs.get("stderr"),
                  "capture_output": kwargs.get("capture_output", False),
                  "start_new_session": kwargs.get("start_new_session", False),
                  "process_group": kwargs.get("process_group"), "preexec_fn": kwargs.get("preexec_fn")}
        launches.append(launch)
        return launch

    def answer(args, *_, **kwargs):
        args = list(args)
        if args[:1] == ["git"]:
            code = 2 if args[3:] == ["remote", "get-url", "origin"] else 128
            empty = "" if kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding") else b""
            return subprocess.CompletedProcess(args, code, empty, empty)
        launched(args, kwargs)
        return subprocess.CompletedProcess(args, 0, None, None)

    def popen(args, *_, **kwargs):
        args = list(args)
        if args[:1] == ["git"]:
            raise AssertionError("git started through Popen: %r" % args)
        launch = launched(args, kwargs)
        process = FakeProcess(args)

        class Stdin(io.BytesIO):
            def write(self, data):
                launch["stdin"] += as_bytes(data)
                return len(data)

        process.stdin = Stdin()

        def communicate(input=None, *_, **__):
            launch["stdin"] += as_bytes(input)
            return None, None

        process.communicate = communicate
        process.poll = lambda *_, **__: 0
        return process

    monkeypatch.setattr(subprocess, "run", answer)
    monkeypatch.setattr(subprocess, "call", lambda *a, **k: answer(*a, **k).returncode)
    monkeypatch.setattr(subprocess, "check_call", lambda *a, **k: answer(*a, **k).returncode)
    monkeypatch.setattr(subprocess, "Popen", popen)
    for name in ("system", "fork", "posix_spawn", "posix_spawnp", "execv", "execvp", "execve", "setsid", "setpgid"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, lambda *args, _name=name, **__: launches.append({"os": _name, "args": args}))
    return launches


@pytest.mark.parametrize("claude_bin,program", [(None, "claude"), ("", "claude"), ("fake-claude", "fake-claude")])
def test_main_launches_exactly_one_claude_with_the_fixed_print_mode_argv_and_no_prompt_element_the_prompt_on_its_stdin_its_stdout_and_stderr_inherited_and_no_new_session(
        claude_bin, program, tmp_path, monkeypatch, capfdbinary):
    import importlib.util
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    if claude_bin is None:
        monkeypatch.delenv("CLAUDE_BIN", raising=False)
    else:
        monkeypatch.setenv("CLAUDE_BIN", claude_bin)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
    (skill / "SKILL.md").write_text("# the procedure, read from SKILL.md\n")
    spec = importlib.util.spec_from_file_location("run_conductor_launch", str(skill / "scripts" / "veri" / "run_conductor.py"))
    run_conductor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_conductor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    launches = fake_claude_launch(monkeypatch)

    code = run_conductor.main(["4242"])

    capfdbinary.readouterr()
    assert code == 0
    observed = [dict(launch, stdin=b"# the procedure, read from SKILL.md" in launch.get("stdin", b""))
                for launch in launches]
    assert observed == [{"argv": [program, "-p", "--output-format", "stream-json", "--verbose",
                                  "--permission-mode", "bypassPermissions"],
                         "stdin": True, "stdout": None, "stderr": None, "capture_output": False,
                         "start_new_session": False, "process_group": None, "preexec_fn": None}]


def test_main_on_a_pinned_launch_whose_snapshot_holds_no_readable_skill_md_names_it_launches_no_claude_removes_the_snapshot_and_returns_2(
        tmp_path, monkeypatch, capfdbinary):
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    run_conductor = importlib.import_module("veri.run_conductor")
    calls = fake_pin(monkeypatch, "1111111111111111111111111111111111111111", set())
    _, launches = fake_snapshot(monkeypatch, calls, 0, 0)
    snapshots, popen = [], subprocess.Popen

    def tar_leaves_a_directory(args, *a, **kwargs):
        process = popen(args, *a, **kwargs)
        if list(args)[:1] == ["tar"]:
            snapshots.append(args[-1])
            os.remove(os.path.join(args[-1], "SKILL.md"))
            os.mkdir(os.path.join(args[-1], "SKILL.md"))
        return process

    monkeypatch.setattr(subprocess, "Popen", tar_leaves_a_directory)

    code = run_conductor.main(["4242"])

    captured = capfdbinary.readouterr()
    assert len(snapshots) == 1
    assert (code, captured.out, captured.err, launches, os.listdir(scratch)) == (
        2, b"", ("run-conductor: cannot read '%s/SKILL.md'\n" % snapshots[0]).encode(), [], [])


def test_main_hands_claude_the_snapshots_committed_skill_md_never_the_skill_clones_working_tree_skill_md_when_the_two_differ(
        tmp_path, monkeypatch, capfdbinary):
    import importlib.util
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
    (skill / "SKILL.md").write_text("# the working tree's uncommitted edit\n")
    spec = importlib.util.spec_from_file_location("run_conductor_committed", str(skill / "scripts" / "veri" / "run_conductor.py"))
    run_conductor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_conductor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    calls = fake_pin(monkeypatch, "1111111111111111111111111111111111111111", set())
    fake_snapshot(monkeypatch, calls, 0, 0)
    popen, run, stdins = subprocess.Popen, subprocess.run, []

    def tar_extracts_the_committed_skill_md(args, *a, **kwargs):
        process = popen(args, *a, **kwargs)
        if list(args)[:1] == ["tar"]:
            pathlib.Path(args[-1], "SKILL.md").write_text("# the committed procedure\n")
        return process

    def claude_reads_stdin(args, *a, **kwargs):
        if list(args)[:1] == ["fake-claude"]:
            data = kwargs.get("input")
            stdins.append(data.encode() if isinstance(data, str) else (data or b""))
        return run(args, *a, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", tar_extracts_the_committed_skill_md)
    monkeypatch.setattr(subprocess, "run", claude_reads_stdin)

    code = run_conductor.main(["4242"])

    capfdbinary.readouterr()
    assert code == 0
    assert [(stdin.startswith(b"# the committed procedure"), b"uncommitted edit" in stdin) for stdin in stdins] == [
        (True, False)]


def test_main_hands_claude_skill_md_stripped_of_trailing_newlines_then_the_base_line_the_pinned_line_only_when_pinned_and_the_solve_line_naming_the_unvalidated_issue_ignoring_further_arguments(
        tmp_path, monkeypatch, capfdbinary):
    import importlib.util
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
    (skill / "SKILL.md").write_text("# the procedure\n\nlast line\n\n\n")
    spec = importlib.util.spec_from_file_location("run_conductor_prompt", str(skill / "scripts" / "veri" / "run_conductor.py"))
    run_conductor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_conductor)
    commit = "1111111111111111111111111111111111111111"
    answers = {}

    unpinned = tmp_path / "unpinned"
    unpinned.mkdir()
    monkeypatch.chdir(unpinned)
    launches = fake_claude_launch(monkeypatch)
    codes = [run_conductor.main(["abc", "extra", "more"])]
    capfdbinary.readouterr()
    answers["unpinned"] = ([launch["stdin"] for launch in launches],
                           sorted(str(p.relative_to(unpinned)) for p in unpinned.rglob("*")))

    pinned = tmp_path / "pinned"
    pinned.mkdir()
    monkeypatch.chdir(pinned)
    calls = fake_pin(monkeypatch, commit, set())
    fake_snapshot(monkeypatch, calls, 0, 0)
    popen, run, stdins, snapshots = subprocess.Popen, subprocess.run, [], []

    def tar_extracts_a_skill_md_with_trailing_newlines(args, *a, **kwargs):
        process = popen(args, *a, **kwargs)
        if list(args)[:1] == ["tar"]:
            snapshots.append(args[-1])
            pathlib.Path(args[-1], "SKILL.md").write_text("# the committed procedure\n\n")
        return process

    def claude_reads_stdin(args, *a, **kwargs):
        if list(args)[:1] == ["fake-claude"]:
            data = kwargs.get("input")
            stdins.append(data.encode() if isinstance(data, str) else (data or b""))
        return run(args, *a, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", tar_extracts_a_skill_md_with_trailing_newlines)
    monkeypatch.setattr(subprocess, "run", claude_reads_stdin)
    codes.append(run_conductor.main(["abc", "extra"]))
    capfdbinary.readouterr()
    answers["pinned"] = (stdins, (pinned / ".tdd" / "issue-abc-skill-commit").read_text())

    assert (len(snapshots), codes) == (1, [0, 0])
    assert answers == {
        "unpinned": ([("# the procedure\n\nlast line"
                       "\n\nBase directory for this skill: %s\n"
                       "\nSolve issue #abc by the procedure above.\n" % skill).encode()], []),
        "pinned": ([("# the committed procedure"
                     "\n\nBase directory for this skill: %s\n"
                     "\nPinned skill commit (name it in the plan comment): %s\n"
                     "\nSolve issue #abc by the procedure above.\n" % (snapshots[0], commit)).encode()],
                   commit + "\n"),
    }


def test_main_strips_claudes_environment_through_veri_session_env_so_a_name_added_to_its_session_vars_is_absent_from_the_launch(
        tmp_path, monkeypatch, capfdbinary):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.setenv("VERI_PLANTED_621", "planted")
    monkeypatch.setenv("VERI_KEPT_621", "kept")
    session_env = importlib.import_module("session_env")
    monkeypatch.setattr(session_env, "SESSION_VARS", session_env.SESSION_VARS + ("VERI_PLANTED_621",))
    if "veri.session_env" in sys.modules:
        monkeypatch.setattr(sys.modules["veri.session_env"], "SESSION_VARS",
                            sys.modules["veri.session_env"].SESSION_VARS + ("VERI_PLANTED_621",))
    run_conductor = importlib.import_module("veri.run_conductor")
    monkeypatch.chdir(tmp_path)
    fake_claude_launch(monkeypatch)
    run, environments = subprocess.run, []

    def claude_records_its_environment(args, *a, **kwargs):
        if list(args)[:1] == ["fake-claude"]:
            environments.append(dict(kwargs.get("env") or os.environ))
        return run(args, *a, **kwargs)

    monkeypatch.setattr(subprocess, "run", claude_records_its_environment)

    code = run_conductor.main(["4242"])

    capfdbinary.readouterr()
    assert code == 0
    assert [("VERI_PLANTED_621" in env, env.get("VERI_KEPT_621")) for env in environments] == [(False, "kept")]


def test_main_given_a_claude_bin_whose_path_carries_the_session_id_runs_that_binary_and_hands_it_on_in_claudes_environment_1244(
        tmp_path, monkeypatch, capfdbinary):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    stub = "/private/tmp/claude-501/veri/sess-1244/scratchpad/claude"
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "sess-1244")
    monkeypatch.setenv("CLAUDE_BIN", stub)
    run_conductor = importlib.import_module("veri.run_conductor")
    monkeypatch.chdir(tmp_path)
    launches = fake_claude_launch(monkeypatch)
    run, environments = subprocess.run, []

    def claude_records_its_environment(args, *a, **kwargs):
        if list(args)[:1] != ["git"]:
            environments.append((kwargs.get("env") or os.environ).get("CLAUDE_BIN"))
        return run(args, *a, **kwargs)

    monkeypatch.setattr(subprocess, "run", claude_records_its_environment)

    code = run_conductor.main(["4242"])

    capfdbinary.readouterr()
    assert (code, [launch["argv"][0] for launch in launches], environments) == (0, [stub], [stub])


def test_main_records_the_skill_repin_event_then_hands_claude_no_veri_new_skill_every_other_veri_variable_and_an_ambient_veri_skill_commit_unpinned_or_veri_skill_unpinned_pinned(
        tmp_path, monkeypatch, capfdbinary, events):
    past_the_guards(monkeypatch)
    monkeypatch.setenv("VERI_NEW_SKILL", "1")
    monkeypatch.setenv("VERI_KEPT", "kept")
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "sess-1077")
    for name in ("VERI_ISSUE", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    commit = "1111111111111111111111111111111111111111"
    run_conductor = importlib.import_module("veri.run_conductor")
    names = ("VERI_NEW_SKILL", "CLAUDE_CODE_SESSION_ID", "VERI_KEPT", "VERI_SKILL_COMMIT", "VERI_SKILL_UNPINNED")
    answers = {}
    for name in ("pinned", "unpinned"):
        cwd = tmp_path / name
        cwd.mkdir()
        monkeypatch.chdir(cwd)
        if name == "pinned":
            monkeypatch.setenv("VERI_SKILL_UNPINNED", "ambient")
            monkeypatch.delenv("VERI_SKILL_COMMIT", raising=False)
            (cwd / ".tdd").mkdir()
            (cwd / ".tdd" / "issue-4242-skill-commit").write_text("2222222\n")
            calls = fake_pin(monkeypatch, commit, set())
            fake_snapshot(monkeypatch, calls, 0, 0)
        else:
            monkeypatch.setenv("VERI_SKILL_COMMIT", "ambient")
            monkeypatch.delenv("VERI_SKILL_UNPINNED", raising=False)
            fake_claude_launch(monkeypatch)
        events.refuse_event_sh()
        run, started = subprocess.run, []

        def records_each_environment(args, *a, **kwargs):
            program = os.path.basename(str(list(args)[0]))
            if program == "fake-claude":
                env = kwargs.get("env") if kwargs.get("env") is not None else os.environ
                started.append((program, {n: env.get(n) for n in names}))
            return run(args, *a, **kwargs)

        monkeypatch.setattr(subprocess, "run", records_each_environment)
        code = run_conductor.main(["4242"])
        capfdbinary.readouterr()
        answers[name] = (code, events.records(cwd / ".tdd" / "wt" / "4242"), started)
    assert answers == {
        "pinned": (0, [
            {"issue": "4242", "actor": "", "phase": "", "step": "", "event": "skill-repin", "attempt": "",
             "skill_commit": "", "commit": commit},
        ], [
            ("fake-claude", {"VERI_NEW_SKILL": None, "CLAUDE_CODE_SESSION_ID": None, "VERI_KEPT": "kept",
                             "VERI_SKILL_COMMIT": commit, "VERI_SKILL_UNPINNED": "ambient"}),
        ]),
        "unpinned": (0, [], [
            ("fake-claude", {"VERI_NEW_SKILL": None, "CLAUDE_CODE_SESSION_ID": None, "VERI_KEPT": "kept",
                             "VERI_SKILL_COMMIT": "ambient", "VERI_SKILL_UNPINNED": "1"}),
        ]),
    }


def test_main_returns_claudes_own_status_128_plus_n_for_a_signal_127_naming_a_claude_that_cannot_start_and_141_for_a_claude_exiting_0_unread_past_a_pipe_buffer(
        tmp_path, monkeypatch, capfdbinary):
    import importlib.util
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
    (skill / "SKILL.md").write_text("# the procedure\n" + "x" * 99 + "\n" * 2000 + "y" * 200000 + "\n")
    spec = importlib.util.spec_from_file_location("run_conductor_status", str(skill / "scripts" / "veri" / "run_conductor.py"))
    run_conductor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_conductor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    real_run, real_popen = subprocess.run, subprocess.Popen

    def git_has_no_origin_and_no_commit(args, *a, **kwargs):
        if list(args)[:1] == ["git"]:
            empty = "" if kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding") else b""
            return subprocess.CompletedProcess(list(args), 128, empty, empty)
        return real_run(args, *a, **kwargs)

    def popen_refuses_git(args, *a, **kwargs):
        if list(args)[:1] == ["git"]:
            raise AssertionError("git started through Popen: %r" % (args,))
        return real_popen(args, *a, **kwargs)

    monkeypatch.setattr(subprocess, "run", git_has_no_origin_and_no_commit)
    monkeypatch.setattr(subprocess, "Popen", popen_refuses_git)
    claudes = {"exit-%d" % n: "cat > /dev/null\nexit %d\n" % n for n in (0, 1, 2, 3, 17)}
    claudes.update({"sigterm": "cat > /dev/null\nkill -TERM $$\n",
                    "sigkill": "cat > /dev/null\nkill -KILL $$\n",
                    "unread-exit-0": "exit 0\n"})
    warning = ("run-conductor: no skill commit resolvable from '%s' — running unpinned\n" % skill).encode()
    answers = {}
    for name, body in list(claudes.items()) + [("missing", None)]:
        claude = tmp_path / ("claude-" + name)
        if body is not None:
            claude.write_text("#!/bin/sh\n" + body)
            claude.chmod(0o755)
        monkeypatch.setenv("CLAUDE_BIN", str(claude))
        try:
            code = run_conductor.main(["4242"])
        except Exception as error:
            code = type(error).__name__
        captured = capfdbinary.readouterr()
        answers[name] = (code, captured.out, captured.err)
    missing = ("run-conductor: %s: command not found\n" % (tmp_path / "claude-missing")).encode()
    assert answers == {
        "exit-0": (0, b"", warning), "exit-1": (1, b"", warning), "exit-2": (2, b"", warning),
        "exit-3": (3, b"", warning), "exit-17": (17, b"", warning),
        "sigterm": (143, b"", warning), "sigkill": (137, b"", warning),
        "unread-exit-0": (141, b"", warning),
        "missing": (127, b"", warning + missing),
    }


def fake_after_conductor(monkeypatch, commit, branches, launches):
    """git faked as a process with no origin: `rev-parse HEAD` resolves to `commit` (None: nothing),
    `rev-parse --show-toplevel` answers a directory's physical path when it is a worktree of its own
    (a `.git` file in it) and the working directory's otherwise, `for-each-ref` lists the `branches`
    its patterns match; tar drops a SKILL.md, and each fake-claude launch records whether the
    record was there."""
    import fnmatch

    def answer(args, *_, **kwargs):
        args = list(args)
        code, out = 0, ""
        if args[:1] == ["git"]:
            where = args[2] if args[1:2] == ["-C"] else "."
            where = os.path.join(kwargs.get("cwd") or os.getcwd(), where)
            rest = args[3:] if args[1:2] == ["-C"] else args[1:]
            if rest == ["remote", "get-url", "origin"]:
                code = 2
            elif "--show-toplevel" in rest:
                if not os.path.isdir(where):
                    code = 128
                elif os.path.exists(os.path.join(where, ".git")):
                    out = os.path.realpath(where) + "\n"
                else:
                    out = os.path.realpath(os.getcwd()) + "\n"
            elif "for-each-ref" in rest:
                patterns = [word for word in rest if word.startswith("refs/")]
                out = "".join(branch + "\n" for branch in branches
                              if not patterns or any(fnmatch.fnmatchcase(branch, p) for p in patterns))
            elif rest[:1] == ["rev-parse"]:
                code, out = (0, commit + "\n") if commit and rest[1:] == ["HEAD"] else (128, "")
        elif args[:1] == ["fake-claude"]:
            launches.append(os.path.exists(".tdd/issue-4242-skill-commit"))
        if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
            out = out.encode()
        return subprocess.CompletedProcess(args, code, out, b"" if isinstance(out, bytes) else "")

    def popen(args, *_, **__):
        args = list(args)
        if args[:1] == ["tar"]:
            pathlib.Path(args[-1], "SKILL.md").write_text("# skill\n")
        return FakeProcess(args)

    monkeypatch.setattr(subprocess, "run", answer)
    monkeypatch.setattr(subprocess, "call", lambda *a, **k: answer(*a, **k).returncode)
    monkeypatch.setattr(subprocess, "check_call", lambda *a, **k: answer(*a, **k).returncode)
    monkeypatch.setattr(subprocess, "Popen", popen)


def test_main_after_claude_exits_keeps_the_record_when_the_run_worktree_is_its_own_toplevel_or_a_tdd_n_branch_exists_and_removes_it_otherwise_pinned_or_unpinned(
        tmp_path, monkeypatch, capfdbinary):
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    scenarios = {
        "own-worktree-through-a-symlink": ("own", []),
        "plain-directory-with-a-run-branch": ("plain", ["refs/heads/tdd/4242-fix-it"]),
        "plain-directory-with-only-other-issues-branches": (
            "plain", ["refs/heads/tdd/42426-other", "refs/heads/tdd/4243-next", "refs/heads/main"]),
        "no-run-worktree-and-no-branch": (None, []),
    }
    answers = {}
    for launch in ("pinned", "unpinned"):
        for name, (worktree, branches) in scenarios.items():
            cwd = tmp_path / launch / name
            (cwd / ".tdd" / "wt").mkdir(parents=True)
            monkeypatch.chdir(cwd)
            if worktree == "own":
                real = tmp_path / launch / (name + "-real")
                real.mkdir()
                (real / ".git").write_text("gitdir: elsewhere\n")
                (cwd / ".tdd" / "wt" / "4242").symlink_to(real)
            elif worktree == "plain":
                (cwd / ".tdd" / "wt" / "4242").mkdir()
            if launch == "unpinned":
                (cwd / ".tdd" / "issue-4242-skill-commit").write_text("2222222\n")
            launches = []
            fake_after_conductor(monkeypatch, "1111111111111111111111111111111111111111"
                                 if launch == "pinned" else None, branches, launches)
            code = run_conductor.main(["4242"])
            capfdbinary.readouterr()
            answers[(launch, name)] = (code, launches, (cwd / ".tdd" / "issue-4242-skill-commit").exists())
    kept = {"own-worktree-through-a-symlink": True, "plain-directory-with-a-run-branch": True,
            "plain-directory-with-only-other-issues-branches": False, "no-run-worktree-and-no-branch": False}
    assert answers == {(launch, name): (0, [True], kept[name])
                       for launch in ("pinned", "unpinned") for name in scenarios}


def fake_tar(args, tar_code):
    """tar exiting `tar_code` after dropping the real SKILL.md into its -C directory."""
    process = FakeProcess(args)
    pathlib.Path(args[-1], "SKILL.md").write_bytes((SCRIPTS.parent / "SKILL.md").read_bytes())
    process.returncode = tar_code
    process.wait = process.poll = lambda *_, **__: tar_code
    return process


def fake_claude_exiting(monkeypatch, child_code, tar_code):
    """git faked as a process with no origin whose HEAD resolves; tar exiting `tar_code` after dropping
    the real SKILL.md into its -C directory; fake-claude recorded with its argv and stdin, exiting `child_code`."""
    launches = []

    def answer(args, *_, **kwargs):
        args = list(args)
        code, out = 128, ""
        if args[:1] == ["fake-claude"]:
            launches.append((args, kwargs.get("input")))
            return subprocess.CompletedProcess(args, child_code, None, None)
        if args[3:] == ["rev-parse", "HEAD"]:
            code, out = 0, "1111111111111111111111111111111111111111\n"
        elif args[3:] == ["remote", "get-url", "origin"]:
            code = 2
        if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
            out = out.encode()
        return subprocess.CompletedProcess(args, code, out, out[:0])

    def popen(args, *_, **__):
        args = list(args)
        return fake_tar(args, tar_code) if args[:1] == ["tar"] else FakeProcess(args)

    monkeypatch.setattr(subprocess, "run", answer)
    monkeypatch.setattr(subprocess, "Popen", popen)
    return launches


def test_cli_launches_claude_p_for_the_issue_in_stream_json_with_bypass_permissions_exits_with_the_childs_code_hands_a_direct_launch_a_procedure_naming_nothing_orchestrate_sh_adds_ends_a_failed_snapshot_with_2_and_without_an_issue_prints_only_its_usage_line_and_exits_2(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_CONDUCTOR_CTX_BUDGET"):
        monkeypatch.delenv(name, raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    scenarios = {
        "direct": (["4242"], 0, 0),
        "child-exits-17": (["4242"], 17, 0),
        "snapshot-tar-fails": (["4242"], 0, 5),
        "no-argument": ([], 0, 0),
    }
    answers = {}
    for name, (argv, child_code, tar_code) in scenarios.items():
        cwd = tmp_path / name
        cwd.mkdir()
        launches = fake_claude_exiting(monkeypatch, child_code, tar_code)
        code, out, err = run_cli(run_conductor, argv, cwd=cwd)
        answers[name] = {
            "code": code, "stdout": out, "stderr": err if name == "no-argument" else None,
            "argvs": [args for args, _ in launches],
            "issue in prompt": [b"Solve issue #4242 by the procedure above." in stdin for _, stdin in launches],
            "orchestrate.sh adds": sorted({added for _, stdin in launches
                                           for added in ("orchestrate.sh", "VERI_CONDUCTOR_CTX_BUDGET", ".tdd/parked/")
                                           if added.encode() in stdin}),
            "parked": (cwd / ".tdd" / "parked").exists(),
        }
    claude = ["fake-claude", "-p", "--output-format", "stream-json", "--verbose",
              "--permission-mode", "bypassPermissions"]
    launched = {"stdout": "", "stderr": None, "argvs": [claude], "issue in prompt": [True],
                "orchestrate.sh adds": [], "parked": False}
    assert answers == {
        "direct": dict(launched, code=0),
        "child-exits-17": dict(launched, code=17),
        "snapshot-tar-fails": {"code": 2, "stdout": "", "stderr": None, "argvs": [], "issue in prompt": [],
                               "orchestrate.sh adds": [], "parked": False},
        "no-argument": {"code": 2, "stdout": "", "stderr": "usage: run-conductor.sh <issue>\n", "argvs": [],
                        "issue in prompt": [], "orchestrate.sh adds": [], "parked": False},
    }


REAL_RUN, REAL_POPEN = subprocess.run, subprocess.Popen


def fake_claude_env(monkeypatch, origin, resolves, leaf):
    """git faked as a process: origin and its fetch present when `origin`, its HEAD and the clone's resolving when
    `resolves`; tar dropping the real SKILL.md into its -C directory; event.sh recorded and exiting 0; fake-claude
    recorded with its environment, and, given a `leaf` directory, detaching a real develop-red leaf there through
    supervise.sh and run-leaf.sh from that environment with a stub claude writing the VERI_GH_DRIVER it saw."""
    launches, events = [], []

    def answer(args, *_, **kwargs):
        args = list(args)
        code, out = 128, ""
        if args[:1] == ["fake-claude"]:
            launches.append(dict(kwargs["env"]))
            if leaf is not None:
                stub = leaf / "leaf-claude"
                stub.write_text('#!/bin/sh\nprintf \'%s\\n\' "${VERI_GH_DRIVER-<unset>}" > "$LEAF_DRIVER_OUT"\n'
                                'printf \'%s\\n\' \'{"type":"result","subtype":"success","is_error":false,"result":"ok"}\'\n')
                stub.chmod(0o755)
                leaf_env = dict(kwargs["env"], CLAUDE_BIN=str(stub), LEAF_DRIVER_OUT=str(leaf / "leaf-driver"),
                                VERI_POLL="0.02")
                REAL_RUN([str(SCRIPTS / "detach-leaf.sh"), str(SCRIPTS / "supervise.sh"), "develop-red",
                          str(SCRIPTS / "run-leaf.sh"), "leaf.prompt"], cwd=leaf, env=leaf_env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                REAL_RUN([str(SCRIPTS / "wait-leaf.sh"), "develop-red", "5"], cwd=leaf, env=leaf_env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return subprocess.CompletedProcess(args, 0, None, None)
        if args[0].endswith("event.sh"):
            events.append(args[1:])
            return subprocess.CompletedProcess(args, 0, None, None)
        if args[3:] == ["remote", "get-url", "origin"] and origin:
            code, out = 0, "https://example.invalid/skill.git\n"
        elif args[3:] == ["fetch", "-q", "origin"] and origin:
            code = 0
        elif args[3:] == ["rev-parse", "-q", "--verify", "refs/remotes/origin/HEAD"] and origin:
            code = 0
        elif args[3:4] == ["rev-parse"] and args[4:] in (["HEAD"], ["refs/remotes/origin/HEAD"]) and resolves:
            code, out = 0, "1111111111111111111111111111111111111111\n"
        if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
            out = out.encode()
        return subprocess.CompletedProcess(args, code, out, out[:0])

    def popen(args, *rest, **kwargs):
        args = list(args)
        if args[:1] not in (["git"], ["tar"]):
            return REAL_POPEN(args, *rest, **kwargs)
        return fake_tar(args, 0) if args[:1] == ["tar"] else FakeProcess(args)

    monkeypatch.setattr(subprocess, "run", answer)
    monkeypatch.setattr(subprocess, "Popen", popen)
    return launches, events


HANDLES = {"CLAUDECODE": "1", "CLAUDE_CODE_SESSION_ID": "parent-session",
           "CLAUDE_CODE_HOST_SESSION_ID": "parent-host-session", "CLAUDE_CODE_MESSAGING_SOCKET": "/tmp/parent.sock",
           "CLAUDE_CODE_MESSAGING_TOKEN": "parent-token", "CLAUDE_PID": "4141", "CLAUDE_CODE_CHILD_SESSION": "1",
           "CLAUDE_CODE_ENTRYPOINT": "cli"}


@pytest.mark.process("a leaf detached through detach-leaf.sh, supervise.sh and run-leaf.sh from the conductor's environment")
def test_cli_hands_claude_an_environment_without_the_session_handles_or_any_value_carrying_the_session_id_with_veri_variables_and_veri_gh_driver_through_to_a_detached_leaf_no_veri_new_skill_on_a_repin_and_the_pinned_clone_and_ref_only_when_pinned(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_GH_DRIVER", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED",
                 "VERI_SKILL_COMMIT", "CLAUDE_CODE_REMOTE_SESSION_ID", "CLAUDE_AUTO_BACKGROUND_TASKS", *HANDLES):
        monkeypatch.delenv(name, raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    base = str(SCRIPTS.parent)
    scenarios = {
        "handles": (dict(HANDLES, CLAUDE_AUTO_BACKGROUND_TASKS="true", VERI_MODEL_VERIFIER="probe-verifier-model"),
                    True, True, False, False),
        "session-id-carrier": ({"CLAUDE_CODE_SESSION_ID": "sess-933-fake", "FAKE_CARRIER": "x-sess-933-fake-y"},
                               True, True, False, False),
        "remote-session-id": ({"CLAUDE_CODE_SESSION_ID": "sess-966-fake",
                               "CLAUDE_CODE_REMOTE_SESSION_ID": "remote-unrelated-value"}, True, True, False, False),
        "repin": ({"VERI_NEW_SKILL": "1"}, True, True, True, False),
        "gh-driver": ({"VERI_GH_DRIVER": "graphql"}, True, True, False, True),
        "unpinned": ({}, False, False, False, False),
    }
    watched = (*HANDLES, "CLAUDE_AUTO_BACKGROUND_TASKS", "CLAUDE_CODE_REMOTE_SESSION_ID", "FAKE_CARRIER",
               "VERI_MODEL_VERIFIER", "VERI_NEW_SKILL", "VERI_GH_DRIVER", "VERI_SKILL_CLONE", "VERI_SKILL_REF",
               "VERI_SKILL_UNPINNED")
    answers = {}
    for name, (env, origin, resolves, recorded, detaches) in scenarios.items():
        cwd = tmp_path / name
        (cwd / ".tdd").mkdir(parents=True)
        if recorded:
            (cwd / ".tdd" / "issue-4242-skill-commit").write_text("0" * 40 + "\n")
        leaf = None
        if detaches:
            leaf = tmp_path / (name + "-leaf")
            leaf.mkdir()
            (leaf / "leaf.prompt").write_text("the leaf prompt\n")
        for var in watched:
            monkeypatch.delenv(var, raising=False)
        launches, events = fake_claude_env(monkeypatch, origin, resolves, leaf)
        code, _, _ = run_cli(run_conductor, ["4242"], env=env, cwd=cwd)
        answers[name] = {
            "code": code,
            "seen": [{var: seen[var] for var in watched if var in seen} for seen in launches],
            "repins": [event[0] for event in events],
            "leaf": (leaf / "leaf-driver").read_text() if leaf is not None and (leaf / "leaf-driver").exists() else None,
        }
    pinned = {"VERI_SKILL_CLONE": base, "VERI_SKILL_REF": "refs/remotes/origin/HEAD"}
    assert answers == {
        "handles": {"code": 0, "seen": [dict(pinned, VERI_MODEL_VERIFIER="probe-verifier-model")], "repins": [],
                    "leaf": None},
        "session-id-carrier": {"code": 0, "seen": [pinned], "repins": [], "leaf": None},
        "remote-session-id": {"code": 0, "seen": [pinned], "repins": [], "leaf": None},
        "repin": {"code": 0, "seen": [pinned], "repins": ["skill-repin"], "leaf": None},
        "gh-driver": {"code": 0, "seen": [dict(pinned, VERI_GH_DRIVER="graphql")], "repins": [], "leaf": "graphql\n"},
        "unpinned": {"code": 0, "seen": [{"VERI_SKILL_UNPINNED": "1"}], "repins": [], "leaf": None},
    }
