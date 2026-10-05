"""In-process cases for veri/parallel_conductors.py, the module parallel-conductors.sh is a shim over."""
import importlib
import json
import os
import pathlib
import shutil
import signal
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


@pytest.mark.parametrize("env, words, run_timeout", [
    ({"VERI_HEARTBEAT": "5", "VERI_POLL": "2"}, ["VERI_HEARTBEAT=5", "VERI_POLL=2"], "14400"),
    ({"VERI_POLL": "3", "VERI_STUCK_RETRIES": "4", "VERI_TIMEOUT": "", "VERI_HEARTBEAT": "6",
      "VERI_RUN_TIMEOUT": "60"},
     ["VERI_HEARTBEAT=6", "VERI_TIMEOUT=", "VERI_STUCK_RETRIES=4", "VERI_POLL=3"], "60"),
    ({}, [], "14400"),
], ids=["two-set", "all-set", "none-set"])
def test_each_issue_launches_as_supervise_env_run_conductor_with_the_caller_s_four_tunables_as_words_and_the_run_timeout_in_supervise_s_environment(
        env, words, run_timeout, capsys, monkeypatch, tmp_path, parallel_conductors):
    for name in TUNABLES:
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(gh))
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)
    monkeypatch.chdir(work)
    log = work / ".tdd" / "conductor-7.log"
    log.write_bytes(b'{"type":"assistant","cache_read_input_tokens":1,"cache_creation_input_tokens":1}\n')
    stale_at_launch = []

    def on_launch(sup):
        stale_at_launch.append(log.exists())
        log.write_bytes(b"")
        sup.exit(0)

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None)
    faked_run, faked_popen = subprocess.run, subprocess.Popen
    solvable_calls, launches = [], []

    def recording_run(args, *rest, **kwargs):
        if pathlib.Path(args[0]).name == "solvable-issues.sh":
            solvable_calls.append((list(args), dict(kwargs)))
        return faked_run(args, *rest, **kwargs)

    def recording_popen(args, *rest, **kwargs):
        launches.append((list(args), dict(kwargs), dict(kwargs.get("env") or os.environ)))
        return faked_popen(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", recording_run)
    monkeypatch.setattr(subprocess, "Popen", recording_popen)

    parallel_conductors.main([])
    out, _ = capsys.readouterr()

    scripts = os.path.dirname(os.path.dirname(os.path.abspath(parallel_conductors.__file__)))
    assert [argv for argv, _, _ in launches] == [
        [os.path.join(scripts, "supervise.sh"), "conductor-7", "env",
         "-u", "VERI_HEARTBEAT", "-u", "VERI_TIMEOUT", "-u", "VERI_STUCK_RETRIES", "-u", "VERI_POLL",
         *words, os.path.join(scripts, "run-conductor.sh"), "7"]]
    _, kwargs, launch_env = launches[0]
    assert (launch_env.get("VERI_HEARTBEAT"), launch_env.get("VERI_TIMEOUT"),
            launch_env.get("VERI_STUCK_RETRIES")) == (run_timeout, run_timeout, "0")
    assert (kwargs.get("stdout"), kwargs.get("stderr")) == (subprocess.DEVNULL, None)
    assert stale_at_launch == [False]
    assert "context 7 2" not in out.splitlines()
    assert solvable_calls and all(argv == [os.path.join(scripts, "solvable-issues.sh")] for argv, _ in solvable_calls)
    assert [(kw.get("stdout"), kw.get("stderr"), kw.get("capture_output", False)) for _, kw in solvable_calls] == [
        (subprocess.PIPE, None, False)] * len(solvable_calls)


@pytest.mark.parametrize("env, answers, exits, launched, slots, stopped, code", [
    ({"VERI_PARALLEL": "2"}, [(0, "7 8\n")], {}, ["7", "8"], 2, "stopped: nothing solvable", 0),
    ({}, [(0, "7 8\n"), (0, "7\t9\n8\n"), (1, "")], {}, ["7", "9"], 1, "stopped: nothing solvable", 0),
    ({"VERI_PARALLEL": "3", "VERI_MAX_ISSUES": "2"}, [(0, "7 8 9\n")], {}, ["7", "8"], 2,
     "stopped: VERI_MAX_ISSUES reached", 0),
    ({}, [(2, "")], {}, [], 0, "stopped: solvable-issues.sh could not answer", 2),
    ({}, [(5, "")], {}, [], 0, "stopped: nothing solvable", 3),
    ({"VERI_PARALLEL": "2"}, [(0, "7\n"), (2, "")], {"7": 2}, ["7"], 1, None, 2),
    ({}, [(0, "7\n"), (1, "")], {"7": 2}, ["7"], 1, None, 1),
], ids=["two-slots", "afresh-first-unlaunched", "max-issues-cap", "plumbing", "nothing-launched",
        "plumbing-beats-failure", "failure"])
def test_slots_fill_from_a_fresh_solvable_issues_answer_up_to_the_cap_and_the_exit_code_ranks_plumbing_failure_nothing_launched_then_done(
        env, answers, exits, launched, slots, stopped, code, capsys, monkeypatch, tmp_path, parallel_conductors):
    for name in TUNABLES:
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(gh))
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)
    monkeypatch.chdir(work)
    lock = threading.Lock()
    lives, numbers, in_flight_at_launch, sleeps = {}, [], [], [0]

    def on_launch(sup):
        n = sup.args[-1]
        with lock:
            in_flight_at_launch.append(1 + sum(1 for s in lives if s.returncode is None))
            lives[sup] = sleeps[0] + 5
            numbers.append(n)
        (work / ".tdd" / ("conductor-%s.log" % n)).write_bytes(b"")

    def on_sleep(supervisors):
        with lock:
            sleeps[0] += 1
            for sup, until in lives.items():
                if sup.returncode is None and sleeps[0] >= until:
                    sup.exit(exits.get(sup.args[-1], 0))

    _boundaries(monkeypatch, tmp_path, on_launch, on_sleep)
    faked_run = subprocess.run
    calls = []

    def answering_run(args, *rest, **kwargs):
        if pathlib.Path(args[0]).name != "solvable-issues.sh":
            return faked_run(args, *rest, **kwargs)
        rc, out = answers[min(len(calls), len(answers) - 1)]
        calls.append(args)
        return subprocess.CompletedProcess(args, rc, out if kwargs.get("text") else out.encode(), None)

    monkeypatch.setattr(subprocess, "run", answering_run)

    returned = parallel_conductors.main([])
    out, _ = capsys.readouterr()

    assert (numbers, max(in_flight_at_launch, default=0), returned) == (launched, slots, code)
    if stopped is not None:
        assert [line for line in out.splitlines() if line.startswith("stopped: ")] == [stopped]
    assert (work / ".tdd" / "parallel.exit").read_text() == "%d\n" % code


@pytest.mark.parametrize("budget, kills, launched, restarted", [
    ("100", [(FakeSupervisor.pid, signal.SIGTERM)], ["7", "7"], ["restarted 7"]),
    ("101", [], ["7"], []),
], ids=["over-budget", "at-budget-disarms"])
def test_a_user_line_after_the_step_done_call_stops_a_conductor_over_the_context_budget_and_relaunches_it_past_the_cap(
        budget, kills, launched, restarted, capsys, monkeypatch, tmp_path, parallel_conductors):
    for name in TUNABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("VERI_CONDUCTOR_CTX_BUDGET", budget)
    monkeypatch.setenv("VERI_MAX_ISSUES", "1")
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(gh))
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)
    monkeypatch.chdir(work)
    log = work / ".tdd" / "conductor-7.log"
    step_done = (b'{"type":"assistant","message":{"content":[{"type":"tool_use","input":{"command":'
                 b'"skills/tdd/scripts/event.sh step-done 3"}}],"usage":{"cache_creation_input_tokens":1,'
                 b'"cache_read_input_tokens":100}}}\n')
    later = b'{"type":"assistant","message":{"usage":{"cache_creation_input_tokens":0,"cache_read_input_tokens":500}}}\n'
    user = b'{"type":"user","message":{"content":[{"type":"tool_result","content":"ok"}]}}\n'
    launches, sleeps = [], [0]

    def on_launch(sup):
        launches.append(sup.args[-1])
        if len(launches) == 1:
            log.write_bytes(step_done)
        else:
            log.write_bytes(b"")
            sup.exit(0)

    def on_sleep(supervisors):
        first = supervisors[0]
        if first.returncode is not None:
            return
        sleeps[0] += 1
        if sleeps[0] == 1:
            with open(log, "ab") as f:
                f.write(user)
        elif sleeps[0] == 2:
            with open(log, "ab") as f:
                f.write(later + user)
        elif sleeps[0] >= 5:
            first.exit(0)

    supervisors = _boundaries(monkeypatch, tmp_path, on_launch, on_sleep, solvable=(0, "7 8\n"))
    sent = []

    def recording_kill(pid, sig):
        sent.append((pid, sig))
        live = [s for s in supervisors if s.pid == pid and s.returncode is None]
        if not live:
            raise ProcessLookupError(pid)
        if sig == signal.SIGTERM:
            live[0].exit(143)

    monkeypatch.setattr(os, "kill", recording_kill)

    code = parallel_conductors.main([])
    out, _ = capsys.readouterr()

    assert ([s for s in sent if s[1] == signal.SIGTERM], launches,
            [line for line in out.splitlines() if line.startswith("restarted ")]) == (kills, launched, restarted)
    assert code in (0, 1, 2, 3)
