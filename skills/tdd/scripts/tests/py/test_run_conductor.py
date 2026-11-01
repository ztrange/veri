"""In-process cases for veri/run_conductor.py, the module run-conductor.sh is a shim over."""
import importlib
import io
import json
import os
import pathlib
import re
import shutil
import signal
import subprocess
import sys

import pytest

from test_supervise import checked_step, committed_head

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def reaches_issue_body_boundary():
    """Named by a case that exercises the pre-launch issue-body fetch itself: it gets the real gh boundary."""


@pytest.fixture(autouse=True)
def issue_body_fetch_answers_empty(request, monkeypatch):
    """The pre-launch issue-body gh call answered with an empty body, so the row-ID check finds no rows."""
    if "reaches_issue_body_boundary" in request.fixturenames:
        return
    import github
    real = github.gh_issue_view

    def view(number, field):
        return "" if field == "body" else real(number, field)

    monkeypatch.setattr(github, "gh_issue_view", view)


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


def loose_skill(source, destination):
    """Copy the files under a skills/tdd directory that git tracks or would track, as the work tree has them."""
    source, destination = pathlib.Path(source), pathlib.Path(destination)
    listed = subprocess.run(
        ["git", "-C", str(source), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True)
    if listed.returncode != 0:
        raise RuntimeError(f"skill copy: git ls-files failed in {source}: {listed.stderr.decode(errors='replace')}")
    for name in sorted(set(listed.stdout.decode().split("\0")) - {""}):
        origin = source / name
        if not os.path.lexists(origin):
            continue
        target = destination / name
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origin, target, follow_symlinks=False)
        except OSError as error:
            raise RuntimeError(f"skill copy: could not copy {origin} to {target}: {error}") from error


def test_main_with_no_issue_returns_2_with_the_usage_line_alone_and_starts_no_process(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    calls = fake_processes()
    run_conductor = importlib.import_module("veri.run_conductor")

    code = run_conductor.main([])

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


def patch_process_boundary(monkeypatch, subprocess_fns, os_fn, extra_os=()):
    """Replace every way the code under test could start a process; os_fn(name, *args, **kwargs) answers the os ones."""
    if callable(subprocess_fns):
        subprocess_fns = dict.fromkeys(("run", "Popen", "call", "check_call", "check_output"), subprocess_fns)
    for name, fn in subprocess_fns.items():
        monkeypatch.setattr(subprocess, name, fn)
    for name in ("system", "fork", "posix_spawn", "posix_spawnp", "execv", "execvp", "execve", *extra_os):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, lambda *args, _name=name, **kwargs: os_fn(_name, *args, **kwargs))


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

    patch_process_boundary(monkeypatch, answer, lambda _name, *args, **kwargs: answer(*args, **kwargs))
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


def test_cli_a_failed_fetch_of_origin_exits_2_before_any_conductor_is_launched_and_names_the_fetch_on_stderr(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.setenv("VERI_FETCH_RETRY_SLEEP", "0")
    run_conductor = importlib.import_module("veri.run_conductor")
    calls = fake_git(monkeypatch, 128, "fatal: unable to access 'origin': no route\n")

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    launched = [call for call in calls if call[:1] == ["fake-claude"]]
    assert (code, launched, "fetch of origin failed" in stderr) == (2, [], True), stderr


def test_cli_a_revise_budget_that_is_not_a_whole_number_exits_2_with_one_stderr_line_naming_it_before_any_process_starts_2705(
        tmp_path, monkeypatch, run_cli, fake_processes):
    past_the_guards(monkeypatch)
    monkeypatch.setenv("REVISE_BUDGET", "three")
    calls = fake_processes()
    run_conductor = importlib.import_module("veri.run_conductor")

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    lines = stderr.splitlines()
    assert (code, len(lines), "REVISE_BUDGET" in stderr, calls) == (2, 1, True, []), stderr


def test_cli_a_revise_budget_that_is_not_a_whole_number_refuses_before_the_bash_version_probe_with_veri_bash_major_unset_2705(
        tmp_path, monkeypatch, run_cli, fake_processes):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_BASH_MAJOR", raising=False)
    monkeypatch.setenv("REVISE_BUDGET", "three")
    calls = fake_processes()
    run_conductor = importlib.import_module("veri.run_conductor")

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (code, "REVISE_BUDGET" in stderr, calls) == (2, True, []), stderr


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

    patch_process_boundary(monkeypatch, answer, lambda _name, *args, **kwargs: answer(*args, **kwargs))
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

    patch_process_boundary(
        monkeypatch,
        {"run": answer, "call": lambda *a, **k: answer(*a, **k).returncode,
         "check_call": lambda *a, **k: answer(*a, **k).returncode, "check_output": check_output, "Popen": popen},
        lambda _name, *args, **__: calls.append(list(args)))
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

    patch_process_boundary(
        monkeypatch,
        {"run": answer, "call": lambda *a, **k: answer(*a, **k).returncode,
         "check_call": lambda *a, **k: answer(*a, **k).returncode, "check_output": check_output, "Popen": popen},
        lambda _name, *args, **__: calls.append(list(args)))
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
        "fresh": (".gitignore\nissue-*-skill-commit\nissue-*-conductor-model\n", commit + "\n", [], None, False),
        "own-gitignore": ("mine\n", commit + "\n", [], None, False),
        "abbreviation": (".gitignore\nissue-*-skill-commit\nissue-*-conductor-model\n", "1111111\n\n", ["1111111^{commit}"], [], False),
        "ref-name": (".gitignore\nissue-*-skill-commit\nissue-*-conductor-model\n", "main\n", ["main^{commit}"], [], False),
        "foreign": (2, b"", [refusal % "2222222"], "2222222\n"),
        "directory": (2, b"", [refusal % ""], None),
    }


def test_main_on_a_fresh_run_runs_update_veri_before_resolving_the_pin_so_the_recorded_commit_is_the_updated_one(
        tmp_path, monkeypatch, capfdbinary):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    old, new = "1" * 40, "2" * 40
    updated = []

    def answer(args, *_, **kwargs):
        args = list(args)
        code, out = 0, ""
        if any("update-veri" in str(arg) for arg in args):
            updated.append(args)
            code = 0
        elif args[:1] == ["git"] and args[3:] == ["remote", "get-url", "origin"]:
            code = 2
        elif args[:1] == ["git"] and args[3:4] == ["rev-parse"]:
            code, out = (0, (new if updated else old) + "\n") if args[4:] == ["HEAD"] else (128, "")
        elif args[:1] == ["git"] and "for-each-ref" in args:
            out = "refs/heads/tdd/4242-run\n"
        if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
            out = out.encode()
        return subprocess.CompletedProcess(args, code, out, b"" if not kwargs.get("text") else "")

    def check_output(args, *a, **kwargs):
        done = answer(args, *a, **kwargs)
        if done.returncode:
            raise subprocess.CalledProcessError(done.returncode, done.args, done.stdout, done.stderr)
        return done.stdout

    def popen(args, *_, **__):
        return FakeProcess(list(args))

    patch_process_boundary(
        monkeypatch,
        {"run": answer, "call": lambda *a, **k: answer(*a, **k).returncode,
         "check_call": lambda *a, **k: answer(*a, **k).returncode, "check_output": check_output, "Popen": popen},
        lambda _name, *args, **__: updated.append(list(args)) if any("update-veri" in str(a) for a in args) else None)
    monkeypatch.chdir(tmp_path)
    run_conductor = importlib.import_module("veri.run_conductor")
    run_conductor.main(["4242"])
    capfdbinary.readouterr()
    assert (tmp_path / ".tdd" / "issue-4242-skill-commit").read_text() == new + "\n"


@pytest.mark.parametrize("update_code", [1, 2, 3])
def test_main_on_a_fresh_run_whose_update_veri_exits_non_zero_still_pins_the_unupdated_commit_and_launches_the_conductor(
        update_code, tmp_path, monkeypatch, capfdbinary):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    monkeypatch.chdir(tmp_path)
    old = "1" * 40
    calls = fake_pin(monkeypatch, old, set())
    snapshots, launches = fake_snapshot(monkeypatch, calls, 0, 0)
    run, updated = subprocess.run, []

    def update_fails(args, *a, **kwargs):
        if any("update-veri" in str(word) for word in args):
            updated.append(list(args))
            return subprocess.CompletedProcess(list(args), update_code, b"", b"")
        return run(args, *a, **kwargs)

    monkeypatch.setattr(subprocess, "run", update_fails)
    run_conductor = importlib.import_module("veri.run_conductor")
    code = run_conductor.main(["4242"])
    capfdbinary.readouterr()
    assert (code, (tmp_path / ".tdd" / "issue-4242-skill-commit").read_text(), len(updated), len(launches)) == (
        0, old + "\n", 1, 1)


def test_main_on_a_resume_with_a_readable_skill_commit_record_never_runs_update_veri(
        tmp_path, monkeypatch, capfdbinary):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-4242-skill-commit").write_text("1" * 40 + "\n")
    calls = fake_pin(monkeypatch, "1" * 40, {"1" * 40 + "^{commit}"})
    run_conductor = importlib.import_module("veri.run_conductor")
    run_conductor.main(["4242"])
    capfdbinary.readouterr()
    assert [call for call in calls if any("update-veri" in str(word) for word in call)] == []


def test_main_run_from_a_subdirectory_of_the_repo_makes_the_run_state_at_the_repo_root_and_leaves_no_tdd_in_the_subdirectory_1895(
        tmp_path, monkeypatch, capfdbinary):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    sub = root / "skills"
    sub.mkdir()
    monkeypatch.chdir(sub)
    commit = "1111111111111111111111111111111111111111"
    fake_pin(monkeypatch, commit, {commit + "^{commit}"})
    run_conductor = importlib.import_module("veri.run_conductor")

    run_conductor.main(["4242"])

    seed = root / ".tdd" / ".gitignore"
    assert (seed.read_text() if seed.is_file() else None, (sub / ".tdd").exists()) == (
        ".gitignore\nissue-*-skill-commit\nissue-*-conductor-model\n", False)


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
        "first-launch": (commit + "\n", True, [], [], 0),
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

    patch_process_boundary(
        monkeypatch,
        {"run": answer, "call": lambda *a, **k: answer(*a, **k).returncode,
         "check_call": lambda *a, **k: answer(*a, **k).returncode, "Popen": popen},
        lambda _name, *args, **__: launches.append(list(args)))
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

    real_check_output = subprocess.check_output

    def check_output(args, *a, **kwargs):
        if list(args)[:1] == ["git"]:
            return real_check_output(args, *a, **kwargs)
        launched(list(args), kwargs)
        return b""

    patch_process_boundary(
        monkeypatch,
        {"run": answer, "call": lambda *a, **k: answer(*a, **k).returncode,
         "check_call": lambda *a, **k: answer(*a, **k).returncode, "check_output": check_output, "Popen": popen},
        lambda _name, *args, **__: launches.append({"os": _name, "args": args}),
        extra_os=("setsid", "setpgid"))
    return launches


def runs_update_veri(argv):
    return any(os.path.basename(str(word)) == "update-veri.sh" for word in argv)


def without_update_veri(launches):
    return [launch for launch in launches if not runs_update_veri(launch.get("argv", []))]


def after_update_veri(launches):
    """The launches past the one update-veri.sh, which a fresh run makes first of all."""
    assert [i for i, launch in enumerate(launches) if runs_update_veri(launch.get("argv", []))] == [0], launches
    return launches[1:]


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
    launches = after_update_veri(launches)
    assert code == 0
    observed = [{key: value for key, value in dict(launch, argv=launch["argv"][:1] + launch["argv"][-4:],
                                                   stdin=b"# the procedure, read from SKILL.md" in launch.get("stdin", b"")).items()
                 if key != "preexec_fn"}
                for launch in launches]
    assert observed == [{"argv": [program, "--permission-mode", "bypassPermissions", "--model", "opus"],
                         "stdin": True, "stdout": None, "stderr": None, "capture_output": False,
                         "start_new_session": False, "process_group": None}]


def test_main_with_no_model_variable_set_launches_claude_with_model_opus(tmp_path, monkeypatch, capfdbinary):
    import importlib.util
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.setenv("CLAUDE_BIN", "fake-claude")
    for name in ("VERI_NEW_SKILL", "VERI_MODEL", "VERI_MODEL_DEVELOPER", "VERI_MODEL_VERIFIER", "VERI_MODEL_REVISE"):
        monkeypatch.delenv(name, raising=False)
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
    (skill / "SKILL.md").write_text("# the procedure, read from SKILL.md\n")
    spec = importlib.util.spec_from_file_location("run_conductor_model", str(skill / "scripts" / "veri" / "run_conductor.py"))
    run_conductor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_conductor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    launches = fake_claude_launch(monkeypatch)

    code = run_conductor.main(["4242"])

    capfdbinary.readouterr()
    launches = after_update_veri(launches)
    assert code == 0
    assert len(launches) == 1
    argv = launches[0]["argv"]
    assert [argv[i + 1] for i, word in enumerate(argv[:-1]) if word == "--model"] == ["opus"]


def test_main_with_veri_model_conductor_set_to_a_value_launches_claude_with_that_model(tmp_path, monkeypatch, capfdbinary):
    import importlib.util
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.setenv("CLAUDE_BIN", "fake-claude")
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.setenv("VERI_MODEL_CONDUCTOR", "sonnet")
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
    (skill / "SKILL.md").write_text("# the procedure, read from SKILL.md\n")
    spec = importlib.util.spec_from_file_location("run_conductor_conductor_model", str(skill / "scripts" / "veri" / "run_conductor.py"))
    run_conductor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_conductor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    launches = fake_claude_launch(monkeypatch)

    code = run_conductor.main(["4242"])

    capfdbinary.readouterr()
    launches = after_update_veri(launches)
    assert code == 0
    assert len(launches) == 1
    argv = launches[0]["argv"]
    assert [argv[i + 1] for i, word in enumerate(argv[:-1]) if word == "--model"] == ["sonnet"]


def test_main_with_veri_model_conductor_set_but_empty_launches_claude_with_model_opus(tmp_path, monkeypatch, capfdbinary):
    import importlib.util
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.setenv("CLAUDE_BIN", "fake-claude")
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.setenv("VERI_MODEL_CONDUCTOR", "")
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
    (skill / "SKILL.md").write_text("# the procedure, read from SKILL.md\n")
    spec = importlib.util.spec_from_file_location("run_conductor_empty_conductor_model", str(skill / "scripts" / "veri" / "run_conductor.py"))
    run_conductor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_conductor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    launches = fake_claude_launch(monkeypatch)

    code = run_conductor.main(["4242"])

    capfdbinary.readouterr()
    launches = after_update_veri(launches)
    assert code == 0
    assert len(launches) == 1
    argv = launches[0]["argv"]
    assert [argv[i + 1] for i, word in enumerate(argv[:-1]) if word == "--model"] == ["opus"]


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
    recorded = "".join(f.read_text() for f in sorted((unpinned / ".tdd").glob("*")) if f.is_file())
    answers["unpinned"] = ([launch["stdin"] for launch in after_update_veri(launches)],
                           (str(scratch / "veri-run-abc-") in recorded, str(os.getpid()) in recorded))

    pinned = tmp_path / "pinned"
    pinned.mkdir()
    monkeypatch.chdir(pinned)
    calls = fake_pin(monkeypatch, commit, set())
    fake_snapshot(monkeypatch, calls, 0, 0)
    popen, run, stdins, snapshots, updates = subprocess.Popen, subprocess.run, [], [], []

    def tar_extracts_a_skill_md_with_trailing_newlines(args, *a, **kwargs):
        process = popen(args, *a, **kwargs)
        if list(args)[:1] == ["tar"]:
            snapshots.append(args[-1])
            pathlib.Path(args[-1], "SKILL.md").write_text("# the committed procedure\n\n")
        return process

    check_output = subprocess.check_output

    def update_noted(args, *a, **kwargs):
        if runs_update_veri(args):
            updates.append(len(snapshots))
        return check_output(args, *a, **kwargs)

    def claude_reads_stdin(args, *a, **kwargs):
        if runs_update_veri(args):
            updates.append(len(snapshots))
        if list(args)[:1] == ["fake-claude"]:
            data = kwargs.get("input")
            stdins.append(data.encode() if isinstance(data, str) else (data or b""))
        return run(args, *a, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", tar_extracts_a_skill_md_with_trailing_newlines)
    monkeypatch.setattr(subprocess, "run", claude_reads_stdin)
    monkeypatch.setattr(subprocess, "check_output", update_noted)
    codes.append(run_conductor.main(["abc", "extra"]))
    capfdbinary.readouterr()
    answers["pinned"] = (stdins, (pinned / ".tdd" / "issue-abc-skill-commit").read_text())

    assert (len(snapshots), codes, updates) == (1, [0, 0], [0])
    assert answers == {
        "unpinned": ([("# the procedure\n\nlast line"
                       "\n\nBase directory for this skill: %s\n"
                       "\nSolve issue #abc by the procedure above.\n" % skill).encode()], (True, True)),
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
        if list(args)[:1] != ["git"] and not runs_update_veri(args):
            environments.append((kwargs.get("env") or os.environ).get("CLAUDE_BIN"))
        return run(args, *a, **kwargs)

    monkeypatch.setattr(subprocess, "run", claude_records_its_environment)

    code = run_conductor.main(["4242"])

    capfdbinary.readouterr()
    assert (code, [launch["argv"][0] for launch in after_update_veri(launches)], environments) == (0, [stub], [stub])


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
            "argvs": [args[:1] + args[-4:] for args, _ in launches],
            "issue in prompt": [b"Solve issue #4242 by the procedure above." in stdin for _, stdin in launches],
            "orchestrate.sh adds": sorted({added for _, stdin in launches
                                           for added in ("orchestrate.sh", "VERI_CONDUCTOR_CTX_BUDGET", ".tdd/parked/")
                                           if added.encode() in stdin}),
            "parked": (cwd / ".tdd" / "parked").exists(),
        }
    claude = ["fake-claude", "--permission-mode", "bypassPermissions", "--model", "opus"]
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


def test_main_conductor_launch_limits_what_the_harness_loads_beside_its_permission_mode_and_model_1705(
        tmp_path, monkeypatch, capfdbinary):
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_MODEL", "VERI_MODEL_DEVELOPER", "VERI_MODEL_VERIFIER", "VERI_MODEL_REVISE"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CLAUDE_BIN", "fake-claude")
    scratch_tmpdir(tmp_path, monkeypatch)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_claude_exiting(monkeypatch, 0, 0)

    code = run_conductor.main(["4242"])

    capfdbinary.readouterr()
    assert code == 0
    argv = launches[0][0]
    value = lambda flag: argv[argv.index(flag) + 1] if flag in argv else "null"
    assert (argv[-4:], "--disable-slash-commands" in argv, "--strict-mcp-config" in argv,
            json.loads(value("--mcp-config")), json.loads(value("--settings")), "--bare" in argv) == (
        ["--permission-mode", "bypassPermissions", "--model", "opus"], True, True, {"mcpServers": {}},
        {"autoMemoryEnabled": False,
         "claudeMdExcludes": [os.path.join(os.path.expanduser("~"), ".claude", "CLAUDE.md")]}, False)


def test_main_a_conductor_launch_does_not_request_the_five_minute_cache_ttl_so_its_writes_stay_one_hour_1707(
        tmp_path, monkeypatch, capfdbinary):
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "FORCE_PROMPT_CACHING_5M"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CLAUDE_BIN", "fake-claude")
    scratch_tmpdir(tmp_path, monkeypatch)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    run_conductor = importlib.import_module("veri.run_conductor")
    run, writes = subprocess.run, []

    def claude_reports_its_cache_writes(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        five = (kwargs.get("env") or os.environ).get("FORCE_PROMPT_CACHING_5M") == "1"
        writes.append("ephemeral_5m_input_tokens" if five else "ephemeral_1h_input_tokens")
        return subprocess.CompletedProcess(args, 0, None, None)

    fake_claude_exiting(monkeypatch, 0, 0)
    fake = subprocess.run
    monkeypatch.setattr(subprocess, "run", lambda args, *a, **kw: claude_reports_its_cache_writes(args, *a, **kw)
                        if list(args)[:1] == ["fake-claude"] else fake(args, *a, **kw))

    code = run_conductor.main(["4242"])

    capfdbinary.readouterr()
    assert (code, writes) == (0, ["ephemeral_1h_input_tokens"])


def test_main_a_conductor_launch_pins_claudes_shell_to_the_bash_on_path_under_a_zsh_login_shell_2204(
        tmp_path, monkeypatch, capfdbinary):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.setenv("SHELL", "/bin/zsh")
    monkeypatch.delenv("CLAUDE_CODE_SHELL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    run_conductor = importlib.import_module("veri.run_conductor")
    shells = []
    run = subprocess.run

    def claude_reports_its_shell(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        env = kwargs.get("env") or os.environ
        shells.append((env.get("SHELL"), env.get("CLAUDE_CODE_SHELL")))
        return subprocess.CompletedProcess(args, 0, None, None)

    fake_claude_exiting(monkeypatch, 0, 0)
    fake = subprocess.run
    monkeypatch.setattr(subprocess, "run", lambda args, *a, **kw: claude_reports_its_shell(args, *a, **kw)
                        if list(args)[:1] == ["fake-claude"] else fake(args, *a, **kw))
    bash = shutil.which("bash")

    code = run_conductor.main(["4242"])

    capfdbinary.readouterr()
    assert (code, shells) == (0, [(bash, bash)])


def test_main_a_parent_environment_asking_for_the_five_minute_cache_ttl_reaches_the_leaf_but_not_the_conductor_1738(
        tmp_path, monkeypatch, capfdbinary):
    from test_run_leaf import _FakeLeaf
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.setenv("FORCE_PROMPT_CACHING_5M", "1")
    monkeypatch.setenv("CLAUDE_BIN", "fake-claude")
    scratch_tmpdir(tmp_path, monkeypatch)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    run_conductor = importlib.import_module("veri.run_conductor")
    run_leaf = importlib.import_module("veri.run_leaf")
    seen = {"conductor": [], "leaf": []}
    fake_claude_exiting(monkeypatch, 0, 0)
    answer = subprocess.run

    def conductor_run(args, *a, **kwargs):
        if list(args)[:1] == ["fake-claude"]:
            seen["conductor"].append(kwargs["env"].get("FORCE_PROMPT_CACHING_5M"))
        return answer(args, *a, **kwargs)

    monkeypatch.setattr(subprocess, "run", conductor_run)

    conductor_code = run_conductor.main(["4242"])
    capfdbinary.readouterr()

    (cwd / "prompt.txt").write_text("do the step\n")

    def leaf_popen(argv, *a, **kwargs):
        seen["leaf"].append(kwargs["env"].get("FORCE_PROMPT_CACHING_5M"))
        return _FakeLeaf([], argv, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", leaf_popen)
    leaf_code = run_leaf.main(["prompt.txt"])
    capfdbinary.readouterr()

    assert (conductor_code, leaf_code, seen) == (0, 0, {"conductor": [None], "leaf": ["1"]})


def stream_of_what_the_real_claude_loads(argv, home, repo):
    """A stream shaped by the 2026-10-18 observation of the real binary under each flag."""
    flag = lambda name: argv[argv.index(name) + 1] if name in argv else None
    if "--bare" in argv:
        return [{"type": "result", "subtype": "error", "is_error": True, "result": "Not logged in"}]
    settings = json.loads(flag("--settings") or "{}")
    excluded = settings.get("claudeMdExcludes", [])
    servers = ["claude.ai Gmail", "claude.ai Slack", "claude.ai ClickUp"]
    if "--strict-mcp-config" in argv:
        servers = list(json.loads(flag("--mcp-config") or "{}").get("mcpServers", {}))
    docs = [str(home / ".claude" / "CLAUDE.md"), str(repo / "CLAUDE.md")]
    if settings.get("autoMemoryEnabled", True):
        docs.append(str(home / ".claude" / "projects" / "MEMORY.md"))
    loaded = [path for path in docs if path not in excluded]
    skills = [] if "--disable-slash-commands" in argv else ["tdd", "merge"]
    return [{"type": "system", "subtype": "init", "mcp_servers": servers, "skills": skills},
            *({"type": "attachment", "path": path} for path in loaded),
            {"type": "result", "subtype": "success", "is_error": False, "result": "ok"}]


def test_main_a_conductor_session_loads_no_skills_connectors_memory_or_user_claude_md_but_logs_in_and_reads_the_repos_claude_md_1705(
        tmp_path, monkeypatch, capfdbinary):
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_MODEL", "VERI_MODEL_DEVELOPER", "VERI_MODEL_VERIFIER", "VERI_MODEL_REVISE"):
        monkeypatch.delenv(name, raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    home = pathlib.Path(os.path.expanduser("~"))
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_claude_exiting(monkeypatch, 0, 0)
    answer = subprocess.run

    def streaming(args, *rest, **kwargs):
        if list(args)[:1] == ["fake-claude"]:
            stream = "".join(json.dumps(r) + "\n" for r in stream_of_what_the_real_claude_loads(list(args), home, cwd))
            os.write(1, stream.encode())
        return answer(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", streaming)

    code = run_conductor.main(["4242"])
    records = [json.loads(line) for line in capfdbinary.readouterr().out.decode().splitlines() if line.startswith("{")]

    init = next(r for r in records if r.get("subtype") == "init")
    assert (code, init["skills"], init["mcp_servers"],
            [r["path"] for r in records if r["type"] == "attachment"],
            [r["is_error"] for r in records if r["type"] == "result"]) == (
        0, [], [], [str(cwd / "CLAUDE.md")], [False])


REAL_RUN, REAL_POPEN = subprocess.run, subprocess.Popen


def fake_claude_env(monkeypatch, origin, resolves, leaf):
    """git faked as a process: origin and its fetch present when `origin`, its HEAD and the clone's resolving when
    `resolves`; tar dropping the real SKILL.md into its -C directory; fake-claude
    recorded with its environment, and, given a `leaf` directory, detaching a real develop-red leaf there through
    supervise.sh and run-leaf.sh from that environment with a stub claude writing the VERI_GH_DRIVER it saw."""
    launches = []

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
                waited = REAL_RUN([str(SCRIPTS / "wait-leaf.sh"), "develop-red", "27"], cwd=leaf, env=leaf_env,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if waited.returncode != 0:
                    pytest.fail(f"the develop-red leaf did not finish (wait-leaf.sh exit {waited.returncode})")
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
    return launches


HANDLES = {"CLAUDECODE": "1", "CLAUDE_CODE_SESSION_ID": "parent-session",
           "CLAUDE_CODE_HOST_SESSION_ID": "parent-host-session", "CLAUDE_CODE_MESSAGING_SOCKET": "/tmp/parent.sock",
           "CLAUDE_CODE_MESSAGING_TOKEN": "parent-token", "CLAUDE_PID": "4141", "CLAUDE_CODE_CHILD_SESSION": "1",
           "CLAUDE_CODE_ENTRYPOINT": "cli"}


@pytest.mark.process("a leaf detached through detach-leaf.sh, supervise.sh and run-leaf.sh from the conductor's environment")
def test_cli_hands_claude_an_environment_without_the_session_handles_or_any_value_carrying_the_session_id_with_veri_variables_and_veri_gh_driver_through_to_a_detached_leaf_no_veri_new_skill_on_a_repin_and_the_pinned_clone_and_ref_only_when_pinned(
        tmp_path, monkeypatch, run_cli, events):
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
        launches = fake_claude_env(monkeypatch, origin, resolves, leaf)
        code, _, _ = run_cli(run_conductor, ["4242"], env=env, cwd=cwd)
        answers[name] = {
            "code": code,
            "seen": [{var: seen[var] for var in watched if var in seen} for seen in launches],
            "repins": [record["event"] for record in events.records(cwd / ".tdd" / "wt" / "4242")],
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


def test_cli_a_frontmatter_fenced_procedure_launches_exits_0_and_reaches_the_binary_whole(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_claude_exiting(monkeypatch, 0, 0)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    procedure = (SCRIPTS.parent / "SKILL.md").read_bytes().rstrip(b"\n")

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, [(stdin.split(b"\n", 1)[0], stdin.startswith(procedure)) for _, stdin in launches]) == (
        0, [(b"---", True)])



def test_cli_a_launch_hands_the_conductor_a_fresh_veri_run_n_directory_inside_the_inherited_tmpdir_and_records_it_with_the_launchers_pid_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, 0, 0)
    answer, seen = subprocess.run, []

    def reporting(args, *rest, **kwargs):
        if list(args)[:1] == ["fake-claude"]:
            seen.append(kwargs["env"]["TMPDIR"])
        return answer(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", reporting)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    handed = pathlib.Path(seen[0]) if seen else None
    recorded = "".join(f.read_text() for f in sorted((cwd / ".tdd").glob("*")) if f.is_file())
    assert (code, handed is not None and handed.parent == scratch and handed.name.startswith("veri-run-4242-"),
            handed is not None and str(handed) in recorded and str(os.getpid()) in recorded) == (0, True, True)


@pytest.mark.parametrize("conductor_code", [0, 1])
def test_cli_a_folder_the_conductor_leaks_into_its_tmpdir_is_gone_from_the_inherited_tmpdir_when_it_exits_and_the_launchers_code_is_the_conductors_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli, conductor_code):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, conductor_code, 0)
    answer = subprocess.run

    def leaking(args, *rest, **kwargs):
        if list(args)[:1] == ["fake-claude"]:
            (pathlib.Path(kwargs["env"]["TMPDIR"]) / "cdk.outAbC123").mkdir()
        return answer(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", leaking)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, sorted(p.name for p in scratch.iterdir())) == (conductor_code, [])


def test_cli_a_folder_the_conductor_leaks_into_its_tmpdir_is_gone_from_the_inherited_tmpdir_when_the_launcher_is_sent_sigterm_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, 0, 0)
    answer = subprocess.run

    def leaking_then_terminated(args, *rest, **kwargs):
        if list(args)[:1] == ["fake-claude"]:
            (pathlib.Path(kwargs["env"]["TMPDIR"]) / "cdk.outAbC123").mkdir()
            os.kill(os.getpid(), signal.SIGTERM)
        return answer(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", leaking_then_terminated)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, sorted(p.name for p in scratch.iterdir())) == (128 + signal.SIGTERM, [])


@pytest.mark.parametrize("sig", [signal.SIGINT, signal.SIGHUP])
def test_cli_a_folder_the_conductor_leaks_into_its_tmpdir_is_gone_from_the_inherited_tmpdir_when_the_launcher_is_sent_sigint_or_sighup_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli, sig):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, 0, 0)
    answer = subprocess.run

    def leaking_then_signalled(args, *rest, **kwargs):
        if list(args)[:1] == ["fake-claude"]:
            (pathlib.Path(kwargs["env"]["TMPDIR"]) / "cdk.outAbC123").mkdir()
            os.kill(os.getpid(), sig)
        return answer(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", leaking_then_signalled)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    run_cli(run_conductor, ["4242"], cwd=cwd)

    assert sorted(p.name for p in scratch.iterdir()) == []


def test_cli_a_launch_whose_run_has_no_tdd_directory_yet_still_records_the_veri_run_n_directory_and_the_launchers_pid_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, 0, 0)
    answer, seen = subprocess.run, []

    def reporting(args, *rest, **kwargs):
        if list(args)[:1] == ["fake-claude"]:
            seen.append(kwargs["env"]["TMPDIR"])
        return answer(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", reporting)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    assert not (cwd / ".tdd").exists()

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    recorded = "".join(f.read_text() for f in sorted((cwd / ".tdd").glob("*")) if f.is_file())
    assert (code, bool(seen) and seen[0] in recorded, str(os.getpid()) in recorded) == (0, True, True)


def test_cli_a_launch_whose_run_worktree_does_not_exist_yet_records_the_conductors_pid_in_its_conductor_pid_file_issue_2390(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, 0, 0)
    answer, seen, asked = subprocess.run, [], []
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    pid_file = cwd / ".tdd" / "wt" / "4242" / ".tdd" / "conductor.pid"

    def running_the_child_setup(args, *rest, **kwargs):
        if list(args)[:1] == ["ps"] and "lstart=" in list(args):
            asked.append(list(args)[-1])
            return subprocess.CompletedProcess(args, 0, stdout="Tue Oct 27 13:40:12 2026\n", stderr="")
        if list(args)[:1] == ["fake-claude"]:
            if kwargs.get("preexec_fn") is not None:
                kwargs["preexec_fn"]()
            seen.append(pid_file.read_text() if pid_file.is_file() else None)
        return answer(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", running_the_child_setup)
    assert not (cwd / ".tdd" / "wt" / "4242").exists()

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, seen, asked) == (0, ["%d\nTue Oct 27 13:40:12 2026\n" % os.getpid()], [str(os.getpid())])


def test_cli_a_launch_records_the_conductors_ps_start_time_on_the_second_line_of_its_conductor_pid_file_issue_2537(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, 0, 0)
    answer, seen, asked = subprocess.run, [], []
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    pid_file = cwd / ".tdd" / "wt" / "4242" / ".tdd" / "conductor.pid"

    def running_the_child_setup(args, *rest, **kwargs):
        if list(args)[:1] == ["ps"] and "lstart=" in list(args):
            asked.append(list(args)[-1])
            return subprocess.CompletedProcess(args, 0, stdout="Tue Oct 27 13:40:12 2026\n", stderr="")
        if list(args)[:1] == ["fake-claude"]:
            if kwargs.get("preexec_fn") is not None:
                kwargs["preexec_fn"]()
            seen.append(pid_file.read_text() if pid_file.is_file() else None)
        return answer(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", running_the_child_setup)

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, seen, asked) == (0, ["%d\nTue Oct 27 13:40:12 2026\n" % os.getpid()], [str(os.getpid())])


def test_cli_a_run_that_ends_leaves_no_conductor_pid_file_for_its_worktree_issue_2537(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, 0, 0)
    answer, seen = subprocess.run, []
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    pid_file = cwd / ".tdd" / "wt" / "4242" / ".tdd" / "conductor.pid"

    def running_the_child_setup(args, *rest, **kwargs):
        if list(args)[:1] == ["ps"] and "lstart=" in list(args):
            return subprocess.CompletedProcess(args, 0, stdout="Tue Oct 27 13:40:12 2026\n", stderr="")
        if list(args)[:1] == ["fake-claude"]:
            if kwargs.get("preexec_fn") is not None:
                kwargs["preexec_fn"]()
            seen.append(pid_file.is_file())
        return answer(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", running_the_child_setup)

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, seen, pid_file.exists()) == (0, [True], False)


def test_cli_an_unpinned_launch_whose_run_has_no_tdd_directory_yet_still_records_the_veri_run_n_directory_and_the_launchers_pid_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_unresolvable(monkeypatch)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    recorded = "".join(f.read_text() for f in sorted((cwd / ".tdd").glob("*")) if f.is_file())
    assert (code, [l["VERI_SKILL_UNPINNED"] for l in launches],
            str(scratch / "veri-run-4242-") in recorded, str(os.getpid()) in recorded) == (0, ["1"], True, True)


def test_cli_a_launch_removes_every_recorded_veri_run_directory_whose_recorded_pid_is_dead_and_keeps_one_whose_pid_is_alive_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, 0, 0)
    cwd = tmp_path / "cwd"
    (cwd / ".tdd").mkdir(parents=True)
    for issue, name, pid in (("77", "veri-run-77-dead", 2**31 - 2), ("88", "veri-run-88-live", os.getpid())):
        (scratch / name / "cdk.outAbC123").mkdir(parents=True)
        (cwd / ".tdd" / ("issue-%s-tmpdir-skill-commit" % issue)).write_text("%s %d\n" % (scratch / name, pid))

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, sorted(p.name for p in scratch.iterdir())) == (0, ["veri-run-88-live"])


def test_cli_a_launch_keeps_a_veri_run_directory_whose_record_it_cannot_read_and_names_the_record_on_stderr_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, 0, 0)
    cwd = tmp_path / "cwd"
    (cwd / ".tdd").mkdir(parents=True)
    (scratch / "veri-run-77-torn" / "cdk.outAbC123").mkdir(parents=True)
    record = cwd / ".tdd" / "issue-77-tmpdir-skill-commit"
    record.write_text("%s not-a-pid\n" % (scratch / "veri-run-77-torn"))

    code, _, err = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, (scratch / "veri-run-77-torn" / "cdk.outAbC123").is_dir(), record.name in err) == (0, True, True)


def test_cli_a_launch_keeps_a_directory_outside_the_inherited_tmpdir_that_a_dead_pid_record_names_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, 0, 0)
    cwd = tmp_path / "cwd"
    (cwd / ".tdd").mkdir(parents=True)
    elsewhere = tmp_path / "elsewhere" / "veri-run-77-dead"
    (elsewhere / "precious").mkdir(parents=True)
    (cwd / ".tdd" / "issue-77-tmpdir-skill-commit").write_text("%s %d\n" % (elsewhere, 2**31 - 2))

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, (elsewhere / "precious").is_dir()) == (0, True)


def test_cli_a_launch_keeps_a_directory_inside_the_inherited_tmpdir_not_named_veri_run_that_a_dead_pid_record_names_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, 0, 0)
    cwd = tmp_path / "cwd"
    (cwd / ".tdd").mkdir(parents=True)
    (scratch / "cdk.outXyz" / "precious").mkdir(parents=True)
    (cwd / ".tdd" / "issue-77-tmpdir-skill-commit").write_text("%s %d\n" % (scratch / "cdk.outXyz", 2**31 - 2))

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, (scratch / "cdk.outXyz" / "precious").is_dir()) == (0, True)


def test_cli_a_launch_keeps_a_record_and_its_directory_whose_pid_answers_permission_denied_and_goes_on_under_tdd_issue_2447(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, 0, 0)
    foreign = 2**31 - 3
    real_kill = os.kill

    def kill(pid, sig):
        if pid == foreign:
            raise PermissionError(1, "Operation not permitted")
        return real_kill(pid, sig)
    monkeypatch.setattr(os, "kill", kill)
    cwd = tmp_path / "cwd"
    (cwd / ".tdd").mkdir(parents=True)
    (scratch / "veri-run-77-foreign" / "cdk.outAbC123").mkdir(parents=True)
    record = cwd / ".tdd" / "issue-77-tmpdir-skill-commit"
    record.write_text("%s %d\n" % (scratch / "veri-run-77-foreign", foreign))

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, record.is_file(), (scratch / "veri-run-77-foreign" / "cdk.outAbC123").is_dir()) == (0, True, True)


def test_cli_a_launch_still_removes_a_directory_whose_recorded_pid_answers_no_such_process_under_tdd_issue_2447(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, 0, 0)
    gone = 2**31 - 4
    real_kill = os.kill

    def kill(pid, sig):
        if pid == gone:
            raise ProcessLookupError(3, "No such process")
        return real_kill(pid, sig)
    monkeypatch.setattr(os, "kill", kill)
    cwd = tmp_path / "cwd"
    (cwd / ".tdd").mkdir(parents=True)
    (scratch / "veri-run-78-gone" / "cdk.outAbC123").mkdir(parents=True)
    record = cwd / ".tdd" / "issue-78-tmpdir-skill-commit"
    record.write_text("%s %d\n" % (scratch / "veri-run-78-gone", gone))

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, (scratch / "veri-run-78-gone").exists()) == (0, False)


def test_cli_a_launch_whose_inherited_tmpdir_filesystem_has_less_than_the_default_20_gb_free_exits_2_naming_the_path_the_free_gb_and_veri_min_free_gb_and_launches_no_conductor_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.delenv("VERI_MIN_FREE_GB", raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_claude_exiting(monkeypatch, 0, 0)
    monkeypatch.setattr(run_conductor, "free_gb",
                        lambda path: 3 if os.path.realpath(path) == os.path.realpath(scratch) else 500,
                        raising=False)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, err = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, launches, str(scratch) in err and "3" in err and "VERI_MIN_FREE_GB" in err) == (2, [], True)


def test_cli_a_launch_whose_target_repository_filesystem_has_less_than_veri_min_free_gb_free_while_the_inherited_tmpdir_has_plenty_exits_2_naming_the_repository_path_the_free_gb_and_veri_min_free_gb_and_launches_no_conductor_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.delenv("VERI_MIN_FREE_GB", raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_claude_exiting(monkeypatch, 0, 0)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.setattr(run_conductor, "free_gb",
                        lambda path: 7 if os.path.realpath(path) == os.path.realpath(cwd) else 500,
                        raising=False)

    code, _, err = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, launches, str(cwd) in err and "7" in err and "VERI_MIN_FREE_GB" in err) == (2, [], True)


def test_cli_a_launch_whose_pinned_slash_tmp_filesystem_has_less_than_veri_min_free_gb_free_while_the_inherited_tmpdir_has_plenty_exits_2_naming_slash_tmp_and_launches_no_conductor_under_tdd_issue_2422(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.delenv("VERI_MIN_FREE_GB", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_claude_exiting(monkeypatch, 0, 0)
    monkeypatch.setattr(run_conductor, "free_gb",
                        lambda path: 4 if os.path.realpath(path) == os.path.realpath("/tmp") else 500,
                        raising=False)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, err = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, launches, "'/tmp' has 4 GB free" in err and "VERI_MIN_FREE_GB" in err) == (2, [], True)


def test_cli_a_veri_min_free_gb_that_is_not_a_whole_number_at_least_0_exits_2_naming_veri_min_free_gb_and_launches_no_conductor_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_claude_exiting(monkeypatch, 0, 0)
    monkeypatch.setattr(run_conductor, "free_gb", lambda path: 500, raising=False)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    outcomes = {}
    for bad in ("", "abc", "-1", "1.5"):
        monkeypatch.setenv("VERI_MIN_FREE_GB", bad)
        try:
            code, _, err = run_cli(run_conductor, ["4242"], cwd=cwd)
        except ValueError:
            code, err = "crashed", ""
        outcomes[bad] = (code, "VERI_MIN_FREE_GB" in err)

    assert (outcomes, launches) == ({bad: (2, True) for bad in ("", "abc", "-1", "1.5")}, [])


def test_cli_a_launch_whose_inherited_tmpdir_filesystem_has_3_gb_free_launches_the_conductor_when_veri_min_free_gb_is_0_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.setenv("VERI_MIN_FREE_GB", "0")
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_claude_exiting(monkeypatch, 0, 0)
    monkeypatch.setattr(run_conductor, "free_gb",
                        lambda path: 3 if os.path.realpath(path) == os.path.realpath(scratch) else 500,
                        raising=False)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, len(launches)) == (0, 1)


def test_cli_a_launch_whose_filesystems_have_19_gb_free_exits_2_and_launches_no_conductor_when_veri_min_free_gb_is_unset_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.delenv("VERI_MIN_FREE_GB", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_claude_exiting(monkeypatch, 0, 0)
    monkeypatch.setattr(run_conductor, "free_gb", lambda path: 19, raising=False)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, err = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, launches, "VERI_MIN_FREE_GB=20" in err) == (2, [], True)


def test_cli_a_launch_whose_filesystems_have_20_gb_free_launches_the_conductor_when_veri_min_free_gb_is_unset_under_tdd_issue_2183(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.delenv("VERI_MIN_FREE_GB", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_claude_exiting(monkeypatch, 0, 0)
    monkeypatch.setattr(run_conductor, "free_gb", lambda path: 20, raising=False)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, len(launches)) == (0, 1)


def test_cli_a_launch_whose_inherited_tmpdir_slash_tmp_and_working_directory_each_report_at_least_veri_min_free_gb_free_launches_the_conductor_under_tdd_issue_2422(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.delenv("VERI_MIN_FREE_GB", raising=False)
    scratch = scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_claude_exiting(monkeypatch, 0, 0)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    free = {os.path.realpath(scratch): 20, os.path.realpath("/tmp"): 21, os.path.realpath(cwd): 22}
    monkeypatch.setattr(run_conductor, "free_gb", lambda path: free.get(os.path.realpath(path), 0), raising=False)

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, len(launches)) == (0, 1)


def test_cli_a_launch_whose_slash_tmp_reports_0_gb_free_launches_the_conductor_when_veri_min_free_gb_is_0_under_tdd_issue_2422(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.setenv("VERI_MIN_FREE_GB", "0")
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_claude_exiting(monkeypatch, 0, 0)
    monkeypatch.setattr(run_conductor, "free_gb",
                        lambda path: 0 if os.path.realpath(path) == os.path.realpath("/tmp") else 500,
                        raising=False)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, len(launches)) == (0, 1)


def test_cli_the_free_space_preflight_reads_the_directory_the_pytest_legs_pinned_scratch_path_constant_names_under_tdd_issue_2430(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.delenv("VERI_MIN_FREE_GB", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    pytest_leg = importlib.import_module("veri.pytest_leg")
    run_conductor = importlib.import_module("veri.run_conductor")
    pinned = tmp_path / "pinned"
    pinned.mkdir()
    monkeypatch.setattr(pytest_leg, "PINNED_TMPDIR", str(pinned))
    launches = fake_claude_exiting(monkeypatch, 0, 0)
    monkeypatch.setattr(run_conductor, "free_gb",
                        lambda path: 5 if os.path.realpath(path) == os.path.realpath(pinned) else 500,
                        raising=False)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, err = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, launches, "'%s' has 5 GB free" % pinned in err) == (2, [], True)


def tree_contents(root):
    """Every file and symlink under root but .git, by relative path: its bytes, or the target it links to."""
    contents = {}
    for path in sorted(pathlib.Path(root).rglob("*")):
        relative = path.relative_to(root)
        if relative.parts[0] == ".git":
            continue
        if path.is_symlink():
            contents[str(relative)] = ("->", os.readlink(path))
        elif path.is_file():
            contents[str(relative)] = path.read_bytes()
    return contents


def git_as_veri(repository):
    """The git argv prefix that runs in repository under a fixed committer identity."""
    return ["git", "-C", str(repository), "-c", "user.name=veri", "-c", "user.email=veri@example.test"]


def load_run_conductor(module_name, skill):
    """The run_conductor module loaded from skill's scripts/veri directory under module_name."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(module_name, str(skill / "scripts" / "veri" / "run_conductor.py"))
    run_conductor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_conductor)
    return run_conductor


def head_commit(repository):
    """The commit repository's HEAD names."""
    return subprocess.run(["git", "-C", str(repository), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()


def skill_clone(tmp_path, monkeypatch, module_name, files, directory="skill", commit=True):
    """A skill directory holding files (path: text, .sh files executable), committed unless commit is False, and its run_conductor module loaded from that directory."""
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    skill = tmp_path / directory
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
    for relative, text in files.items():
        (skill / relative).parent.mkdir(parents=True, exist_ok=True)
        (skill / relative).write_text(text)
        if relative.endswith(".sh"):
            (skill / relative).chmod(0o755)
    if commit:
        git = git_as_veri(skill)
        subprocess.run(["git", "init", "-q", str(skill)], check=True)
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-q", "-m", "the skill commit"], check=True)
    # Loading compiles the module before its own dont_write_bytecode line runs; a __pycache__ written
    # into the skill here is in tree_contents but never in the snapshot, whichever case loads first.
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    return skill, load_run_conductor(module_name, skill)


def commit_appended_line(repository, relative, message):
    """Commit to repository a line appended to relative, saying message."""
    with open(repository / relative, "a") as appended:
        appended.write("# " + message + "\n")
    subprocess.run(git_as_veri(repository) + ["commit", "-q", "-am", message], check=True)


def repin_commits(log):
    """The commit of every skill-repin event in the events log at log, none when the log does not exist."""
    if not log.is_file():
        return []
    return [json.loads(line)["commit"] for line in log.read_text().splitlines() if '"skill-repin"' in line]


def clone_behind_origin(tmp_path, remote, relative):
    """A clone of remote at tmp_path/clone, cut before one more commit, appending a line to relative, lands on remote."""
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(remote), str(clone)], check=True)
    commit_appended_line(remote, relative, "a commit that landed on the remote after the clone was cut")
    return clone


def caller_repository(tmp_path, files=None):
    """A committed caller repository at tmp_path/caller holding files (path: text); its commit is empty when there are none."""
    caller = tmp_path / "caller"
    caller.mkdir()
    for relative, text in (files or {}).items():
        (caller / relative).write_text(text)
    subprocess.run(["git", "init", "-q", str(caller)], check=True)
    subprocess.run(git_as_veri(caller) + ["add", "-A"], check=True)
    subprocess.run(git_as_veri(caller) + ["commit", "-q", "--allow-empty", "-m", "base"], check=True)
    return caller


def base_directories(stdin):
    """The base directories the procedure on a launched claude's stdin names."""
    stdin = stdin.decode() if isinstance(stdin, bytes) else stdin
    return [line[len("Base directory for this skill: "):] for line in stdin.splitlines()
            if line.startswith("Base directory for this skill: ")]


def without_origin_head(clone):
    subprocess.run(["git", "-C", str(clone), "remote", "set-head", "origin", "-d"], check=True)
    subprocess.run(["git", "-C", str(clone), "config", "remote.origin.followRemoteHEAD", "never"], check=True)


def claude_records_per_launch(monkeypatch, record):
    """Fake the launched claude; the returned list gains record(base directory, its call kwargs) per launch."""
    run, seen = subprocess.run, []

    def claude_reads_its_base(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        (base,) = base_directories(kwargs.get("input"))
        seen.append(record(base, kwargs))
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_reads_its_base)
    return seen


def claude_records_its_base_trees(monkeypatch):
    """Fake the launched claude; the returned list gains the tree under its base directory per launch."""
    return claude_records_per_launch(monkeypatch, lambda base, kwargs: tree_contents(base))


def claude_records_its_base_trees_and_prompts(monkeypatch):
    """Fake the launched claude; the returned list gains (base tree, prompt) per launch."""
    def tree_and_prompt(base, kwargs):
        stdin = kwargs.get("input")
        return tree_contents(base), stdin.decode() if isinstance(stdin, bytes) else stdin

    return claude_records_per_launch(monkeypatch, tree_and_prompt)


def claude_records_its_base_trees_and_environments(monkeypatch):
    """Fake the launched claude; the returned list gains (base tree, environment) per launch."""
    return claude_records_per_launch(
        monkeypatch, lambda base, kwargs: (tree_contents(base), dict(kwargs.get("env") or os.environ)))


@pytest.mark.process("real git archive and tar materialising a scratch skill clone's commit into the snapshot")
def test_cli_the_conductors_base_directory_holds_the_skill_commits_files_not_the_clones_uncommitted_edit_is_not_the_clone_and_is_gone_after_the_launch(
        tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(
        tmp_path, monkeypatch, "run_conductor_snapshot",
        {"SKILL.md": "# the committed procedure\n", "scripts/supervise.sh": "#!/bin/sh\necho the committed supervisor\n"})
    committed = tree_contents(skill)
    with open(skill / "scripts" / "supervise.sh", "a") as edit:
        edit.write("# uncommitted edit after the skill commit\n")
    run, seen = subprocess.run, []

    def claude_reads_its_base(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        bases = base_directories(kwargs.get("input"))
        seen.append((bases, tree_contents(bases[0]) if bases else None))
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_reads_its_base)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert len(seen) == 1 and len(seen[0][0]) == 1
    (base,), contents = seen[0]
    assert (code, os.path.realpath(base) == os.path.realpath(skill), contents == committed, os.path.exists(base)) == (
        0, False, True, False)


@pytest.mark.process("real git archive and tar materialising a scratch skill clone's commit, and a supervise.sh run from the snapshot")
def test_cli_a_leaf_launched_mid_run_executes_the_snapshots_supervise_sh_run_leaf_sh_and_template_not_the_clones(
        tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(
        tmp_path, monkeypatch, "run_conductor_leaf",
        {"SKILL.md": "# the committed procedure\n", "scripts/supervise.sh": "#!/bin/sh\necho the committed supervisor\n",
         "scripts/run-leaf.sh": "#!/bin/sh\necho the committed run-leaf\n",
         "scripts/prompts/develop-red.md": "the committed develop-red template\n"})
    scripts = skill / "scripts"
    (scripts / "supervise.sh").write_text("#!/bin/sh\necho SABOTAGED; exit 42\n")
    (scripts / "run-leaf.sh").unlink()
    (scripts / "prompts" / "develop-red.md").write_text("SABOTAGED-TEMPLATE\n")
    run, seen = subprocess.run, []

    def claude_launches_a_leaf_from_its_base(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        (base,) = base_directories(kwargs.get("input"))
        supervised = run([base + "/scripts/supervise.sh"], capture_output=True, text=True)
        seen.append((supervised.returncode, supervised.stdout, os.path.exists(base + "/scripts/run-leaf.sh"),
                     pathlib.Path(base, "scripts", "prompts", "develop-red.md").read_text()))
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_launches_a_leaf_from_its_base)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, seen) == (0, [(0, "the committed supervisor\n", True, "the committed develop-red template\n")])


@pytest.mark.process("real git archive and tar materialising a scratch skill clone's recorded commit twice, and a real caller repository holding the tdd branch that keeps the record")
def test_cli_a_resume_of_the_run_is_handed_a_re_materialised_snapshot_of_the_recorded_commit_not_the_clones_new_head(
        tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(
        tmp_path, monkeypatch, "run_conductor_resume",
        {"SKILL.md": "# the committed procedure\n", "scripts/supervise.sh": "#!/bin/sh\necho the recorded supervisor\n"})
    recorded = tree_contents(skill)
    caller = caller_repository(tmp_path)
    subprocess.run(git_as_veri(caller) + ["branch", "tdd/4242-past-preflight"], check=True)
    run, seen = subprocess.run, []

    def claude_reads_its_base(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        (base,) = base_directories(kwargs.get("input"))
        seen.append((base, tree_contents(base)))
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_reads_its_base)

    first_code, _, _ = run_cli(run_conductor, ["4242"], cwd=caller)
    (skill / "scripts" / "supervise.sh").write_text("#!/bin/sh\necho the pulled supervisor\n")
    subprocess.run(git_as_veri(skill) + ["commit", "-q", "-am", "pulled after the run started"], check=True)
    resumed_code, _, _ = run_cli(run_conductor, ["4242"], cwd=caller)

    assert len(seen) == 2
    (first_base, _), (resumed_base, resumed_contents) = seen
    assert (first_code, resumed_code, os.path.exists(first_base), resumed_contents == recorded) == (0, 0, False, True)


@pytest.mark.process("real git archive and tar materialising a scratch skill clone's current commit, and the real event.sh appending the skill-repin event in a real caller repository")
def test_cli_a_resume_with_veri_new_skill_1_is_re_pinned_to_the_clones_current_commit_and_logs_a_skill_repin_event(
        tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(
        tmp_path, monkeypatch, "run_conductor_repin",
        {"SKILL.md": "# the committed procedure\n", "scripts/supervise.sh": "#!/bin/sh\necho the recorded supervisor\n"})
    caller = caller_repository(tmp_path)
    subprocess.run(git_as_veri(caller) + ["branch", "tdd/4242-past-preflight"], check=True)
    seen = claude_records_its_base_trees(monkeypatch)

    first_code, _, _ = run_cli(run_conductor, ["4242"], cwd=caller)
    (skill / "scripts" / "supervise.sh").write_text("#!/bin/sh\necho the pulled supervisor\n")
    subprocess.run(git_as_veri(skill) + ["commit", "-q", "-am", "a commit the operator asks the run to take"], check=True)
    current = head_commit(skill)
    taken = tree_contents(skill)
    resumed_code, _, _ = run_cli(run_conductor, ["4242"], cwd=caller, env={"VERI_NEW_SKILL": "1"})

    repins = repin_commits(caller / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl")
    assert len(seen) == 2
    assert (first_code, resumed_code, seen[1] == taken, (caller / ".tdd" / "issue-4242-skill-commit").read_text(),
            repins) == (0, 0, True, current + "\n", [current])


def test_cli_with_no_resolvable_skill_commit_the_run_proceeds_unpinned_from_the_skill_directory_itself_and_warns_on_stderr(
        tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(
        tmp_path, monkeypatch, "run_conductor_loose", {"SKILL.md": "# the loose procedure\n"},
        directory="loose", commit=False)
    fake_unresolvable(monkeypatch)
    answer, seen = subprocess.run, []

    def claude_reads_its_base(args, *a, **kwargs):
        if list(args)[:1] == ["fake-claude"]:
            seen.append(base_directories(kwargs.get("input")))
        return answer(args, *a, **kwargs)

    monkeypatch.setattr(subprocess, "run", claude_reads_its_base)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert len(seen) == 1 and len(seen[0]) == 1
    assert (code, os.path.realpath(seen[0][0]) == os.path.realpath(skill), "unpinned" in stderr.lower()) == (
        0, True, True), stderr


def test_cli_an_unpinned_launch_hands_the_conductor_veri_skill_unpinned_1(
        tmp_path, monkeypatch, run_cli):
    _, run_conductor = skill_clone(
        tmp_path, monkeypatch, "run_conductor_unpinned_env", {"SKILL.md": "# the loose procedure\n"},
        directory="loose", commit=False)
    launches = fake_unresolvable(monkeypatch)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, [launch["VERI_SKILL_UNPINNED"] for launch in launches]) == (0, ["1"]), stderr


@pytest.mark.process("real git archive and tar materialising a scratch skill clone's commit, and git status read in a real caller repository and the skill clone")
def test_cli_a_launch_leaves_git_status_porcelain_empty_in_the_callers_checkout_and_in_the_skill_clone_during_and_after_the_run(
        tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(
        tmp_path, monkeypatch, "run_conductor_status", {"SKILL.md": "# the committed procedure\n"})
    caller = caller_repository(tmp_path, {"README": "target\n"})
    run = subprocess.run

    def status():
        return {name: run(["git", "-C", str(tree), "status", "--porcelain"], capture_output=True, text=True).stdout
                for name, tree in (("caller", caller), ("clone", skill))}

    during = []

    def claude_reads_both_statuses(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        during.append(status())
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_reads_both_statuses)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    clean = {"caller": "", "clone": ""}
    assert (code, during, status()) == (0, [clean], clean), stderr


@pytest.mark.process("real git clone, fetch and archive of a scratch skill clone whose origin has moved on, and git reading its HEAD, branch and status")
def test_cli_a_launch_leaves_the_skill_clones_head_branch_and_working_tree_unchanged_when_origin_has_moved_on_and_the_tree_has_an_uncommitted_edit(
        tmp_path, monkeypatch, run_cli):
    remote, _ = skill_clone(tmp_path, monkeypatch, "run_conductor_remote", {"SKILL.md": "# the committed procedure\n"},
                            directory="remote")
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(remote), str(clone)], check=True)
    with open(remote / "SKILL.md", "a") as landed:
        landed.write("# a commit that landed on the remote after the clone was cut\n")
    subprocess.run(git_as_veri(remote) + ["commit", "-q", "-am", "pulled"], check=True)
    with open(clone / "SKILL.md", "a") as edit:
        edit.write("# an uncommitted edit in the clone\n")
    run_conductor = load_run_conductor("run_conductor_clone", clone)
    caller = caller_repository(tmp_path, {"README": "target\n"})
    run = subprocess.run

    def state():
        git = ["git", "-C", str(clone)]
        read = lambda *args: run(git + list(args), capture_output=True, text=True).stdout
        return (read("rev-parse", "HEAD"), read("symbolic-ref", "-q", "HEAD"), read("status", "--porcelain"),
                tree_contents(clone))

    def claude_returns(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_returns)
    before = state()

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    assert (code, state()) == (0, before), stderr


def launch_reading_procedure(tmp_path, monkeypatch, run_cli, run_conductor, examine):
    """(exit code, stderr, [examine(stdin) per claude started]) for run_conductor launched with 4242 from an empty directory."""
    run, seen = subprocess.run, []

    def claude_reads_its_procedure(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        stdin = kwargs.get("input")
        seen.append(examine(stdin.decode() if isinstance(stdin, bytes) else stdin))
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_reads_its_procedure)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=cwd)
    return code, stderr, seen


@pytest.mark.process("real git archive and tar materialising a scratch skill clone's commit, with an uncommitted edit to its SKILL.md in the tree")
def test_cli_a_frontmatter_fenced_procedure_launches_exits_0_and_reaches_the_binary_whole_with_an_uncommitted_edit_to_skill_md_in_the_tree(
        tmp_path, monkeypatch, run_cli):
    committed = "---\nname: tdd\n---\n# the committed procedure\n"
    skill, run_conductor = skill_clone(tmp_path, monkeypatch, "run_conductor_edited_procedure", {"SKILL.md": committed})
    with open(skill / "SKILL.md", "a") as edit:
        edit.write("uncommitted edit to the procedure\n")

    code, stderr, seen = launch_reading_procedure(
        tmp_path, monkeypatch, run_cli, run_conductor,
        lambda stdin: (stdin.split("\n", 1)[0], stdin.startswith(committed.rstrip("\n"))))

    assert (code, seen) == (0, [("---", True)]), stderr


@pytest.mark.process("real git archive and tar materialising a scratch skill clone's commit, with a marker line prepended to its SKILL.md in the tree")
def test_cli_a_working_tree_edit_to_skill_md_never_reaches_the_conductor_the_committed_skill_md_does(
        tmp_path, monkeypatch, run_cli):
    committed = "---\nname: tdd\n---\n# the committed procedure\n"
    marker = "uncommitted edit to the procedure, never to reach the conductor"
    skill, run_conductor = skill_clone(tmp_path, monkeypatch, "run_conductor_prepended_edit", {"SKILL.md": committed})
    (skill / "SKILL.md").write_text(marker + "\n" + committed)

    code, stderr, seen = launch_reading_procedure(
        tmp_path, monkeypatch, run_cli, run_conductor,
        lambda stdin: (marker in stdin, stdin.startswith(committed.rstrip("\n"))))

    assert (code, seen) == (0, [(False, True)]), stderr


@pytest.mark.process("a real develop-prompt builder, supervise.sh and run-leaf.sh run from a launched claude, the leaf's prompt read off a stub claude")
def test_cli_2748_the_develop_red_leaf_launched_alone_receives_the_affected_tier(tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(tmp_path, monkeypatch, "run_conductor_tier_develop_red", {"SKILL.md": "# the procedure\n"})
    every = "make ALL-TIER-7781"
    tiers = tmp_path / "tiers"
    tiers.mkdir()
    (tiers / "spec.md").write_text("spec\n")
    (tiers / ".gitignore").write_text(".tdd/\n*.received\n*.prompt\n")
    stub = tmp_path / "tier-claude"
    stub.write_text('#!/bin/sh\nwhile [ "$#" -gt 0 ]; do\n  [ "$1" = "-p" ] && { printf \'%s\\n\' "$2" > "$LEAF_PROMPT_OUT"; shift; }\n'
                    '  shift\ndone\nprintf \'%s\\n\' \'{"type":"result","subtype":"success","is_error":false,"result":"done"}\'\n')
    stub.chmod(0o755)
    run, launched = subprocess.run, {}

    def claude_launches_develop_red(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        run([str(SCRIPTS / "build-develop-prompt.sh"), "red", "spec.md", "the step", every], cwd=tiers, check=True,
            stdout=open(tiers / "develop-red.prompt", "w"))
        env = dict(os.environ, CLAUDE_BIN=str(stub), LEAF_PROMPT_OUT=str(tiers / "develop-red.received"), VERI_POLL="0.02")
        launched["exit"] = run([str(SCRIPTS / "supervise.sh"), "develop-red", str(SCRIPTS / "run-leaf.sh"), "develop-red.prompt"],
                               cwd=tiers, env=env, capture_output=True).returncode
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_launches_develop_red)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=cwd)

    received = tiers / "develop-red.received"
    text = received.read_text() if received.exists() else ""
    assert (code, launched.get("exit"), "affected-suites.sh" in text, "FAST-TIER" in text) == (0, 0, True, False), stderr


@pytest.mark.process("a real develop-prompt builder, supervise.sh and run-leaf.sh run from a launched claude, the leaf's prompt read off a stub claude")
def test_cli_2748_the_develop_green_leaf_launched_alone_receives_the_fast_and_affected_tier(tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(tmp_path, monkeypatch, "run_conductor_tier_develop_green", {"SKILL.md": "# the procedure\n"})
    fast, every = "make FAST-TIER-7781", "make ALL-TIER-7781"
    tiers = tmp_path / "tiers"
    tiers.mkdir()
    (tiers / "spec.md").write_text("spec\n")
    (tiers / ".gitignore").write_text(".tdd/\n*.received\n*.prompt\n")
    stub = tmp_path / "tier-claude"
    stub.write_text('#!/bin/sh\nwhile [ "$#" -gt 0 ]; do\n  [ "$1" = "-p" ] && { printf \'%s\\n\' "$2" > "$LEAF_PROMPT_OUT"; shift; }\n'
                    '  shift\ndone\nprintf \'%s\\n\' \'{"type":"result","subtype":"success","is_error":false,"result":"done"}\'\n')
    stub.chmod(0o755)
    run, launched = subprocess.run, {}

    def claude_launches_develop_green(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        run([str(SCRIPTS / "build-develop-prompt.sh"), "green", "spec.md", "the step", every, "t.test.sh", "the case", fast], cwd=tiers, check=True,
            stdout=open(tiers / "develop-green.prompt", "w"))
        env = dict(os.environ, CLAUDE_BIN=str(stub), LEAF_PROMPT_OUT=str(tiers / "develop-green.received"), VERI_POLL="0.02")
        launched["exit"] = run([str(SCRIPTS / "supervise.sh"), "develop-green", str(SCRIPTS / "run-leaf.sh"), "develop-green.prompt"],
                               cwd=tiers, env=env, capture_output=True).returncode
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_launches_develop_green)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=cwd)

    received = tiers / "develop-green.received"
    text = received.read_text() if received.exists() else ""
    assert (code, launched.get("exit"), "affected-suites.sh" in text, fast in text) == (0, 0, True, True), stderr


@pytest.mark.process("a real develop-prompt builder, supervise.sh and run-leaf.sh run from a launched claude, the leaf's prompt read off a stub claude")
def test_cli_2748_the_develop_refactor_leaf_launched_alone_receives_the_affected_tier(tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(tmp_path, monkeypatch, "run_conductor_tier_develop_refactor", {"SKILL.md": "# the procedure\n"})
    every = "make ALL-TIER-7781"
    tiers = tmp_path / "tiers"
    tiers.mkdir()
    (tiers / "spec.md").write_text("spec\n")
    (tiers / ".gitignore").write_text(".tdd/\n*.received\n*.prompt\n")
    stub = tmp_path / "tier-claude"
    stub.write_text('#!/bin/sh\nwhile [ "$#" -gt 0 ]; do\n  [ "$1" = "-p" ] && { printf \'%s\\n\' "$2" > "$LEAF_PROMPT_OUT"; shift; }\n'
                    '  shift\ndone\nprintf \'%s\\n\' \'{"type":"result","subtype":"success","is_error":false,"result":"done"}\'\n')
    stub.chmod(0o755)
    run, launched = subprocess.run, {}

    def claude_launches_develop_refactor(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        run([str(SCRIPTS / "build-develop-prompt.sh"), "refactor", "spec.md", "the step", every, "src/a.sh"], cwd=tiers, check=True,
            stdout=open(tiers / "develop-refactor.prompt", "w"))
        env = dict(os.environ, CLAUDE_BIN=str(stub), LEAF_PROMPT_OUT=str(tiers / "develop-refactor.received"), VERI_POLL="0.02")
        launched["exit"] = run([str(SCRIPTS / "supervise.sh"), "develop-refactor", str(SCRIPTS / "run-leaf.sh"), "develop-refactor.prompt"],
                               cwd=tiers, env=env, capture_output=True).returncode
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_launches_develop_refactor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=cwd)

    received = tiers / "develop-refactor.received"
    text = received.read_text() if received.exists() else ""
    assert (code, launched.get("exit"), "affected-suites.sh" in text, "FAST-TIER" in text) == (0, 0, True, False), stderr


@pytest.mark.process("the real verify.sh run from a launched claude, the leaf's prompt read off a stub claude")
def test_cli_2748_the_verify_red_leaf_given_fast_cmd_launched_alone_receives_the_fast_and_affected_tier(tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(tmp_path, monkeypatch, "run_conductor_tier_verify_red", {"SKILL.md": "# the procedure\n"})
    fast = "make FAST-TIER-7781"
    tiers = tmp_path / "tiers"
    tiers.mkdir()
    (tiers / "spec.md").write_text("spec\n")
    (tiers / ".gitignore").write_text(".tdd/\n*.received\n*.prompt\n")
    step = checked_step(tiers, committed_head(tiers))
    stub = tmp_path / "tier-claude"
    stub.write_text('#!/bin/sh\nwhile [ "$#" -gt 0 ]; do\n  [ "$1" = "-p" ] && { printf \'%s\\n\' "$2" > "$LEAF_PROMPT_OUT"; shift; }\n'
                    '  shift\ndone\nprintf \'%s\\n\' \'{"type":"result","subtype":"success","is_error":false,"result":"VERDICT: PASS\\nREASON: ok"}\'\n')
    stub.chmod(0o755)
    run, launched = subprocess.run, {}

    def claude_launches_verify_red(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        env = dict(os.environ, CLAUDE_BIN=str(stub), LEAF_PROMPT_OUT=str(tiers / "verify-red.received"), VERI_POLL="0.02", **step)
        launched["exit"] = run([str(SCRIPTS / "verify.sh"), "--step", "the step", "--fast-cmd", fast, "red", "spec.md", "t.test.sh", "the case"],
                               cwd=tiers, env=env, capture_output=True).returncode
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_launches_verify_red)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=cwd)

    received = tiers / "verify-red.received"
    text = received.read_text() if received.exists() else ""
    assert (code, launched.get("exit"), "affected-suites.sh" in text, fast in text) == (0, 0, True, True), stderr


@pytest.mark.process("the real verify.sh run from a launched claude, the leaf's prompt read off a stub claude")
def test_cli_2748_the_verify_green_leaf_given_fast_cmd_launched_alone_receives_the_fast_and_affected_tier(tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(tmp_path, monkeypatch, "run_conductor_tier_verify_green", {"SKILL.md": "# the procedure\n"})
    fast = "make FAST-TIER-7781"
    tiers = tmp_path / "tiers"
    tiers.mkdir()
    (tiers / "spec.md").write_text("spec\n")
    (tiers / ".gitignore").write_text(".tdd/\n*.received\n*.prompt\n")
    step = checked_step(tiers, committed_head(tiers))
    stub = tmp_path / "tier-claude"
    stub.write_text('#!/bin/sh\nwhile [ "$#" -gt 0 ]; do\n  [ "$1" = "-p" ] && { printf \'%s\\n\' "$2" > "$LEAF_PROMPT_OUT"; shift; }\n'
                    '  shift\ndone\nprintf \'%s\\n\' \'{"type":"result","subtype":"success","is_error":false,"result":"VERDICT: PASS\\nREASON: ok"}\'\n')
    stub.chmod(0o755)
    run, launched = subprocess.run, {}

    def claude_launches_verify_green(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        env = dict(os.environ, CLAUDE_BIN=str(stub), LEAF_PROMPT_OUT=str(tiers / "verify-green.received"), VERI_POLL="0.02", **step)
        launched["exit"] = run([str(SCRIPTS / "verify.sh"), "--step", "the step", "--fast-cmd", fast, "green", "spec.md", "t.test.sh", "the case"],
                               cwd=tiers, env=env, capture_output=True).returncode
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_launches_verify_green)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=cwd)

    received = tiers / "verify-green.received"
    text = received.read_text() if received.exists() else ""
    assert (code, launched.get("exit"), "affected-suites.sh" in text, fast in text) == (0, 0, True, True), stderr


@pytest.mark.process("the real verify.sh run from a launched claude, the leaf's prompt read off a stub claude")
def test_cli_2748_the_verify_refactor_leaf_given_fast_cmd_launched_alone_receives_the_fast_and_affected_tier(tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(tmp_path, monkeypatch, "run_conductor_tier_verify_refactor", {"SKILL.md": "# the procedure\n"})
    fast = "make FAST-TIER-7781"
    tiers = tmp_path / "tiers"
    tiers.mkdir()
    (tiers / "spec.md").write_text("spec\n")
    (tiers / ".gitignore").write_text(".tdd/\n*.received\n*.prompt\n")
    step = checked_step(tiers, committed_head(tiers))
    stub = tmp_path / "tier-claude"
    stub.write_text('#!/bin/sh\nwhile [ "$#" -gt 0 ]; do\n  [ "$1" = "-p" ] && { printf \'%s\\n\' "$2" > "$LEAF_PROMPT_OUT"; shift; }\n'
                    '  shift\ndone\nprintf \'%s\\n\' \'{"type":"result","subtype":"success","is_error":false,"result":"VERDICT: PASS\\nREASON: ok"}\'\n')
    stub.chmod(0o755)
    run, launched = subprocess.run, {}

    def claude_launches_verify_refactor(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        env = dict(os.environ, CLAUDE_BIN=str(stub), LEAF_PROMPT_OUT=str(tiers / "verify-refactor.received"), VERI_POLL="0.02", **step)
        launched["exit"] = run([str(SCRIPTS / "verify.sh"), "--step", "the step", "--fast-cmd", fast, "refactor", "spec.md", "t.test.sh", "abc1234"],
                               cwd=tiers, env=env, capture_output=True).returncode
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_launches_verify_refactor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=cwd)

    received = tiers / "verify-refactor.received"
    text = received.read_text() if received.exists() else ""
    assert (code, launched.get("exit"), "affected-suites.sh" in text, fast in text) == (0, 0, True, True), stderr


@pytest.mark.process("the real verify.sh run from a launched claude, a stub claude that records any prompt it receives")
def test_cli_2748_the_verify_refactor_leaf_without_fast_cmd_launched_alone_exits_2_and_reaches_no_claude(tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(tmp_path, monkeypatch, "run_conductor_tier_verify_refactor_bare", {"SKILL.md": "# the procedure\n"})
    tiers = tmp_path / "tiers"
    tiers.mkdir()
    (tiers / "spec.md").write_text("spec\n")
    (tiers / ".gitignore").write_text(".tdd/\n*.received\n*.prompt\n")
    step = checked_step(tiers, committed_head(tiers))
    stub = tmp_path / "tier-claude"
    stub.write_text('#!/bin/sh\nwhile [ "$#" -gt 0 ]; do\n  [ "$1" = "-p" ] && { printf \'%s\\n\' "$2" > "$LEAF_PROMPT_OUT"; shift; }\n'
                    '  shift\ndone\nprintf \'%s\\n\' \'{"type":"result","subtype":"success","is_error":false,"result":"VERDICT: PASS\\nREASON: ok"}\'\n')
    stub.chmod(0o755)
    run, launched = subprocess.run, {}

    def claude_launches_bare_verify_refactor(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        env = dict(os.environ, CLAUDE_BIN=str(stub), LEAF_PROMPT_OUT=str(tiers / "verify-refactor-bare.received"), VERI_POLL="0.02", **step)
        launched["exit"] = run([str(SCRIPTS / "verify.sh"), "--step", "the step", "refactor", "spec.md", "t.test.sh", "abc1234"],
                               cwd=tiers, env=env, capture_output=True).returncode
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_launches_bare_verify_refactor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, launched.get("exit"), (tiers / "verify-refactor-bare.received").exists()) == (0, 2, False), stderr


@pytest.mark.process("real git archive and tar materialising a scratch skill clone's commit reached through a symlink, and a real caller repository holding the record")
def test_cli_a_run_through_a_symlink_to_the_skill_directory_from_another_working_directory_pins_snapshots_and_records_as_run_in_place(
        tmp_path, monkeypatch, run_cli):
    skill, _ = skill_clone(
        tmp_path, monkeypatch, "run_conductor_in_place", {"SKILL.md": "# the committed procedure\n"})
    tip = head_commit(skill)
    with open(skill / "SKILL.md", "a") as edit:
        edit.write("# uncommitted edit to the clone's SKILL.md\n")
    link = tmp_path / "link"
    link.symlink_to(skill)
    run_conductor = load_run_conductor("run_conductor_through_link", link)
    caller = caller_repository(tmp_path)
    run, seen = subprocess.run, []

    def claude_reads_its_record_and_base(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        bases = base_directories(kwargs.get("input"))
        record = caller / ".tdd" / "issue-4242-skill-commit"
        seen.append({"record": record.read_text().strip() if record.exists() else None,
                     "bases": len(bases),
                     "base_is_clone": bool(bases) and os.path.realpath(bases[0]) == os.path.realpath(skill),
                     "skill_md": (pathlib.Path(bases[0]) / "SKILL.md").read_bytes() if bases else None,
                     "names_tip": tip in kwargs.get("input").decode()})
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_reads_its_record_and_base)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    assert (code, seen) == (0, [{"record": tip, "bases": 1, "base_is_clone": False,
                                 "skill_md": b"# the committed procedure\n", "names_tip": True}]), stderr


@pytest.mark.process("real git init, commit and clone of a checkout under test whose origin is a local bare repository or an https address nothing listens on, the skill clone's real git fetch of that checkout, and git archive and tar materialising the fetched commit")
def test_cli_a_launch_from_a_skill_clone_whose_origin_is_a_checkout_under_test_with_an_unreachable_origin_exits_and_hands_claude_its_environment_as_with_a_reachable_origin(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    monkeypatch.setenv("GIT_TERMINAL_PROMPT", "0")
    run, seen = subprocess.run, []

    def claude_reads_its_environment(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        seen.append({name: value for name, value in kwargs["env"].items() if name.startswith("VERI_SKILL_")})
        return subprocess.CompletedProcess(args, 0, None, None)

    answers = {}
    for name in ("reachable", "unreachable"):
        variant = tmp_path / name
        checkout = variant / "checkout"
        (checkout / "scripts" / "veri").mkdir(parents=True)
        (checkout / "SKILL.md").write_text("---\nname: tdd\n---\n# the procedure\n")
        (checkout / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
        subprocess.run(["git", "init", "-q", str(checkout)], check=True)
        subprocess.run(git_as_veri(checkout) + ["add", "-A"], check=True)
        subprocess.run(git_as_veri(checkout) + ["commit", "-q", "-m", "the checkout under test"], check=True)
        remote = variant / "remote.git"
        subprocess.run(["git", "clone", "-q", "--bare", str(checkout), str(remote)], check=True)
        origin = str(remote) if name == "reachable" else "https://127.0.0.1:1/veri.git"
        subprocess.run(git_as_veri(checkout) + ["remote", "add", "origin", origin], check=True)
        skill = variant / "skill"
        subprocess.run(["git", "clone", "-q", str(checkout), str(skill)], check=True)
        (checkout / "SKILL.md").write_text("---\nname: tdd\n---\n# the procedure, advanced\n")
        subprocess.run(git_as_veri(checkout) + ["commit", "-q", "-am", "the checkout under test advances"], check=True)
        tip = head_commit(checkout)
        run_conductor = load_run_conductor("run_conductor_checkout_" + name, skill)
        caller = variant / "caller"
        caller.mkdir()
        monkeypatch.setattr(subprocess, "run", claude_reads_its_environment)
        seen.clear()
        code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)
        monkeypatch.setattr(subprocess, "run", run)
        answers[name] = (code, [{"VERI_SKILL_CLONE": env.get("VERI_SKILL_CLONE") == str(skill),
                                 "VERI_SKILL_COMMIT": env.get("VERI_SKILL_COMMIT") == tip,
                                 "VERI_SKILL_REF": env.get("VERI_SKILL_REF"),
                                 "VERI_SKILL_UNPINNED": env.get("VERI_SKILL_UNPINNED")} for env in seen], stderr)

    assert answers["unreachable"][:2] == answers["reachable"][:2], answers["unreachable"][2]
    assert answers["reachable"][:2] == (0, [{"VERI_SKILL_CLONE": True, "VERI_SKILL_COMMIT": True,
                                             "VERI_SKILL_REF": "refs/remotes/origin/HEAD",
                                             "VERI_SKILL_UNPINNED": None}]), answers["reachable"][2]


@pytest.mark.process("real git clone, fetch and archive of a scratch skill clone whose origin has moved on, and tar materialising origin's tip")
def test_cli_a_launch_from_a_clone_behind_origin_default_is_handed_a_snapshot_of_origins_tip(
        tmp_path, monkeypatch, run_cli):
    remote, _ = skill_clone(tmp_path, monkeypatch, "run_conductor_tip_remote",
                            {"SKILL.md": "# the committed procedure\n", "scripts/supervise.sh": "#!/bin/sh\necho the cut supervisor\n"},
                            directory="remote")
    clone = clone_behind_origin(tmp_path, remote, "scripts/supervise.sh")
    tip = tree_contents(remote)
    behind = tree_contents(clone)
    run_conductor = load_run_conductor("run_conductor_tip_clone", clone)
    caller = caller_repository(tmp_path)
    seen = claude_records_its_base_trees(monkeypatch)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    assert tip != behind
    assert (code, seen == [tip]) == (0, True), stderr


@pytest.mark.process("real git clone, fetch and archive of a scratch skill clone whose origin has moved on, and the real event.sh and supervise.sh run from the snapshot in a real caller repository")
@pytest.mark.tree_audit("every directory under scripts/ but tests/")
def test_cli_every_event_a_launched_run_writes_carries_origins_tip_as_skill_commit_and_the_prompt_names_it(
        tmp_path, monkeypatch, run_cli):
    remote, _ = skill_clone(tmp_path, monkeypatch, "run_conductor_events_remote", {"SKILL.md": "# the committed procedure\n"},
                            directory="remote", commit=False)
    shutil.copytree(SCRIPTS, remote / "scripts", symlinks=True, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("tests", "__pycache__", "run_conductor.py"))
    subprocess.run(["git", "init", "-q", str(remote)], check=True)
    subprocess.run(git_as_veri(remote) + ["add", "-A"], check=True)
    subprocess.run(git_as_veri(remote) + ["commit", "-q", "-m", "the skill commit"], check=True)
    clone = clone_behind_origin(tmp_path, remote, "scripts/supervise.sh")
    tip = head_commit(remote)
    run_conductor = load_run_conductor("run_conductor_events_clone", clone)
    caller = caller_repository(tmp_path)
    run, prompts = subprocess.run, []

    def claude_writes_events_from_its_base(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        stdin = kwargs.get("input")
        prompts.append(stdin.decode() if isinstance(stdin, bytes) else stdin)
        (base,) = base_directories(stdin)
        env = dict(kwargs.get("env") or os.environ, VERI_POLL="0.02")
        run([base + "/scripts/event.sh", "conductor-mark"], cwd=caller, env=env, capture_output=True)
        run([base + "/scripts/supervise.sh", "develop-red", "echo", "ok"], cwd=caller, env=env, capture_output=True)
        return subprocess.CompletedProcess(args, 0, None, None)

    monkeypatch.setattr(subprocess, "run", claude_writes_events_from_its_base)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    log = caller / ".tdd" / "events.jsonl"
    events = [json.loads(line) for line in log.read_text().splitlines() if line.strip()] if log.exists() else []
    assert code == 0, stderr
    assert [event["event"] for event in events][:1] == ["conductor-mark"]
    assert len(events) > 1
    assert [(event["event"], event.get("skill_commit")) for event in events if event.get("skill_commit") != tip] == []
    assert len(prompts) == 1 and tip in prompts[0]


@pytest.mark.process("real git clone, fetch and archive of a scratch skill clone whose origin moves between two launches, tar materialising the recorded commit, and a real caller repository holding the tdd branch that keeps the record")
def test_cli_a_resumed_run_keeps_its_recorded_pin_when_origin_default_has_moved_since_the_first_launch(
        tmp_path, monkeypatch, run_cli):
    remote, _ = skill_clone(tmp_path, monkeypatch, "run_conductor_pin_remote",
                            {"SKILL.md": "# the committed procedure\n", "scripts/supervise.sh": "#!/bin/sh\necho the first supervisor\n"},
                            directory="remote")
    first = head_commit(remote)
    recorded = tree_contents(remote)
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(remote), str(clone)], check=True)
    run_conductor = load_run_conductor("run_conductor_pin_clone", clone)
    caller = caller_repository(tmp_path)
    subprocess.run(git_as_veri(caller) + ["branch", "tdd/4242-past-preflight"], check=True)
    seen = claude_records_its_base_trees_and_prompts(monkeypatch)

    first_code, _, _ = run_cli(run_conductor, ["4242"], cwd=caller)
    commit_appended_line(remote, "scripts/supervise.sh", "a commit that landed on the remote after the run started")
    moved = head_commit(remote)
    resumed_code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    assert moved != first and len(seen) == 2
    resumed_tree, resumed_prompt = seen[1]
    assert (first_code, resumed_code, resumed_tree == recorded, first in resumed_prompt, moved in resumed_prompt) == (
        0, 0, True, True, False), stderr


@pytest.mark.process("real git clone, fetch and archive of a scratch skill clone whose origin and own HEAD have both moved on, tar materialising origin's tip, and the real event.sh appending the skill-repin event in a real caller repository")
def test_cli_a_resume_with_veri_new_skill_1_re_pins_to_origin_default_as_just_fetched_not_to_the_clones_head(
        tmp_path, monkeypatch, run_cli):
    remote, _ = skill_clone(tmp_path, monkeypatch, "run_conductor_repin_tip_remote",
                            {"SKILL.md": "# the committed procedure\n", "scripts/supervise.sh": "#!/bin/sh\necho the cut supervisor\n"},
                            directory="remote")
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(remote), str(clone)], check=True)
    run_conductor = load_run_conductor("run_conductor_repin_tip_clone", clone)
    caller = caller_repository(tmp_path)
    subprocess.run(git_as_veri(caller) + ["branch", "tdd/4242-past-preflight"], check=True)
    seen = claude_records_its_base_trees_and_prompts(monkeypatch)

    first_code, _, _ = run_cli(run_conductor, ["4242"], cwd=caller)
    commit_appended_line(remote, "scripts/supervise.sh", "a commit that landed on the remote after the run started")
    tip = head_commit(remote)
    tip_tree = tree_contents(remote)
    commit_appended_line(clone, "scripts/supervise.sh", "a commit of the clone's own that origin never saw")
    clone_head = head_commit(clone)
    resumed_code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller, env={"VERI_NEW_SKILL": "1"})

    assert tip != clone_head and len(seen) == 2
    resumed_tree, resumed_prompt = seen[1]
    assert (first_code, resumed_code, resumed_tree == tip_tree, tip in resumed_prompt, clone_head in resumed_prompt,
            (caller / ".tdd" / "issue-4242-skill-commit").read_text()) == (0, 0, True, True, False, tip + "\n"), stderr


@pytest.mark.process("real git archive and tar materialising a scratch skill clone's current commit, a recorded commit the clone cannot resolve, and the real event.sh appending the skill-repin event in a real caller repository")
def test_cli_an_unresolvable_recorded_skill_commit_refuses_with_exit_2_unless_veri_new_skill_1_which_re_pins_and_logs_a_skill_repin_event(
        tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(
        tmp_path, monkeypatch, "run_conductor_unresolvable",
        {"SKILL.md": "# the committed procedure\n", "scripts/supervise.sh": "#!/bin/sh\necho the supervisor\n"})
    head = head_commit(skill)
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    subprocess.run(["git", "init", "-q", str(foreign)], check=True)
    subprocess.run(git_as_veri(foreign) + ["commit", "-q", "--allow-empty", "-m", "elsewhere"], check=True)
    missing = head_commit(foreign)
    caller = caller_repository(tmp_path)
    subprocess.run(git_as_veri(caller) + ["branch", "tdd/4242-past-preflight"], check=True)
    seen = claude_records_its_base_trees(monkeypatch)
    record = caller / ".tdd" / "issue-4242-skill-commit"

    first_code, _, _ = run_cli(run_conductor, ["4242"], cwd=caller)
    record.write_text(missing + "\n")
    refused_code, _, _ = run_cli(run_conductor, ["4242"], cwd=caller)
    launched_when_refused = len(seen)
    record.write_text(missing + "\n")
    repinned_code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller, env={"VERI_NEW_SKILL": "1"})

    repins = repin_commits(caller / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl")
    assert (first_code, refused_code, launched_when_refused, repinned_code, len(seen), record.read_text(),
            repins) == (0, 2, 1, 0, 2, head + "\n", [head]), stderr


def launched_once_then_moved_on(tmp_path, monkeypatch, run_cli, module_name):
    skill, run_conductor = skill_clone(
        tmp_path, monkeypatch, module_name,
        {"SKILL.md": "# the committed procedure\n", "scripts/supervise.sh": "#!/bin/sh\necho the recorded supervisor\n"})
    caller = caller_repository(tmp_path)
    subprocess.run(git_as_veri(caller) + ["branch", "tdd/4242-past-preflight"], check=True)
    claude_records_its_base_trees(monkeypatch)

    first_code, _, _ = run_cli(run_conductor, ["4242"], cwd=caller)
    commit_appended_line(skill, "SKILL.md", "a commit the operator asks the run to take")
    current = head_commit(skill)
    return run_conductor, caller, first_code, current


@pytest.mark.process("real git archive and tar materialising a scratch skill clone's current commit, and the real event.sh appending the skill-repin event in a real caller repository")
def test_cli_the_skill_repin_event_lands_in_the_run_worktrees_events_jsonl_never_the_callers(
        tmp_path, monkeypatch, run_cli):
    run_conductor, caller, first_code, current = launched_once_then_moved_on(tmp_path, monkeypatch, run_cli, "run_conductor_repin_log")
    (caller / ".tdd" / "wt" / "4242").mkdir(parents=True, exist_ok=True)
    resumed_code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller, env={"VERI_NEW_SKILL": "1"})

    assert (first_code, resumed_code, repin_commits(caller / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl"),
            repin_commits(caller / ".tdd" / "events.jsonl")) == (0, 0, [current], []), stderr


@pytest.mark.process("real git archive and tar materialising a scratch skill clone's current commit, and the real event.sh appending the skill-repin event in a real caller repository")
def test_cli_a_veri_new_skill_1_re_pin_that_runs_before_the_run_worktree_exists_writes_its_skill_repin_event_to_the_run_worktrees_events_jsonl_and_never_to_the_callers(
        tmp_path, monkeypatch, run_cli):
    run_conductor, caller, first_code, current = launched_once_then_moved_on(tmp_path, monkeypatch, run_cli, "run_conductor_repin_before_worktree")
    shutil.rmtree(caller / ".tdd" / "wt" / "4242", ignore_errors=True)
    worktree_existed = (caller / ".tdd" / "wt" / "4242").exists()
    resumed_code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller, env={"VERI_NEW_SKILL": "1"})

    assert (first_code, worktree_existed, resumed_code,
            repin_commits(caller / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl"),
            repin_commits(caller / ".tdd" / "events.jsonl")) == (0, False, 0, [current], []), stderr


@pytest.mark.process("real git clone, fetch and archive of a scratch skill clone with no refs/remotes/origin/HEAD whose origin has moved on, tar materialising origin's tip, and a real caller repository holding the tdd branch that keeps the record")
def test_cli_with_no_origin_head_the_launch_pins_to_the_remotes_default_branch_tip_records_it_and_runs_pinned(
        tmp_path, monkeypatch, run_cli):
    remote, _ = skill_clone(tmp_path, monkeypatch, "run_conductor_no_head_remote",
                            {"SKILL.md": "# the committed procedure\n", "scripts/supervise.sh": "#!/bin/sh\necho the cut supervisor\n"},
                            directory="remote")
    clone = clone_behind_origin(tmp_path, remote, "scripts/supervise.sh")
    without_origin_head(clone)
    tip = head_commit(remote)
    run_conductor = load_run_conductor("run_conductor_no_head_clone", clone)
    caller = caller_repository(tmp_path)
    subprocess.run(git_as_veri(caller) + ["branch", "tdd/4242-past-preflight"], check=True)
    seen = claude_records_its_base_trees_and_environments(monkeypatch)
    monkeypatch.delenv("VERI_SKILL_UNPINNED", raising=False)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    record = caller / ".tdd" / "issue-4242-skill-commit"
    assert (code, record.read_text() if record.is_file() else None, [tree for tree, _ in seen],
            ["VERI_SKILL_UNPINNED" in env for _, env in seen]) == (0, tip + "\n", [tree_contents(remote)], [False]), stderr


@pytest.mark.process("real git clone and ls-remote of a scratch skill clone with no refs/remotes/origin/HEAD whose origin is on a detached HEAD, so it names no default branch")
def test_cli_with_no_origin_head_and_no_resolvable_remote_default_branch_the_launch_exits_2_naming_the_ref_and_never_runs_unpinned(
        tmp_path, monkeypatch, run_cli):
    remote, _ = skill_clone(tmp_path, monkeypatch, "run_conductor_no_default_remote",
                            {"SKILL.md": "# the committed procedure\n"}, directory="remote")
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(remote), str(clone)], check=True)
    without_origin_head(clone)
    subprocess.run(["git", "-C", str(remote), "checkout", "-q", "--detach"], check=True)
    subprocess.run(git_as_veri(remote) + ["commit", "-q", "--allow-empty", "-m", "on no branch"], check=True)
    run_conductor = load_run_conductor("run_conductor_no_default_clone", clone)
    caller = caller_repository(tmp_path)
    seen = claude_records_its_base_trees_and_environments(monkeypatch)
    monkeypatch.delenv("VERI_SKILL_UNPINNED", raising=False)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    assert (code, "refs/remotes/origin/HEAD" in stderr, seen) == (2, True, []), stderr


@pytest.mark.process("real git clone and ls-remote of a scratch skill clone with no refs/remotes/origin/HEAD whose remote names a default branch the clone holds no ref for")
def test_cli_with_no_origin_head_and_the_remotes_named_default_branch_absent_locally_the_launch_exits_2_naming_the_ref_and_never_runs_unpinned(
        tmp_path, monkeypatch, run_cli):
    remote, _ = skill_clone(tmp_path, monkeypatch, "run_conductor_absent_default_remote",
                            {"SKILL.md": "# the committed procedure\n"}, directory="remote")
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(remote), str(clone)], check=True)
    default = subprocess.run(["git", "-C", str(remote), "symbolic-ref", "--short", "HEAD"],
                             check=True, capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "-C", str(remote), "branch", "-q", "side"], check=True)
    without_origin_head(clone)
    subprocess.run(["git", "-C", str(clone), "config", "remote.origin.fetch", "+refs/heads/side:refs/remotes/origin/side"], check=True)
    subprocess.run(["git", "-C", str(clone), "update-ref", "-d", "refs/remotes/origin/" + default], check=True)
    run_conductor = load_run_conductor("run_conductor_absent_default_clone", clone)
    caller = caller_repository(tmp_path)
    seen = claude_records_its_base_trees_and_environments(monkeypatch)
    monkeypatch.delenv("VERI_SKILL_UNPINNED", raising=False)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    assert (code, "refs/remotes/origin/HEAD" in stderr, seen) == (2, True, []), stderr


def fetch_faked_run(tmp_path, monkeypatch):
    past_the_guards(monkeypatch)
    monkeypatch.setenv("VERI_FETCH_RETRY_SLEEP", "0")
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT"):
        monkeypatch.delenv(name, raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_claude_env(monkeypatch, True, True, None)
    answer, calls = subprocess.run, []
    cwd = tmp_path / "caller"
    cwd.mkdir()
    return run_conductor, launches, answer, calls, cwd


def run_with_the_first_fetches_losing_a_ref_lock(locked_fetches, tmp_path, monkeypatch, run_cli, interval="0"):
    run_conductor, launches, answer, calls, cwd = fetch_faked_run(tmp_path, monkeypatch)
    if interval is None:
        monkeypatch.delenv("VERI_FETCH_RETRY_SLEEP", raising=False)
    lock = "error: cannot lock ref 'refs/remotes/origin/main': is at 1111111 but expected 2222222\n"
    tip, prompts = "3333333333333333333333333333333333333333", []

    def lock_held_for_the_first_fetches(args, *rest, **kwargs):
        args = list(args)
        calls.append(args)
        if args[3:] == ["fetch", "-q", "origin"] and len([c for c in calls if c[3:4] == ["fetch"]]) <= locked_fetches:
            return subprocess.CompletedProcess(args, 1, "", lock)
        if args[3:] == ["rev-parse", "refs/remotes/origin/HEAD"]:
            return subprocess.CompletedProcess(args, 0, tip + "\n", "")
        if args[:1] == ["sleep"]:
            return subprocess.CompletedProcess(args, 0)
        if args[:1] == ["fake-claude"]:
            prompts.append(kwargs["input"].decode())
        return answer(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", lock_held_for_the_first_fetches)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=cwd)

    fetches = [call for call in calls if call[3:4] == ["fetch"]]
    sleeps = [call for call in calls if call[:1] == ["sleep"]]
    assert (code, len(fetches), sleeps, len(launches), "fetch of origin failed" in stderr) == (
        0, locked_fetches + 1, [["sleep", interval or "1"]] * locked_fetches, 1, False), stderr
    assert ["Pinned skill commit (name it in the plan comment): %s" % tip in prompt for prompt in prompts] == [True]


def test_cli_a_fetch_of_origin_that_loses_a_ref_lock_held_by_another_process_is_retried_once_the_lock_is_released_and_the_conductor_starts_886(
        tmp_path, monkeypatch, run_cli):
    run_with_the_first_fetches_losing_a_ref_lock(1, tmp_path, monkeypatch, run_cli)


def test_cli_a_locked_fetch_is_retried_after_waiting_the_interval_veri_fetch_retry_sleep_names_so_veri_fetch_retry_sleep_0_retries_without_waiting_on_the_real_clock_900(
        tmp_path, monkeypatch, run_cli):
    run_with_the_first_fetches_losing_a_ref_lock(1, tmp_path, monkeypatch, run_cli)


def test_cli_with_veri_fetch_retry_sleep_unset_a_locked_fetch_is_retried_after_waiting_1_s_the_default_interval_900(
        tmp_path, monkeypatch, run_cli):
    run_with_the_first_fetches_losing_a_ref_lock(1, tmp_path, monkeypatch, run_cli, interval=None)


def test_cli_a_fetch_of_origin_whose_ref_lock_is_still_held_when_the_second_fetch_runs_keeps_retrying_until_the_lock_is_released_and_the_conductor_starts_886(
        tmp_path, monkeypatch, run_cli):
    run_with_the_first_fetches_losing_a_ref_lock(2, tmp_path, monkeypatch, run_cli)


def run_with_the_one_fetch_failing(fetch_stderr, tmp_path, monkeypatch, run_cli):
    run_conductor, launches, answer, calls, cwd = fetch_faked_run(tmp_path, monkeypatch)

    def fetch_fails_with_no_lock(args, *rest, **kwargs):
        args = list(args)
        calls.append(args)
        if args[3:] == ["fetch", "-q", "origin"]:
            return subprocess.CompletedProcess(args, 128, "", fetch_stderr)
        if args[:1] == ["sleep"]:
            return subprocess.CompletedProcess(args, 0)
        return answer(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", fetch_fails_with_no_lock)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=cwd)

    fetches = [call for call in calls if call[3:4] == ["fetch"]]
    sleeps = [call for call in calls if call[:1] == ["sleep"]]
    assert (code, len(fetches), sleeps, launches, "fetch of origin failed" in stderr) == (
        2, 1, [], [], True), stderr


def test_cli_a_fetch_of_origin_whose_url_is_no_remote_is_refused_with_exit_2_and_the_fetch_failed_message_after_one_fetch_not_after_the_lock_retries_886(
        tmp_path, monkeypatch, run_cli):
    url = str(tmp_path / "no-remote")
    run_with_the_one_fetch_failing(
        "fatal: '%s' does not appear to be a git repository\n" % url, tmp_path, monkeypatch, run_cli)


def test_cli_a_fetch_of_origin_that_fails_for_a_reason_other_than_a_ref_lock_is_refused_with_exit_2_after_one_fetch_without_waiting_for_any_retry_1012(
        tmp_path, monkeypatch, run_cli):
    run_with_the_one_fetch_failing(
        "fatal: unable to access 'x': Could not resolve host: origin.invalid\n", tmp_path, monkeypatch, run_cli)


def clone_behind_origin_holding_a_ref_lock(tmp_path, monkeypatch, name):
    remote, _ = skill_clone(tmp_path, monkeypatch, name + "_remote", {"SKILL.md": "# the committed procedure\n"},
                            directory="remote")
    clone = clone_behind_origin(tmp_path, remote, "SKILL.md")
    branch = subprocess.run(["git", "-C", str(remote), "symbolic-ref", "--short", "HEAD"], capture_output=True,
                            text=True, check=True).stdout.strip()
    lock = clone / ".git" / "refs" / "remotes" / "origin" / (branch + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.touch()
    return head_commit(remote), lock, load_run_conductor(name + "_clone", clone), caller_repository(tmp_path)


@pytest.mark.process("a real ref lock file held against the skill clone's real git fetch of a real origin, released by the sleep between retries, and git archive and tar materialising origin's tip")
def test_cli_a_ref_lock_that_outlives_five_back_to_back_fetches_and_is_released_only_while_the_run_waits_between_retries_still_lets_the_conductor_start_pinned_to_origins_tip_886(
        tmp_path, monkeypatch, run_cli):
    tip, lock, run_conductor, caller = clone_behind_origin_holding_a_ref_lock(tmp_path, monkeypatch, "run_conductor_lock")
    monkeypatch.setenv("VERI_FETCH_RETRY_SLEEP", "0")
    run, prompts = subprocess.run, []

    def sleep_releases_the_lock(args, *a, **kwargs):
        args = list(args)
        if args[:1] == ["sleep"]:
            lock.unlink()
            return subprocess.CompletedProcess(args, 0)
        if args[:1] == ["fake-claude"]:
            prompts.append(kwargs["input"].decode())
            return subprocess.CompletedProcess(args, 0, None, None)
        return run(args, *a, **kwargs)

    monkeypatch.setattr(subprocess, "run", sleep_releases_the_lock)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    assert (code, len(prompts), bool(prompts) and tip in prompts[0]) == (0, 1, True), stderr


def real_git_with_a_fake_claude_and_instant_sleep(monkeypatch, after_fetch=lambda fetches: None):
    run, prompts, fetches = subprocess.run, [], []

    def fake_claude_and_instant_sleep(args, *a, **kwargs):
        args = list(args)
        if args[:1] == ["sleep"]:
            return subprocess.CompletedProcess(args, 0)
        if args[:1] == ["fake-claude"]:
            prompts.append(kwargs["input"].decode())
            return subprocess.CompletedProcess(args, 0, None, None)
        done = run(args, *a, **kwargs)
        if args[3:4] == ["fetch"]:
            fetches.append(args)
            after_fetch(fetches)
        return done

    monkeypatch.setattr(subprocess, "run", fake_claude_and_instant_sleep)
    return prompts, fetches


@pytest.mark.process("a real ref lock file held against the skill clone's real git fetch of a real origin until the fifth fetch has run, and git archive and tar materialising origin's tip")
def test_cli_a_ref_lock_still_held_when_the_fifth_fetch_runs_and_released_only_after_it_lets_the_conductor_start_pinned_to_origins_tip_1012(
        tmp_path, monkeypatch, run_cli):
    tip, lock, run_conductor, caller = clone_behind_origin_holding_a_ref_lock(tmp_path, monkeypatch, "run_conductor_fifth_fetch")
    monkeypatch.setenv("VERI_FETCH_RETRY_SLEEP", "0")
    prompts, fetches = real_git_with_a_fake_claude_and_instant_sleep(
        monkeypatch, lambda fetches: len(fetches) >= 5 and lock.unlink(missing_ok=True))

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    assert (code, len(prompts), bool(prompts) and tip in prompts[0]) == (0, 1, True), stderr


@pytest.mark.process("a real ref lock file held and never released against the skill clone's real git fetch of a real origin, whichever wording the installed git gives it")
def test_cli_a_ref_lock_that_is_never_released_makes_the_launch_refuse_with_exit_2_once_the_retry_bound_past_five_fetches_is_reached_launching_no_conductor_and_naming_the_ref_lock_whichever_wording_git_used_1012_1306(
        tmp_path, monkeypatch, run_cli):
    _, _, run_conductor, caller = clone_behind_origin_holding_a_ref_lock(tmp_path, monkeypatch, "run_conductor_never_released")
    monkeypatch.setenv("VERI_FETCH_RETRY_SLEEP", "0")
    prompts, fetches = real_git_with_a_fake_claude_and_instant_sleep(monkeypatch)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    assert (code, prompts, len(fetches) > 5, "run-conductor: another process holds the ref lock" in stderr) == (
        2, [], True, True), stderr


@pytest.mark.process("a real git work tree whose ls-files the skill copy reads")
def test_loose_skill_copies_tracked_and_untracked_unignored_files_under_skills_tdd_and_never_an_ignored_cache(tmp_path):
    repo = tmp_path / "src"
    skill = repo / "skills" / "tdd"
    (skill / "scripts" / "veri" / "__pycache__").mkdir(parents=True)
    (skill / "SKILL.md").write_text("skill\n")
    (repo / ".gitignore").write_text("__pycache__/\n")
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-qm", "skill"], check=True)
    (skill / "untracked.txt").write_text("stray\n")
    (skill / "scripts" / "veri" / "__pycache__" / "mod.pyc").write_text("cache\n")

    destination = tmp_path / "dest"
    loose_skill(skill, destination)

    assert (destination / "SKILL.md").read_text() == "skill\n"
    assert (destination / "untracked.txt").read_text() == "stray\n"
    assert not (destination / "scripts" / "veri" / "__pycache__").exists()


def claude_that_runs(monkeypatch, hook=lambda: None, code=0):
    """Fake the launched claude; the first launch runs hook(), every launch exits code, and the returned list gains (base tree, prompt) per launch."""
    run, seen = subprocess.run, []

    def claude_leaves_its_mark(args, *a, **kwargs):
        if list(args)[:1] != ["fake-claude"]:
            return run(args, *a, **kwargs)
        prompt = kwargs["input"].decode()
        (base,) = base_directories(prompt)
        seen.append((tree_contents(base), prompt))
        if len(seen) == 1:
            hook()
        return subprocess.CompletedProcess(args, code, None, None)

    monkeypatch.setattr(subprocess, "run", claude_leaves_its_mark)
    return seen


def skill_and_caller(tmp_path, monkeypatch, module_name):
    skill, run_conductor = skill_clone(
        tmp_path, monkeypatch, module_name,
        {"SKILL.md": "# the committed procedure\n", "scripts/supervise.sh": "#!/bin/sh\necho the first supervisor\n"})
    return skill, run_conductor, caller_repository(tmp_path)


def seeded_record(caller, commit):
    record = caller / ".tdd" / "issue-4242-skill-commit"
    record.parent.mkdir()
    record.write_text(commit + "\n")
    return record


def registered_worktrees(repository):
    listed = subprocess.run(["git", "-C", str(repository), "worktree", "list", "--porcelain"],
                            capture_output=True, text=True, check=True).stdout
    return [line[len("worktree "):] for line in listed.splitlines() if line.startswith("worktree ")]


@pytest.mark.process("real git worktree add registering .tdd/wt/<n> in a real caller repository, and git archive and tar materialising the recorded commit")
def test_cli_a_conductor_that_exits_with_tdd_wt_n_registered_as_a_worktree_keeps_the_skill_record_and_the_next_launch_runs_the_recorded_commit_866(
        tmp_path, monkeypatch, run_cli):
    skill, run_conductor, caller = skill_and_caller(tmp_path, monkeypatch, "run_conductor_record_worktree")
    first = head_commit(skill)
    recorded = tree_contents(skill)
    worktree = caller / ".tdd" / "wt" / "4242"
    def add_worktree_then_seed_pid():
        pid_file = worktree / ".tdd" / "conductor.pid"
        seeded = pid_file.read_bytes() if pid_file.is_file() else None
        if worktree.exists():
            shutil.rmtree(worktree)
        subprocess.run(git_as_veri(caller) + ["worktree", "add", "-q", "--detach", str(worktree)], check=True)
        if seeded is not None:
            pid_file.parent.mkdir(exist_ok=True)
            pid_file.write_bytes(seeded)

    seen = claude_that_runs(monkeypatch, add_worktree_then_seed_pid)
    record = caller / ".tdd" / "issue-4242-skill-commit"

    first_code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)
    kept = record.read_text() if record.is_file() else None
    registered = os.path.realpath(worktree) in [os.path.realpath(path) for path in registered_worktrees(caller)]
    commit_appended_line(skill, "scripts/supervise.sh", "a commit that landed after the run got past preflight")
    moved = head_commit(skill)
    resumed_code, _, resumed_stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    assert len(seen) == 2
    assert (first_code, registered, kept, resumed_code, seen[1][0] == recorded, first in seen[1][1],
            moved in seen[1][1]) == (0, True, first + "\n", 0, True, True, False), stderr + resumed_stderr


@pytest.mark.process("a real caller repository holding a local tdd/<n>-* branch and no worktree, and git archive and tar materialising the recorded commit")
def test_cli_a_conductor_that_exits_with_a_local_tdd_n_branch_and_no_worktree_keeps_the_skill_record_and_the_next_launch_runs_the_recorded_commit_866(
        tmp_path, monkeypatch, run_cli):
    skill, run_conductor, caller = skill_and_caller(tmp_path, monkeypatch, "run_conductor_record_branch")
    first = head_commit(skill)
    recorded = tree_contents(skill)
    seen = claude_that_runs(
        monkeypatch, lambda: subprocess.run(git_as_veri(caller) + ["branch", "tdd/4242-past-preflight"], check=True))
    record = caller / ".tdd" / "issue-4242-skill-commit"

    first_code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)
    kept = record.read_text() if record.is_file() else None
    branch = subprocess.run(git_as_veri(caller) + ["show-ref", "--verify", "-q", "refs/heads/tdd/4242-past-preflight"]).returncode
    worktrees = registered_worktrees(caller)
    commit_appended_line(skill, "scripts/supervise.sh", "a commit that landed after the run got past preflight")
    moved = head_commit(skill)
    resumed_code, _, resumed_stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    assert len(seen) == 2
    assert (first_code, branch, len(worktrees), kept, resumed_code, seen[1][0] == recorded, first in seen[1][1],
            moved in seen[1][1]) == (0, 0, 1, first + "\n", 0, True, True, False), stderr + resumed_stderr


@pytest.mark.process("a real caller repository with no .tdd/wt/<n> worktree and no tdd/<n>-* branch, and git archive and tar materialising the pinned commit")
def test_cli_a_conductor_that_exits_0_or_non_zero_with_no_registered_tdd_wt_n_worktree_and_no_local_tdd_n_branch_leaves_no_skill_record_866(
        tmp_path, monkeypatch, run_cli):
    skill, run_conductor = skill_clone(
        tmp_path, monkeypatch, "run_conductor_record_removed",
        {"SKILL.md": "# the committed procedure\n", "scripts/supervise.sh": "#!/bin/sh\necho the supervisor\n"})
    outcomes = []
    for code in (0, 1):
        parent = tmp_path / f"caller-{code}"
        parent.mkdir()
        caller = caller_repository(parent)
        claude_that_runs(monkeypatch, code=code)
        exited, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)
        outcomes.append((exited, (caller / ".tdd" / "issue-4242-skill-commit").exists()))

    assert outcomes == [(0, False), (1, False)]


@pytest.mark.process("a real caller repository holding only a local tdd/<n>6-* branch of another issue, and git archive and tar materialising the pinned commit")
def test_cli_a_local_branch_for_another_issue_whose_number_starts_with_n_tdd_n6_does_not_count_as_a_run_past_preflight_the_skill_record_is_removed_866(
        tmp_path, monkeypatch, run_cli):
    _, run_conductor, caller = skill_and_caller(tmp_path, monkeypatch, "run_conductor_record_other_issue")
    claude_that_runs(
        monkeypatch, lambda: subprocess.run(git_as_veri(caller) + ["branch", "tdd/42426-other-issue"], check=True))

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    branch = subprocess.run(git_as_veri(caller) + ["show-ref", "--verify", "-q", "refs/heads/tdd/42426-other-issue"]).returncode
    assert (code, branch, (caller / ".tdd" / "issue-4242-skill-commit").exists()) == (0, 0, False), stderr


@pytest.mark.process("a real caller repository left with no worktree and no tdd/<n>-* branch, and git archive and tar materialising the tip at each launch")
def test_cli_after_a_launch_that_left_no_worktree_and_no_tdd_n_branch_the_next_launch_without_veri_new_skill_pins_the_default_branchs_tip_at_that_moment_not_the_earlier_launchs_commit_866(
        tmp_path, monkeypatch, run_cli):
    skill, run_conductor, caller = skill_and_caller(tmp_path, monkeypatch, "run_conductor_record_repinned_by_tip")
    first = head_commit(skill)
    seen = claude_that_runs(monkeypatch)

    first_code, _, _ = run_cli(run_conductor, ["4242"], cwd=caller)
    commit_appended_line(skill, "scripts/supervise.sh", "a commit that landed after the run stopped at preflight")
    moved = head_commit(skill)
    tip = tree_contents(skill)
    second_code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    assert len(seen) == 2
    assert (first_code, second_code, first in seen[0][1], seen[1][0] == tip, moved in seen[1][1], first in seen[1][1]) == (
        0, 0, True, True, True, False), stderr


@pytest.mark.process("a real caller repository holding an unregistered .tdd/wt/<n> with only .tdd/events.jsonl written by the real event.sh, and git archive and tar materialising the fresh tip")
def test_cli_an_unregistered_tdd_wt_n_holding_only_tdd_events_jsonl_as_veri_new_skill_1_leaves_it_does_not_count_as_a_run_past_preflight_with_no_worktree_and_no_branch_the_skill_record_is_removed_866(
        tmp_path, monkeypatch, run_cli):
    skill, run_conductor, caller = skill_and_caller(tmp_path, monkeypatch, "run_conductor_record_events_only")
    record = seeded_record(caller, head_commit(skill))
    claude_that_runs(monkeypatch)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller, env={"VERI_NEW_SKILL": "1"})

    worktree = caller / ".tdd" / "wt" / "4242"
    left = sorted(str(path.relative_to(worktree)) for path in worktree.rglob("*") if path.is_file())
    registered = os.path.realpath(worktree) in [os.path.realpath(path) for path in registered_worktrees(caller)]
    assert (code, left, registered, record.exists()) == (0, [".tdd/events.jsonl"], False, False), stderr


@pytest.mark.process("a recorded commit the skill clone cannot resolve, with no worktree and no tdd/<n>-* branch in a real caller repository")
def test_cli_with_no_worktree_and_no_tdd_n_branch_an_unresolvable_recorded_skill_commit_still_exits_2_before_launching_any_conductor_866(
        tmp_path, monkeypatch, run_cli):
    _, run_conductor, caller = skill_and_caller(tmp_path, monkeypatch, "run_conductor_record_unresolvable")
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    subprocess.run(["git", "init", "-q", str(foreign)], check=True)
    subprocess.run(git_as_veri(foreign) + ["commit", "-q", "--allow-empty", "-m", "elsewhere"], check=True)
    missing = head_commit(foreign)
    seeded_record(caller, missing)
    seen = claude_that_runs(monkeypatch)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)

    assert (code, seen) == (2, []), stderr


@pytest.mark.process("a real caller repository with no worktree and no tdd/<n>-* branch, git archive and tar materialising the fresh tip, and the real event.sh appending the skill-repin event")
def test_cli_with_no_worktree_and_no_tdd_n_branch_veri_new_skill_1_still_re_pins_the_record_to_the_fresh_tip_for_the_conductors_run_and_writes_its_skill_repin_event_866(
        tmp_path, monkeypatch, run_cli):
    skill, run_conductor, caller = skill_and_caller(tmp_path, monkeypatch, "run_conductor_record_repin_no_run")
    record = seeded_record(caller, head_commit(skill))
    commit_appended_line(skill, "scripts/supervise.sh", "a commit the operator asks the run to take")
    moved = head_commit(skill)
    during = []
    seen = claude_that_runs(monkeypatch, lambda: during.append(record.read_text()))

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller, env={"VERI_NEW_SKILL": "1"})

    repins = repin_commits(caller / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl")
    assert len(seen) == 1
    assert (code, during, moved in seen[0][1], repins) == (0, [moved + "\n"], True, [moved]), stderr


def run_signalled_while_claude_runs(signum, claude_code, tmp_path, monkeypatch, run_cli, module_name):
    """Launch with a claude that is sent signum while it runs; answers (exit code, stderr, snapshot while claude still ran, snapshot after the exit)."""
    skill, run_conductor, caller = skill_and_caller(tmp_path, monkeypatch, module_name)
    during = []

    def signalled():
        os.kill(os.getpid(), signum)
        (snapshot,) = base_directories(seen[0][1])
        during.append(os.path.isdir(snapshot))

    seen = claude_that_runs(monkeypatch, signalled, code=claude_code)
    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=caller)
    (snapshot,) = base_directories(seen[0][1])
    return code, stderr, during, os.path.exists(snapshot)


@pytest.mark.process("a real SIGTERM sent to the conductor's own process while its claude runs, and git archive and tar materialising the snapshot")
def test_cli_sent_sigterm_while_its_claude_runs_keeps_the_snapshot_until_claude_exits_then_removes_it_and_exits_143(
        tmp_path, monkeypatch, run_cli):
    code, stderr, during, left = run_signalled_while_claude_runs(
        signal.SIGTERM, 0, tmp_path, monkeypatch, run_cli, "run_conductor_sigterm")

    assert (code, during, left) == (143, [True], False), stderr


@pytest.mark.process("a real SIGINT alone sent to the conductor's own process while its claude runs, and git archive and tar materialising the snapshot")
def test_cli_sent_sigint_alone_while_its_claude_runs_waits_for_claude_removes_the_snapshot_prints_no_traceback_and_exits_with_claudes_status_1219(
        tmp_path, monkeypatch, run_cli):
    code, stderr, during, left = run_signalled_while_claude_runs(
        signal.SIGINT, 5, tmp_path, monkeypatch, run_cli, "run_conductor_sigint")

    assert (code, during, left, "Traceback" in stderr) == (5, [True], False, False), stderr


@pytest.mark.process("a real SIGHUP alone sent to the conductor's own process while its claude runs, and git archive and tar materialising the snapshot")
def test_cli_sent_sighup_alone_while_its_claude_runs_waits_for_claude_removes_the_snapshot_prints_no_traceback_and_exits_with_claudes_status_1219(
        tmp_path, monkeypatch, run_cli):
    code, stderr, during, left = run_signalled_while_claude_runs(
        signal.SIGHUP, 5, tmp_path, monkeypatch, run_cli, "run_conductor_sighup")

    assert (code, during, left, "Traceback" in stderr) == (5, [True], False, False), stderr


def conductor_that_prints(monkeypatch, tmp_path, events, stdout, code=0):
    """The snapshot materialised and the conductor started in-process: the conductor appends events (a list of
    event names) to the run's log, prints stdout on its stream and exits code; the gh calls are returned."""
    commit = "1111111111111111111111111111111111111111"
    calls = fake_pin(monkeypatch, commit, set())
    fake_snapshot(monkeypatch, calls, 0, 0)
    started, gh_calls = subprocess.run, []

    def start(args, *a, **kwargs):
        args = list(args)
        if args[:1] == ["gh"]:
            gh_calls.append(args[1:])
            return subprocess.CompletedProcess(args, 0, b"", b"")
        if args[:1] != ["fake-claude"]:
            return started(args, *a, **kwargs)
        log = tmp_path / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl"
        log.parent.mkdir(parents=True, exist_ok=True)
        with open(log, "a") as appended:
            for name in events:
                appended.write(json.dumps({"event": name, "ts": 1}) + "\n")
        os.write(1, stdout.encode())
        return subprocess.CompletedProcess(args, code, None, None)

    monkeypatch.setattr(subprocess, "run", start)
    return gh_calls


def result_record(text):
    return json.dumps({"type": "result", "subtype": "success", "result": text}) + "\n"


def events_named(tmp_path):
    log = tmp_path / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl"
    return [json.loads(line) for line in log.read_text().splitlines()]


def test_cli_a_conductor_that_exits_0_with_a_result_ending_on_a_question_and_events_ending_in_no_done_bail_or_stop_gets_a_needs_user_bail_appended_1866(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    conductor_that_prints(monkeypatch, tmp_path, ["phase-start"],
                          result_record("Options A, B or C.\n\nWhich option do you want?"))

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    records = events_named(tmp_path)
    assert (code, records[-1].get("event"), records[-1].get("cause")) == (0, "bail", "needs-user"), stderr


@pytest.mark.parametrize("closing", ["done", "bail", "stop"])
def test_cli_a_conductor_that_exits_0_with_a_result_ending_on_a_question_but_events_already_ending_in_done_bail_or_stop_gets_no_bail_appended_1866(
        closing, tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    conductor_that_prints(monkeypatch, tmp_path, [closing], result_record("Which option do you want?"))

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (code, [r.get("event") for r in events_named(tmp_path)]) == (0, [closing]), stderr


@pytest.mark.parametrize("answer, log_events, bails", [
    ((True, "bailed", {"event": "bail"}), ["phase-start"], False),
    ((True, "unknown", {}), ["done"], True),
])
def test_cli_a_run_is_closed_by_what_run_end_answers_and_not_by_the_events_log_2009(
        answer, log_events, bails, tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    monkeypatch.setattr(run_conductor.run_end, "run_end", lambda run_dir: answer)
    conductor_that_prints(monkeypatch, tmp_path, log_events, result_record("Which option do you want?"))

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    records = events_named(tmp_path)
    appended = records[-1].get("event") == "bail" and records[-1].get("cause") == "needs-user"
    assert (code, appended) == (0, bails), stderr


@pytest.mark.parametrize("code, stdout", [(1, result_record("Which option do you want?")), (0, "")])
def test_cli_a_conductor_failing_or_silent_over_bail_resume_launch_gets_no_bail_appended_and_keeps_its_exit_code_2009(
        code, stdout, tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    conductor_that_prints(monkeypatch, tmp_path, ["bail", "resume", "launch"], stdout, code=code)

    got, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (got, [r.get("event") for r in events_named(tmp_path)]) == (code, ["bail", "resume", "launch"]), stderr


def test_cli_a_conductor_that_exits_0_with_a_result_not_ending_on_a_question_and_events_ending_in_no_done_bail_or_stop_gets_a_needs_user_bail_appended_1866(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    conductor_that_prints(monkeypatch, tmp_path, ["phase-start"], result_record("I will stop here and wait for you."))

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    records = events_named(tmp_path)
    assert (code, records[-1].get("event"), records[-1].get("cause")) == (0, "bail", "needs-user"), stderr


def test_cli_a_run_whose_last_non_blank_event_is_done_after_an_open_one_and_before_blank_lines_is_closed_and_gets_no_bail_appended_1977(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    conductor_that_prints(monkeypatch, tmp_path, [], result_record("Which option do you want?"))
    log = tmp_path / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text('{"event": "phase-start", "ts": 1}\n{"event": "done", "ts": 2}\n\n  \n')

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (code, [line for line in log.read_text().splitlines() if line.strip()]) == (
        0, ['{"event": "phase-start", "ts": 1}', '{"event": "done", "ts": 2}']), stderr


def test_cli_a_run_whose_last_non_blank_event_is_bail_after_an_open_one_and_before_blank_lines_is_closed_and_gets_no_bail_appended_1977(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    conductor_that_prints(monkeypatch, tmp_path, [], result_record("Which option do you want?"))
    log = tmp_path / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text('{"event": "phase-start", "ts": 1}\n{"event": "bail", "ts": 2}\n\n  \n')

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (code, [line for line in log.read_text().splitlines() if line.strip()]) == (
        0, ['{"event": "phase-start", "ts": 1}', '{"event": "bail", "ts": 2}']), stderr


def test_cli_a_run_whose_last_non_blank_event_is_stop_after_an_open_one_and_before_blank_lines_is_closed_and_gets_no_bail_appended_1977(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    conductor_that_prints(monkeypatch, tmp_path, [], result_record("Which option do you want?"))
    log = tmp_path / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text('{"event": "phase-start", "ts": 1}\n{"event": "stop", "ts": 2}\n\n  \n')

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (code, [line for line in log.read_text().splitlines() if line.strip()]) == (
        0, ['{"event": "phase-start", "ts": 1}', '{"event": "stop", "ts": 2}']), stderr


def test_cli_a_run_whose_last_non_blank_event_is_neither_done_bail_nor_stop_even_after_a_closing_one_is_open_and_gets_a_needs_user_bail_appended_1977(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    conductor_that_prints(monkeypatch, tmp_path, [], result_record("Which option do you want?"))
    log = tmp_path / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text('{"event": "done", "ts": 1}\n{"event": "phase-start", "ts": 2}\n\n  \n')

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (code, [line for line in log.read_text().splitlines() if line.strip()]) == (
        0, ['{"event": "done", "ts": 1}', '{"event": "phase-start", "ts": 2}']), stderr


def test_cli_a_run_whose_events_are_bail_then_resume_then_launch_is_open_and_gets_a_needs_user_bail_appended_2009(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    conductor_that_prints(monkeypatch, tmp_path, [], result_record("Which option do you want?"))
    log = tmp_path / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text('{"event": "bail", "ts": 1}\n{"event": "resume", "ts": 2}\n{"event": "launch", "ts": 3}\n')

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    records = [json.loads(line) for line in log.read_text().splitlines() if line.strip()]
    assert (code, records[-1].get("event"), records[-1].get("cause")) == (0, "bail", "needs-user"), stderr


def test_cli_a_run_whose_last_non_blank_line_is_not_json_after_a_done_event_is_open_and_gets_a_needs_user_bail_appended_1977(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    conductor_that_prints(monkeypatch, tmp_path, [], result_record("Which option do you want?"))
    log = tmp_path / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text('{"event": "done", "ts": 1}\nnot json at all\n\n  \n')

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    last = [line for line in log.read_text().splitlines() if line.strip()][-1]
    record = json.loads(last)
    assert (code, record.get("event"), record.get("cause")) == (0, "bail", "needs-user"), stderr


@pytest.mark.parametrize("stdout, expected", [(result_record("Which option do you want?"), 3), ("", 0)])
def test_cli_a_conductor_that_exits_non_zero_or_exits_0_without_a_result_record_gets_no_bail_appended_1866(
        stdout, expected, tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    conductor_that_prints(monkeypatch, tmp_path, ["phase-start"], stdout, code=expected)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (code, [r.get("event") for r in events_named(tmp_path)]) == (expected, ["phase-start"]), stderr


def test_cli_the_needs_user_bail_also_posts_an_issue_comment_quoting_only_the_last_paragraph_of_the_result_1866(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    gh_calls = conductor_that_prints(monkeypatch, tmp_path, ["phase-start"],
                                     result_record("Options A, B or C.\n\nWhich option do you want?"))

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    logged = " ".join(" ".join(call) for call in gh_calls)
    assert (code, "4242" in logged and "Which option do you want?" in logged and "Options A, B or C." not in logged) == (0, True), stderr + logged


def test_cli_the_needs_user_comment_under_the_rest_driver_posts_over_the_issue_comments_route_with_the_body_as_a_field_starts_no_gh_issue_and_quotes_only_the_last_paragraph_1974(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    monkeypatch.setenv("VERI_GH_DRIVER", "rest")
    run_conductor = importlib.import_module("veri.run_conductor")
    gh_calls = conductor_that_prints(monkeypatch, tmp_path, ["phase-start"],
                                     result_record("Options A, B or C.\n\nWhich option do you want?"))

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    posted = [call for call in gh_calls if call[:2] == ["api", "repos/{owner}/{repo}/issues/4242/comments"]]
    bodies = [arg for call in posted for arg in call if arg.startswith("body=")]
    assert (code, [call for call in gh_calls if call[:1] == ["issue"]], len(bodies),
            "Which option do you want?" in "".join(bodies), "Options A, B or C." in "".join(bodies)) == (
        0, [], 1, True, False), stderr + repr(gh_calls)


def test_cli_a_needs_user_comment_that_github_refuses_is_reported_on_stderr_naming_the_issue_and_the_exit_code_stays_0_1974(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    github = run_conductor.github
    conductor_that_prints(monkeypatch, tmp_path, ["phase-start"], result_record("Which option do you want?"))

    def refuse(number, body):
        raise github.NoAnswer("")

    monkeypatch.setattr(github, "gh_issue_comment", refuse)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (code, "needs-user comment" in stderr and "4242" in stderr) == (0, True), stderr


def test_cli_a_conductor_exiting_0_over_an_open_log_whose_issue_thread_already_carries_a_done_comment_gets_no_needs_user_bail_and_no_comment_2070(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    gh_calls = conductor_that_prints(monkeypatch, tmp_path, ["done", "resume"],
                                     result_record("Which option do you want?"))
    done = "### ✅ Done\n\nhttps://github.com/ztrange/veri/pull/2066"
    thread = json.dumps({"comments": [{"body": done}], "body": done})
    recorded = subprocess.run

    def gh_answering_the_thread(args, *a, **kwargs):
        args = list(args)
        if args[:1] == ["gh"] and "needs-user" not in " ".join(args) and "comment" not in args[1:2] and not any(
                arg.startswith("body=") for arg in args):
            gh_calls.append(args[1:])
            return subprocess.CompletedProcess(args, 0, thread.encode() if not kwargs.get("text") else thread, b"")
        return recorded(args, *a, **kwargs)

    monkeypatch.setattr(subprocess, "run", gh_answering_the_thread)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    posted = [call for call in gh_calls if "needs-user" in " ".join(call)]
    assert (code, [r.get("event") for r in events_named(tmp_path)], posted) == (0, ["done", "resume"], []), stderr


def test_cli_a_resumed_run_stopping_without_a_verdict_still_bails_needs_user_and_comments_when_the_only_done_on_the_thread_predates_its_last_resume_event_2238(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    gh_calls = conductor_that_prints(monkeypatch, tmp_path, [], result_record("Which option do you want?"))
    log = tmp_path / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text('{"event": "done", "ts": 1761000000}\n{"event": "resume", "ts": 1761100000}\n')
    earlier_done = {"body": "### ✅ Done\n\nhttps://github.com/ztrange/veri/pull/2066",
                    "created_at": "2025-10-20T22:00:00Z"}
    thread = json.dumps([earlier_done])
    recorded = subprocess.run

    def gh_answering_the_thread(args, *a, **kwargs):
        args = list(args)
        if args[:1] == ["gh"] and "needs-user" not in " ".join(args) and "comment" not in args[1:2] and not any(
                arg.startswith("body=") for arg in args):
            gh_calls.append(args[1:])
            return subprocess.CompletedProcess(args, 0, thread.encode() if not kwargs.get("text") else thread, b"")
        return recorded(args, *a, **kwargs)

    monkeypatch.setattr(subprocess, "run", gh_answering_the_thread)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    posted = [call for call in gh_calls if "needs-user" in " ".join(call)]
    last = json.loads(log.read_text().splitlines()[-1])
    assert (code, last.get("event"), last.get("cause"), len(posted)) == (0, "bail", "needs-user", 1), stderr + repr(gh_calls)


def test_cli_a_done_comment_that_is_comment_101_or_later_on_a_thread_served_over_several_pages_still_suppresses_the_needs_user_bail_and_comment_2238(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    gh_calls = conductor_that_prints(monkeypatch, tmp_path, ["done", "resume"],
                                     result_record("Which option do you want?"))
    chatter = [{"body": "comment %d" % n, "created_at": "2099-01-01T00:00:00Z"} for n in range(100)]
    done = {"body": "### ✅ Done\n\nhttps://github.com/ztrange/veri/pull/2066", "created_at": "2099-01-02T00:00:00Z"}
    pages = {"1": chatter, "2": [done]}
    recorded = subprocess.run

    def gh_serving_the_thread_by_page(args, *a, **kwargs):
        args = list(args)
        if args[:1] == ["gh"] and "needs-user" not in " ".join(args) and "comment" not in args[1:2] and not any(
                arg.startswith("body=") for arg in args):
            gh_calls.append(args[1:])
            page = (re.search(r"[?&]page=(\d+)", args[-1]) or [None, "1"])[1]
            served = json.dumps(pages.get(page, []))
            return subprocess.CompletedProcess(args, 0, served.encode() if not kwargs.get("text") else served, b"")
        return recorded(args, *a, **kwargs)

    monkeypatch.setattr(subprocess, "run", gh_serving_the_thread_by_page)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    posted = [call for call in gh_calls if "needs-user" in " ".join(call)]
    assert (code, [r.get("event") for r in events_named(tmp_path)], posted) == (0, ["done", "resume"], []), stderr


def test_cli_a_launch_with_veri_model_conductor_set_records_that_model_in_tdd_issue_n_conductor_model_under_tdd_issue_2308(
        tmp_path, monkeypatch, run_cli):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    monkeypatch.setenv("VERI_MODEL_CONDUCTOR", "sonnet")
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    fake_claude_exiting(monkeypatch, 0, 0)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    code, _, _ = run_cli(run_conductor, ["4242"], cwd=cwd)

    record = cwd / ".tdd" / "issue-4242-conductor-model"
    assert (code, record.read_text().strip() if record.is_file() else None) == (0, "sonnet")


def test_main_with_the_issue_body_fetch_unanswered_writes_one_skip_line_on_stderr_and_still_launches_the_conductor_issue_2373(
        tmp_path, monkeypatch, capfdbinary, reaches_issue_body_boundary):
    import github
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
    (skill / "SKILL.md").write_text("# the procedure, read from SKILL.md\n")
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_conductor_2373", str(skill / "scripts" / "veri" / "run_conductor.py"))
    run_conductor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_conductor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)

    def refused(number, field):
        raise github.NoAnswer("")

    monkeypatch.setattr(github, "gh_issue_view", refused)
    launches = fake_claude_launch(monkeypatch)

    code = run_conductor.main(["4242"])

    stderr = capfdbinary.readouterr().err.decode(errors="replace")
    skips = [line for line in stderr.splitlines() if "issue body unavailable" in line]
    assert skips == ["run-conductor.sh: issue body unavailable, Requirements row IDs unchecked"]
    assert code == 0
    assert len(after_update_veri(launches)) == 1


def test_main_with_a_requirements_row_id_of_bare_next_refuses_in_preflight_naming_it_and_launches_no_conductor_issue_2373(
        tmp_path, monkeypatch, capfdbinary, reaches_issue_body_boundary):
    import github
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
    (skill / "SKILL.md").write_text("# the procedure, read from SKILL.md\n")
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_conductor_2373_bare_next", str(skill / "scripts" / "veri" / "run_conductor.py"))
    run_conductor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_conductor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    body = ("## Requirements\n\n### skills/tdd/SKILL.md\n\n| ID | Requirement | Why |\n| --- | --- | --- |\n"
            "| SK1 | a well-formed row | because |\n| <next> | a bare row | because |\n")
    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: body if field == "body" else "")
    launches = fake_claude_launch(monkeypatch)

    code = run_conductor.main(["4242"])

    stderr = capfdbinary.readouterr().err.decode(errors="replace")
    assert (code, len(without_update_veri(launches)), "<next>" in stderr) == (2, 0, True)


def test_main_with_well_formed_requirements_rows_beside_other_tables_launches_the_conductor_once_issue_2373(
        tmp_path, monkeypatch, capfdbinary, reaches_issue_body_boundary):
    import github
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
    (skill / "SKILL.md").write_text("# the procedure, read from SKILL.md\n")
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_conductor_2373_well_formed", str(skill / "scripts" / "veri" / "run_conductor.py"))
    run_conductor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_conductor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    body = ("## Observed\n\n| Step | Cost |\n| --- | --- |\n| one | cheap |\n\n"
            "## Requirements\n\n| ID | Requirement | Why |\n| --- | --- | --- |\n| <next> | above any heading | because |\n\n"
            "### skills/tdd/SKILL.md\n\n| ID | Requirement | Why |\n| --- | --- | --- |\n"
            "| SK1 | a numbered row | because |\n| SK<next> | a next row | because |\n")
    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: body if field == "body" else "")
    launches = fake_claude_launch(monkeypatch)

    code = run_conductor.main(["4242"])

    capfdbinary.readouterr()
    assert (code, len(after_update_veri(launches))) == (0, 1)


def test_main_with_an_empty_issue_body_from_gh_writes_only_the_skip_line_on_stderr_and_still_launches_the_conductor_issue_2373(
        tmp_path, monkeypatch, capfdbinary, reaches_issue_body_boundary):
    import types
    import github
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
    (skill / "SKILL.md").write_text("# the procedure, read from SKILL.md\n")
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_conductor_2373_empty", str(skill / "scripts" / "veri" / "run_conductor.py"))
    run_conductor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_conductor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(github, "gh_api", lambda path, stderr=None: types.SimpleNamespace(returncode=0, stdout="", stderr=""))
    launches = fake_claude_launch(monkeypatch)

    code = run_conductor.main(["4242"])

    stderr = capfdbinary.readouterr().err.decode(errors="replace")
    issue_body_lines = [line for line in stderr.splitlines() if "issue body" in line or "JSONDecodeError" in line]
    assert issue_body_lines == ["run-conductor.sh: issue body unavailable, Requirements row IDs unchecked"]
    assert (code, len(after_update_veri(launches))) == (0, 1)


def test_main_with_a_non_json_issue_body_from_gh_writes_only_the_skip_line_on_stderr_and_still_launches_the_conductor_issue_2373(
        tmp_path, monkeypatch, capfdbinary, reaches_issue_body_boundary):
    import types
    import github
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
    (skill / "SKILL.md").write_text("# the procedure, read from SKILL.md\n")
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_conductor_2373_non_json", str(skill / "scripts" / "veri" / "run_conductor.py"))
    run_conductor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_conductor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(github, "gh_api", lambda path, stderr=None: types.SimpleNamespace(returncode=0, stdout="<html>502 Bad Gateway</html>\n", stderr=""))
    launches = fake_claude_launch(monkeypatch)

    code = run_conductor.main(["4242"])

    stderr = capfdbinary.readouterr().err.decode(errors="replace")
    issue_body_lines = [line for line in stderr.splitlines() if "issue body" in line or "JSONDecodeError" in line]
    assert issue_body_lines == ["run-conductor.sh: issue body unavailable, Requirements row IDs unchecked"]
    assert (code, len(after_update_veri(launches))) == (0, 1)


def test_cli_with_the_issue_body_fetch_unanswered_exits_with_the_conductors_own_code_not_2_issue_2373(
        tmp_path, monkeypatch, run_cli, reaches_issue_body_boundary):
    import github
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    launches = fake_claude_exiting(monkeypatch, 17, 0)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    def refused(number, field):
        raise github.NoAnswer("")

    monkeypatch.setattr(github, "gh_issue_view", refused)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, len(launches)) == (17, 1), stderr


def test_main_with_multi_digit_and_prefix_next_requirements_row_ids_passes_the_row_id_check_and_launches_the_conductor_issue_2373(
        tmp_path, monkeypatch, capfdbinary, reaches_issue_body_boundary):
    import github
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "scripts" / "veri" / "run_conductor.py").symlink_to(SCRIPTS / "veri" / "run_conductor.py")
    (skill / "SKILL.md").write_text("# the procedure, read from SKILL.md\n")
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_conductor_2373_ids", str(skill / "scripts" / "veri" / "run_conductor.py"))
    run_conductor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_conductor)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    body = ("## Requirements\n\n### scripts/veri/run_conductor.py\n\n| ID | Requirement | Why |\n| --- | --- | --- |\n"
            "| RC12 | a multi-digit row | because |\n| RC<next> | a next row | because |\n")
    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: body if field == "body" else "")
    launches = fake_claude_launch(monkeypatch)

    code = run_conductor.main(["4242"])

    stderr = capfdbinary.readouterr().err.decode(errors="replace")
    assert (code, len(after_update_veri(launches)), "neither" in stderr) == (0, 1, False)


def test_main_runs_the_procedure_from_the_recorded_skill_commit_refuses_an_unresolvable_one_with_2_and_re_pins_only_under_veri_new_skill_2483(
        tmp_path, monkeypatch, capfdbinary):
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    head = "1111111111111111111111111111111111111111"
    recorded = "2222222222222222222222222222222222222222"
    run_conductor = importlib.import_module("veri.run_conductor")
    scenarios = {
        "recorded": (None, recorded, {recorded + "^{commit}"}),
        "unresolvable": (None, recorded, set()),
        "re-pin": ("1", recorded, set()),
    }
    answers = {}
    for name, (new_skill, record, accepted) in scenarios.items():
        cwd = tmp_path / name
        (cwd / ".tdd").mkdir(parents=True)
        monkeypatch.chdir(cwd)
        if new_skill:
            monkeypatch.setenv("VERI_NEW_SKILL", new_skill)
        else:
            monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
        path = cwd / ".tdd" / "issue-4242-skill-commit"
        path.write_text(record + "\n")
        calls = fake_pin(monkeypatch, head, accepted)
        snapshots, launches = fake_snapshot(monkeypatch, calls, 0, 0)
        code = run_conductor.main(["4242"])
        capfdbinary.readouterr()
        archived = [call[4] for call in snapshots if call[3:4] == ["archive"]]
        answers[name] = (code, path.read_text(), archived, [launch["VERI_SKILL_COMMIT"] for launch in launches])
    assert answers == {
        "recorded": (0, recorded + "\n", [recorded], [recorded]),
        "unresolvable": (2, recorded + "\n", [], []),
        "re-pin": (0, head + "\n", [head], [head]),
    }
