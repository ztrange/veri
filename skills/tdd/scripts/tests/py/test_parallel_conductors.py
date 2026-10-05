"""In-process cases for veri/parallel_conductors.py, the module parallel-conductors.sh is a shim over."""
import importlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import threading
import time

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

TUNABLES = ("VERI_PARALLEL", "VERI_MAX_ISSUES", "VERI_CONDUCTOR_CTX_BUDGET", "VERI_RUN_TIMEOUT",
            "VERI_POLL", "VERI_HEARTBEAT", "VERI_TIMEOUT", "VERI_STUCK_RETRIES", "VERI_GH_JSON")


@pytest.fixture
def parallel_conductors():
    return importlib.import_module("veri.parallel_conductors")


class FakeSupervisor:
    """A supervise.sh that is alive until the faked clock lets it exit."""

    pid = 424242

    def __init__(self, args):
        self.args = args
        self.returncode = None
        self.exited = threading.Event()

    def exit(self, code):
        self.returncode = code
        self.exited.set()

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        if not self.exited.wait(10 if timeout is None else timeout):
            raise subprocess.TimeoutExpired(self.args, timeout)
        return self.returncode


def _boundaries(monkeypatch, tmp_path, on_launch, on_sleep, solvable=(0, "7\n")):
    """Fake git, solvable-issues.sh (answering 7 by default), supervise.sh, os.kill and the clock."""
    common = tmp_path / ".git"
    (common / "info").mkdir(parents=True)
    supervisors = []

    def answer(args):
        name = pathlib.Path(args[0]).name
        if name == "solvable-issues.sh":
            return subprocess.CompletedProcess(args, solvable[0], solvable[1], "")
        if name == "git" and list(args[1:]) == ["rev-parse", "--git-common-dir"]:
            return subprocess.CompletedProcess(args, 0, "%s\n" % common, "")
        raise AssertionError("unexpected subprocess call: %r" % (args,))

    def fake_run(args, *rest, **kwargs):
        done = answer(args)
        if kwargs.get("check") and done.returncode:
            raise subprocess.CalledProcessError(done.returncode, args, done.stdout)
        if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
            done = subprocess.CompletedProcess(args, done.returncode, done.stdout.encode(), b"")
        return done

    def fake_check_output(args, *rest, **kwargs):
        return fake_run(args, *rest, check=True, **kwargs).stdout

    def fake_popen(args, *rest, **kwargs):
        if pathlib.Path(args[0]).name != "supervise.sh":
            raise AssertionError("unexpected subprocess.Popen call: %r" % (args,))
        sup = FakeSupervisor(args)
        supervisors.append(sup)
        on_launch(sup)
        return sup

    def fake_kill(pid, sig):
        live = [s for s in supervisors if s.pid == pid and s.returncode is None]
        if not live:
            raise ProcessLookupError(pid)

    clock = {"now": 1000.0}

    def fake_sleep(seconds):
        clock["now"] += seconds if seconds else 0.001
        on_sleep(supervisors)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(os, "kill", fake_kill)
    monkeypatch.setattr(time, "sleep", fake_sleep)
    monkeypatch.setattr(time, "monotonic", lambda: clock["now"])
    monkeypatch.setattr(time, "time", lambda: clock["now"])
    return supervisors


def test_an_assistant_event_the_conductor_writes_in_two_pieces_still_prints_one_context_line_for_the_whole_event(
        capsys, monkeypatch, tmp_path, parallel_conductors):
    for name in TUNABLES:
        monkeypatch.delenv(name, raising=False)
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text(json.dumps(
        [{"body": "Closes #7", "isDraft": False, "url": "https://github.com/o/r/pull/70"}]))
    monkeypatch.setenv("VERI_GH_JSON", str(gh))
    work = tmp_path / "repo"
    work.mkdir()
    monkeypatch.chdir(work)
    log = work / ".tdd" / "conductor-7.log"
    head = b'{"type":"assistant","message":{"role":"assistant",'
    tail = b'"usage":{"input_tokens":7,"cache_creation_input_tokens":3438,"cache_read_input_tokens":50000,"output_tokens":120}}}\n'
    sleeps_after_head = []

    def on_launch(sup):
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_bytes(head)

    def on_sleep(supervisors):
        if not supervisors or supervisors[-1].returncode is not None:
            return
        sleeps_after_head.append(time.monotonic())
        if len(sleeps_after_head) == 1:
            with open(log, "ab") as f:
                f.write(tail)
        elif len(sleeps_after_head) == 2:
            supervisors[-1].exit(0)

    _boundaries(monkeypatch, tmp_path, on_launch, on_sleep)

    code = parallel_conductors.main([])
    out, _ = capsys.readouterr()

    assert len(sleeps_after_head) == 2
    assert [line for line in out.splitlines() if line.startswith("context ")] == ["context 7 53438"]
    assert code in (0, 1, 2, 3)


def test_a_solvable_issues_exit_other_than_0_and_2_stops_with_nothing_solvable_and_returns_3(
        capsys, monkeypatch, tmp_path, parallel_conductors):
    for name in TUNABLES:
        monkeypatch.delenv(name, raising=False)
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(gh))
    work = tmp_path / "repo"
    work.mkdir()
    monkeypatch.chdir(work)

    def on_launch(sup):
        raise AssertionError("nothing should launch when solvable-issues.sh exits 5")

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None, solvable=(5, ""))

    code = parallel_conductors.main([])
    out, _ = capsys.readouterr()

    assert code == 3
    assert "stopped: nothing solvable" in out.splitlines()


def test_a_failing_removal_of_the_run_s_scratch_directory_at_exit_returns_2_and_leaves_parallel_exit_holding_the_code_written_before_it(
        capsys, monkeypatch, tmp_path, parallel_conductors):
    for name in TUNABLES:
        monkeypatch.delenv(name, raising=False)
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(gh))
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)
    monkeypatch.chdir(work)
    real_rmtree = shutil.rmtree
    removals = []

    def failing_rmtree(path, *args, **kwargs):
        removals.append(str(path))
        raise OSError("rm: %s: cannot remove" % path)

    def on_launch(sup):
        raise AssertionError("nothing should launch when solvable-issues.sh exits 5")

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None, solvable=(5, ""))
    monkeypatch.setattr(shutil, "rmtree", failing_rmtree)

    code = parallel_conductors.main([])
    capsys.readouterr()
    monkeypatch.undo()
    for path in removals:
        real_rmtree(path, ignore_errors=True)

    assert code == 2
    assert removals, "the run's scratch directory was never removed"
    assert (work / ".tdd" / "parallel.exit").read_text() == "3\n"


@pytest.mark.parametrize("env, refusal", [
    ({"VERI_CONDUCTOR_CTX_BUDGET": "-1", "VERI_PARALLEL": "0", "VERI_MAX_ISSUES": ""},
     "parallel-conductors: VERI_CONDUCTOR_CTX_BUDGET must be a whole number >= 0: '-1'"),
    ({"VERI_CONDUCTOR_CTX_BUDGET": "", "VERI_PARALLEL": "", "VERI_MAX_ISSUES": "x"},
     "parallel-conductors: VERI_PARALLEL must be a whole number >= 1: ''"),
    ({"VERI_PARALLEL": "0"}, "parallel-conductors: VERI_PARALLEL must be a whole number >= 1: '0'"),
    ({"VERI_PARALLEL": "two", "VERI_MAX_ISSUES": "0"},
     "parallel-conductors: VERI_PARALLEL must be a whole number >= 1: 'two'"),
    ({"VERI_CONDUCTOR_CTX_BUDGET": "007", "VERI_MAX_ISSUES": ""},
     "parallel-conductors: VERI_MAX_ISSUES must be a whole number >= 1: ''"),
    ({"VERI_PARALLEL": "007", "VERI_MAX_ISSUES": "0"},
     "parallel-conductors: VERI_MAX_ISSUES must be a whole number >= 1: '0'"),
    ({"VERI_CONDUCTOR_CTX_BUDGET": "0", "VERI_PARALLEL": "007", "VERI_MAX_ISSUES": "007",
      "VERI_RUN_TIMEOUT": "soon", "VERI_POLL": "often"}, None),
])
def test_tunables_are_validated_in_order_naming_only_the_first_bad_one_and_a_refusal_returns_2_before_solvable_issues_runs(
        env, refusal, capsys, monkeypatch, tmp_path, parallel_conductors):
    for name in TUNABLES:
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(gh))
    work = tmp_path / "repo"
    work.mkdir()
    monkeypatch.chdir(work)

    def on_launch(sup):
        raise AssertionError("nothing should launch when solvable-issues.sh exits 5")

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None, solvable=(5, ""))
    faked_run = subprocess.run
    solvable_calls = []

    def recording_run(args, *rest, **kwargs):
        if pathlib.Path(args[0]).name == "solvable-issues.sh":
            solvable_calls.append(args)
        return faked_run(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", recording_run)

    code = parallel_conductors.main([])
    out, err = capsys.readouterr()

    if refusal is None:
        assert (code, err, len(solvable_calls)) == (3, "", 1)
    else:
        assert (code, out, err.splitlines(), solvable_calls) == (2, "", [refusal], [])
        assert (work / ".tdd" / "parallel.exit").read_text() == "2\n"


@pytest.mark.parametrize("env, info, before, git_status, code, after", [
    ({}, None, None, 0, 3, ".tdd/*\n"),
    ({}, "dir", "", 0, 3, ".tdd/*\n"),
    ({}, "dir", "a\nb", 0, 3, "a\nb\n.tdd/*\n"),
    ({}, "dir", "a\nb\n", 0, 3, "a\nb\n.tdd/*\n"),
    ({}, "dir", "x.tdd/*\n.tdd/*x\n", 0, 3, "x.tdd/*\n.tdd/*x\n.tdd/*\n"),
    ({}, "dir", "a\n.tdd/*\nb", 0, 3, "a\n.tdd/*\nb"),
    ({"VERI_PARALLEL": "0"}, None, None, 0, 2, ".tdd/*\n"),
    ({"VERI_CONDUCTOR_CTX_BUDGET": "-1"}, "dir", "a", 0, 2, "a\n.tdd/*\n"),
    ({}, "dir", "a", 128, 2, "a"),
], ids=["no-info-dir", "empty", "no-final-newline", "final-newline", "not-a-whole-line",
        "present-already", "refused-tunable", "refused-budget", "git-128"])
def test_the_exclude_gains_tdd_once_as_a_whole_line_before_any_tunable_is_validated_and_git_failing_returns_2_with_no_parallel_exit(
        env, info, before, git_status, code, after, capsys, monkeypatch, tmp_path, parallel_conductors):
    for name in TUNABLES:
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(gh))
    work = tmp_path / "repo"
    work.mkdir()
    monkeypatch.chdir(work)

    def on_launch(sup):
        raise AssertionError("nothing should launch when solvable-issues.sh exits 5")

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None, solvable=(5, ""))
    exclude = tmp_path / ".git" / "info" / "exclude"
    if info is None:
        shutil.rmtree(exclude.parent)
    if before is not None:
        exclude.write_bytes(before.encode())
    faked_run, faked_check_output = subprocess.run, subprocess.check_output

    def git_failing(args):
        return pathlib.Path(args[0]).name == "git" and git_status

    def run(args, *rest, **kwargs):
        if not git_failing(args):
            return faked_run(args, *rest, **kwargs)
        if kwargs.get("check"):
            raise subprocess.CalledProcessError(git_status, args)
        text = kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")
        return subprocess.CompletedProcess(args, git_status, "" if text else b"", "" if text else b"")

    def check_output(args, *rest, **kwargs):
        if git_failing(args):
            raise subprocess.CalledProcessError(git_status, args)
        return faked_check_output(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(subprocess, "check_output", check_output)

    returned = parallel_conductors.main([])
    capsys.readouterr()

    written = exclude.read_bytes().decode() if exclude.is_file() else None
    assert (returned, written) == (code, after)
    assert (work / ".tdd" / "parallel.exit").is_file() == (git_status == 0)
