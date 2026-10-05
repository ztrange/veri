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
import traceback

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


@pytest.mark.parametrize("max_issues, launched, code", [
    ("010", [str(n) for n in range(1, 9)], 0),
    ("08", [], 3),
    ("09", [], 3),
], ids=["010-is-octal-8", "08-is-no-number", "09-is-no-number"])
def test_veri_max_issues_with_a_leading_zero_is_read_as_bash_s_bare_arithmetic_reads_it(
        max_issues, launched, code, capsys, monkeypatch, tmp_path, parallel_conductors):
    for name in TUNABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("VERI_PARALLEL", "20")
    monkeypatch.setenv("VERI_MAX_ISSUES", max_issues)
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(gh))
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)
    monkeypatch.chdir(work)
    numbers = []

    def on_launch(sup):
        numbers.append(sup.args[-1])
        (work / ".tdd" / ("conductor-%s.log" % sup.args[-1])).write_bytes(b"")
        sup.exit(0)

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None,
                solvable=(0, " ".join(str(n) for n in range(1, 13)) + "\n"))

    returned = parallel_conductors.main([])
    out, _ = capsys.readouterr()

    assert (numbers, [line for line in out.splitlines() if line.startswith("stopped: ")], returned) == (
        launched, ["stopped: VERI_MAX_ISSUES reached"], code)


# Observed running parallel-conductors.sh at 79a9520bf with a conductor at context 50000 after its
# step-done call: VERI_CONDUCTOR_CTX_BUDGET=0100000 stops and relaunches it; 08 and 09 print
# "line 122: ((: 08: value too great for base" on stderr, never stop it, and keep printing its
# context lines; every run exits 0.
@pytest.mark.parametrize("budget, kills, launched, restarted, contexts", [
    ("0100000", [(FakeSupervisor.pid, signal.SIGTERM)], ["7", "7"], ["restarted 7"], ["context 7 50000"]),
    ("08", [], ["7"], [], ["context 7 50000", "context 7 500"]),
    ("09", [], ["7"], [], ["context 7 50000", "context 7 500"]),
], ids=["0100000-is-octal-32768", "08-never-stops", "09-never-stops"])
def test_veri_conductor_ctx_budget_with_a_leading_zero_is_read_as_bash_s_bare_arithmetic_reads_it(
        budget, kills, launched, restarted, contexts, capsys, monkeypatch, tmp_path, parallel_conductors):
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
                 b'"skills/tdd/scripts/event.sh step-done 3"}}],"usage":{"cache_creation_input_tokens":100,'
                 b'"cache_read_input_tokens":49900}}}\n')
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
            [line for line in out.splitlines() if line.startswith("restarted ")],
            [line for line in out.splitlines() if line.startswith("context ")], code) == (
        kills, launched, restarted, contexts, 0)


def test_the_report_prints_one_line_per_issue_in_launch_order_killed_ahead_of_any_pr_parked_never_then_the_first_open_pr_closing_it_done_or_bailed(
        capsys, monkeypatch, tmp_path, parallel_conductors):
    for name in TUNABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("VERI_RUN_TIMEOUT", "60")
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text(json.dumps([
        {"body": "Closes #21", "isDraft": False, "url": "https://github.com/o/r/pull/121"},
        {"body": "Closes #3", "isDraft": False, "url": "https://github.com/o/r/pull/103"},
        {"body": "Fixes the thing.\n\nCloses #14", "isDraft": False, "url": "https://github.com/o/r/pull/114"},
        {"body": "Closes #5", "draft": False, "html_url": "https://github.com/o/r/pull/105"},
        {"body": "Closes #6", "isDraft": False},
        {"body": "Closes #7", "isDraft": True, "url": "https://github.com/o/r/pull/107"},
        {"body": "Closes #8", "draft": True, "html_url": "https://github.com/o/r/pull/108"},
        {"body": "Closes #9", "isDraft": True, "url": "https://github.com/o/r/pull/109"},
        {"body": "closes #10 and Closes #100", "isDraft": False, "url": "https://github.com/o/r/pull/110"},
        {"body": None, "isDraft": False, "url": "https://github.com/o/r/pull/1"},
        {"body": "Closes #110 and Closes #11", "isDraft": False, "draft": True,
         "html_url": "https://github.com/o/r/pull/111", "url": "https://api.github.com/o/r/pulls/111"},
        {"body": "Closes #11", "isDraft": False, "url": "https://github.com/o/r/pull/211"},
        {"body": "Closes #12", "isDraft": True, "url": "https://github.com/o/r/pull/112"},
    ]))
    monkeypatch.setenv("VERI_GH_JSON", str(gh))
    work = tmp_path / "repo"
    (work / ".tdd" / "parked").mkdir(parents=True)
    (work / ".tdd" / "parked" / "3.md").write_text("parked\n")
    events = {"7": '{"event": "red"}\n{"event": "bail", "why": "stuck"}\n',
              "8": '{"event": "bail", "why": "stuck"}\n{"event": "resume"}\n',
              "9": '{"event":"bail"}\n'}
    for n, text in events.items():
        (work / ".tdd" / "wt" / n / ".tdd").mkdir(parents=True)
        (work / ".tdd" / "wt" / n / ".tdd" / "events.jsonl").write_text(text)
    monkeypatch.chdir(work)
    order = ["21", "3", "14", "5", "6", "7", "8", "9", "10", "11", "12"]
    numbers = []

    def on_launch(sup):
        n = sup.args[-1]
        numbers.append(n)
        (work / ".tdd" / ("conductor-%s.log" % n)).write_bytes(b"")
        sup.exit(2 if n == "21" else 0)

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None, solvable=(0, " ".join(order) + "\n"))

    parallel_conductors.main(["--continue-on-bail"])
    out, _ = capsys.readouterr()

    assert numbers == order
    assert [line for line in out.splitlines() if line.startswith("#")] == [
        "#21 — killed after 60s",
        "#14 — done https://github.com/o/r/pull/114",
        "#5 — done https://github.com/o/r/pull/105",
        "#6 — done ",
        "#7 — bailed https://github.com/o/r/pull/107",
        "#11 — done https://github.com/o/r/pull/111",
    ]


def test_the_open_pr_list_is_read_through_gh_json_a_no_answer_at_the_report_returns_2_unwritten_at_a_finish_it_decides_over_the_pages_read_and_a_missing_or_non_json_list_is_survived_as_bash_survives_it(
        capsys, monkeypatch, tmp_path, parallel_conductors):
    graphql = ["gh", "pr", "list", "--state", "open", "--limit", "10000", "--json", "body,isDraft,url"]
    rest = "repos/{owner}/{repo}/pulls?state=open&per_page=100&page=%d"
    bailed = json.dumps([{"body": "Closes #7", "draft": True, "html_url": "https://github.com/o/r/pull/107"}])

    def run(name, env, solvable, gh_answer=None, fixture=None):
        for var in TUNABLES + ("VERI_GH_DRIVER",):
            monkeypatch.delenv(var, raising=False)
        for var, value in env.items():
            monkeypatch.setenv(var, value)
        root = tmp_path / name
        work = root / "repo"
        (work / ".tdd" / "wt" / "7" / ".tdd").mkdir(parents=True)
        (work / ".tdd" / "wt" / "7" / ".tdd" / "events.jsonl").write_text('{"event": "red"}\n{"event": "bail"}\n')
        if fixture is not None:
            gh = root / "gh"
            gh.mkdir()
            if fixture:
                (gh / "prs.json").write_text(fixture)
            monkeypatch.setenv("VERI_GH_JSON", str(gh))
        monkeypatch.chdir(work)
        numbers, gh_calls = [], []

        def on_launch(sup):
            numbers.append(sup.args[-1])
            (work / ".tdd" / ("conductor-%s.log" % sup.args[-1])).write_bytes(b"")
            sup.exit(0)

        _boundaries(monkeypatch, root, on_launch, lambda supervisors: None, solvable=solvable)
        faked_run = subprocess.run

        def gh_run(args, *rest_args, **kwargs):
            if args[0] != "gh":
                return faked_run(args, *rest_args, **kwargs)
            gh_calls.append(list(args))
            rc, out = gh_answer(len(gh_calls), list(args))
            return subprocess.CompletedProcess(args, rc, out, "")

        monkeypatch.setattr(subprocess, "run", gh_run)
        try:
            code = parallel_conductors.main([])
        except Exception:
            traceback.print_exc()
            code = 1
        out, err = capsys.readouterr()
        lines = [line for line in out.splitlines() if line.startswith(("#", "stopped:"))]
        return code, lines, err, numbers, gh_calls, (work / ".tdd" / "parallel.exit").exists()

    code, lines, _, numbers, calls, written = run(
        "report-no-answer", {"VERI_GH_DRIVER": "graphql"}, (0, "7\n"), lambda i, args: (1, ""))
    assert (code, lines, written, numbers) == (2, [], False, ["7"])
    assert calls and all(call == graphql for call in calls)

    def paged(i, args):
        if i == 1:
            return 0, bailed + "\n"
        if i == 2:
            return 1, ""
        return (0, bailed + "\n") if i % 2 else (0, "[]\n")

    code, lines, _, numbers, calls, _ = run("finish-no-answer", {}, (0, "7 8\n"), paged)
    assert (code, lines, numbers) == (1, ["#7 — bailed https://github.com/o/r/pull/107", "stopped: #7 bailed"], ["7"])
    assert calls[:2] == [["gh", "api", rest % 1], ["gh", "api", rest % 2]]

    code, lines, err, numbers, _, _ = run("missing-fixture", {}, (0, "7 8\n"), fixture="")
    assert (code, lines, numbers) == (1, [], ["7", "8"])
    assert "Traceback" in err and "FileNotFoundError" in err

    code, lines, err, numbers, _, _ = run("not-json", {}, (0, "7 8\n"), fixture="not json\n")
    assert (code, lines, numbers) == (0, ["stopped: nothing solvable"], ["7", "8"])
    assert "Traceback" in err and "JSONDecodeError" in err


def test_a_finished_sweep_in_launch_order_restarts_past_a_stop_prints_parked_alone_stops_at_the_first_bail_or_kill_and_honours_continue_on_bail_only_as_argv_0(
        capsys, monkeypatch, tmp_path, parallel_conductors):
    step_done = (b'{"type":"assistant","message":{"content":[{"type":"tool_use","input":{"command":'
                 b'"skills/tdd/scripts/event.sh step-done 3"}}],"usage":{"cache_creation_input_tokens":1,'
                 b'"cache_read_input_tokens":100}}}\n')
    user = b'{"type":"user","message":{"content":[{"type":"tool_result","content":"ok"}]}}\n'

    def run(name, argv, env, solvable, exits):
        for var in TUNABLES:
            monkeypatch.delenv(var, raising=False)
        for var, value in env.items():
            monkeypatch.setenv(var, value)
        root = tmp_path / name
        gh = root / "gh"
        gh.mkdir(parents=True)
        (gh / "prs.json").write_text(json.dumps([
            {"body": "Closes #4", "isDraft": True, "url": "https://github.com/o/r/pull/104"},
            {"body": "Closes #6", "isDraft": True, "url": "https://github.com/o/r/pull/106"},
        ]))
        monkeypatch.setenv("VERI_GH_JSON", str(gh))
        work = root / "repo"
        (work / ".tdd" / "parked").mkdir(parents=True)
        (work / ".tdd" / "parked" / "4.md").write_text("parked\n")
        for n in ("4", "6"):
            (work / ".tdd" / "wt" / n / ".tdd").mkdir(parents=True)
            (work / ".tdd" / "wt" / n / ".tdd" / "events.jsonl").write_text('{"event": "red"}\n{"event": "bail"}\n')
        monkeypatch.chdir(work)
        launches = []

        def on_launch(sup):
            n = sup.args[-1]
            launches.append(n)
            sup.pid = 5000 + len(launches)
            log = work / ".tdd" / ("conductor-%s.log" % n)
            if n == "3" and launches.count("3") == 1:
                log.write_bytes(step_done + user)
            else:
                log.write_bytes(b"")
                if n not in exits:
                    sup.exit(0)

        def on_sleep(supervisors):
            for sup in supervisors:
                if sup.returncode is None and sup.args[-1] in exits:
                    sup.exit(exits[sup.args[-1]])

        supervisors = _boundaries(monkeypatch, root, on_launch, on_sleep, solvable=(0, solvable))

        def terminating_kill(pid, sig):
            live = [s for s in supervisors if s.pid == pid and s.returncode is None]
            if not live:
                raise ProcessLookupError(pid)
            if sig == signal.SIGTERM:
                live[0].exit(143)

        monkeypatch.setattr(os, "kill", terminating_kill)
        code = parallel_conductors.main(argv)
        out, _ = capsys.readouterr()
        return code, launches, [line for line in out.splitlines()
                                if line.startswith(("parked ", "restarted ", "#", "stopped: "))]

    assert run("sweep", [], {"VERI_PARALLEL": "4", "VERI_MAX_ISSUES": "4", "VERI_CONDUCTOR_CTX_BUDGET": "100"},
               "4 5 6 3 9\n", {"4": 0, "5": 2, "6": 0}) == (1, ["4", "5", "6", "3", "3"], [
        "parked 4",
        "restarted 3",
        "#5 — killed after 14400s",
        "#6 — bailed https://github.com/o/r/pull/106",
        "stopped: #5 killed",
    ])
    assert run("continue-not-first", ["--repo", "o/r", "--continue-on-bail"], {}, "6 9\n", {"6": 0}) == (1, ["6"], [
        "#6 — bailed https://github.com/o/r/pull/106",
        "stopped: #6 bailed",
    ])
