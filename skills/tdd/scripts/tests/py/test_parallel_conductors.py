"""In-process cases for veri/parallel_conductors.py, the module parallel-conductors.sh is a shim over."""
import importlib
import json
import os
import pathlib
import re
import shutil
import signal
import subprocess
import threading
import time
import traceback

import pytest

from conftest import SCRIPTS, issues_listing, listed, serve_through_gh, started_for_real

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


def _boundaries(monkeypatch, tmp_path, on_launch, on_sleep, solvable=(0, "7\n"), through_gh=False):
    """Fake git, supervise.sh, os.kill and the clock, and serve <solvable> (an answer, or a list of answers in
    turn) as the listings the real solvable-issues.sh selects from, issue 7 by default."""
    common = tmp_path / "repo" / ".git"
    (common / "info").mkdir(parents=True, exist_ok=True)
    supervisors = []

    answers = solvable if isinstance(solvable, list) else [solvable]
    if len(answers) > 1 or through_gh:
        serve_through_gh(tmp_path / "solvable-listing", monkeypatch, prs=tmp_path / "gh" / "prs.json")(answers)
    else:
        code, stdout, *priority = answers[0]
        (tmp_path / "gh").mkdir(exist_ok=True)
        (tmp_path / "gh" / "issues.json").write_text(issues_listing(listed(code, stdout), priority=(priority or [()])[0]))

    def answer(args):
        if list(args) == ["git", "rev-parse", "--git-common-dir"]:
            return subprocess.CompletedProcess(args, 0, "%s\n" % common, "")
        if list(args[:3]) == ["git", "worktree", "list"]:
            return subprocess.CompletedProcess(args, 0, "worktree %s\n\n" % (tmp_path / "repo"), "")
        raise AssertionError("unexpected subprocess call: %r" % (args,))

    def fake_run(args, *rest, **kwargs):
        if pathlib.Path(args[0]).name != "git":
            return started_for_real(args, *rest, **kwargs)
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


def selection_asked(args):
    """Whether the gh command <args> is the solvable selection's own listing, which the shim on PATH answers."""
    fields = args[args.index("--json") + 1] if "--json" in args else ""
    return fields in ("number,title,labels,body,state", "body,state") or (
        args[1:2] == ["api"] and "&page=" not in args[2])


def _gh_and_work(tmp_path):
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)
    return gh, work


def _event_log(work, n, text):
    log = work / ".tdd" / "wt" / n / ".tdd"
    log.mkdir(parents=True)
    (log / "events.jsonl").write_text(text)


def _sigterm_ends_the_live_conductor(monkeypatch, supervisors, events=None, sent=None):
    def recording_kill(pid, sig):
        if sent is not None:
            sent.append((pid, sig))
        live = [s for s in supervisors if s.pid == pid and s.returncode is None]
        if not live:
            raise ProcessLookupError(pid)
        if events is not None:
            events.append("kill %d" % pid)
        if sig == signal.SIGTERM:
            live[0].exit(143)

    monkeypatch.setattr(os, "kill", recording_kill)


def _exit_every_live_conductor(live):
    for sup in live:
        if sup.returncode is None:
            sup.exit(0)


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_an_assistant_event_the_conductor_writes_in_two_pieces_still_prints_one_context_line_for_the_whole_event(
        capsys, monkeypatch, tmp_path, parallel_conductors):
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


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_a_listing_with_no_labelled_open_issue_stops_with_nothing_solvable_and_returns_3(
        capsys, monkeypatch, tmp_path, parallel_conductors):
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(gh))
    work = tmp_path / "repo"
    work.mkdir()
    monkeypatch.chdir(work)

    def on_launch(sup):
        raise AssertionError("nothing should launch when no labelled issue is open")

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None, solvable=(3, ""))

    code = parallel_conductors.main([])
    out, _ = capsys.readouterr()

    assert code == 3
    assert "stopped: nothing solvable" in out.splitlines()


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_a_failing_removal_of_the_run_s_scratch_directory_at_exit_returns_2_and_leaves_parallel_exit_holding_the_code_written_before_it(
        capsys, monkeypatch, tmp_path, parallel_conductors):
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
        raise AssertionError("nothing should launch when no labelled issue is open")

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None, solvable=(3, ""))
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
@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_tunables_are_validated_in_order_naming_only_the_first_bad_one_and_a_refusal_returns_2_before_the_listing_is_read(
        env, refusal, capsys, monkeypatch, tmp_path, parallel_conductors):
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
        raise AssertionError("nothing should launch when no labelled issue is open")

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None, solvable=(3, ""))

    code = parallel_conductors.main([])
    out, err = capsys.readouterr()

    if refusal is None:
        assert (code, err, out.splitlines()[-1:]) == (3, "", ["stopped: nothing solvable"])
    else:
        assert (code, out, err.splitlines()) == (2, "", [refusal])
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
@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_the_exclude_gains_tdd_once_as_a_whole_line_before_any_tunable_is_validated_and_git_failing_returns_2_with_no_parallel_exit(
        env, info, before, git_status, code, after, capsys, monkeypatch, tmp_path, parallel_conductors):
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
        raise AssertionError("nothing should launch when no labelled issue is open")

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None, solvable=(3, ""))
    exclude = tmp_path / "repo" / ".git" / "info" / "exclude"
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
@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_each_issue_launches_as_supervise_env_run_conductor_with_the_caller_s_four_tunables_as_words_and_the_run_timeout_in_supervise_s_environment(
        env, words, run_timeout, capsys, monkeypatch, tmp_path, parallel_conductors):
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
    earlier = b'{"type":"assistant","cache_read_input_tokens":1,"cache_creation_input_tokens":1}\n'
    log.write_bytes(earlier)
    kept_at_launch = []

    def on_launch(sup):
        kept_at_launch.append(log.read_bytes() if log.exists() else None)
        with open(log, "ab") as f:
            f.write(b'{"type":"assistant","cache_read_input_tokens":5,"cache_creation_input_tokens":5}\n')
        sup.exit(0)

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None)
    faked_popen = subprocess.Popen
    launches = []

    def recording_popen(args, *rest, **kwargs):
        launches.append((list(args), dict(kwargs), dict(kwargs.get("env") or os.environ)))
        return faked_popen(args, *rest, **kwargs)

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
    assert kept_at_launch == [earlier]
    assert log.read_bytes().startswith(earlier)
    assert [l for l in out.splitlines() if l.startswith("context 7 ")] == ["context 7 10"]


@pytest.mark.parametrize("env, answers, exits, launched, slots, stopped, code", [
    ({"VERI_PARALLEL": "2"}, [(0, "7\n8\n")], {}, ["7", "8"], 2, "stopped: nothing solvable", 0),
    ({}, [(0, "7\n8\n"), (0, "7\n9\n"), (3, "")], {}, ["7", "9"], 1, "stopped: nothing solvable", 0),
    ({"VERI_PARALLEL": "3", "VERI_MAX_ISSUES": "2"}, [(0, "7\n8\n9\n")], {}, ["7", "8"], 2,
     "stopped: VERI_MAX_ISSUES reached", 0),
    ({}, [(2, "")], {}, [], 0, "stopped: solvable-issues.sh could not answer", 2),
    ({}, [(3, "")], {}, [], 0, "stopped: nothing solvable", 3),
    ({"VERI_PARALLEL": "2"}, [(0, "7\n"), (2, "")], {"7": 2}, ["7"], 1, None, 2),
    ({}, [(0, "7\n"), (3, "")], {"7": 2}, ["7"], 1, None, 1),
], ids=["two-slots", "afresh-first-unlaunched", "max-issues-cap", "plumbing", "nothing-launched",
        "plumbing-beats-failure", "failure"])
@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_slots_fill_from_a_fresh_solvable_issues_answer_up_to_the_cap_and_the_exit_code_ranks_plumbing_failure_nothing_launched_then_done(
        env, answers, exits, launched, slots, stopped, code, capsys, monkeypatch, tmp_path, parallel_conductors):
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
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

    _boundaries(monkeypatch, tmp_path, on_launch, on_sleep, solvable=answers, through_gh=True)

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
@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_a_user_line_after_the_step_done_call_stops_a_conductor_over_the_context_budget_and_relaunches_it_past_the_cap(
        budget, kills, launched, restarted, capsys, monkeypatch, tmp_path, parallel_conductors):
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

    supervisors = _boundaries(monkeypatch, tmp_path, on_launch, on_sleep, solvable=(0, "7\n8\n"))
    sent = []

    _sigterm_ends_the_live_conductor(monkeypatch, supervisors, sent=sent)

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
@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_veri_max_issues_with_a_leading_zero_is_read_as_bash_s_bare_arithmetic_reads_it(
        max_issues, launched, code, capsys, monkeypatch, tmp_path, parallel_conductors):
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
                solvable=(0, "\n".join(str(n) for n in range(1, 13)) + "\n"))

    returned = parallel_conductors.main([])
    out, _ = capsys.readouterr()

    assert (numbers, [line for line in out.splitlines() if line.startswith("stopped: ")], returned) == (
        launched, ["stopped: VERI_MAX_ISSUES reached"], code)


# Observed running parallel-conductors.sh at 79a9520bf with a conductor at context 50000 after its
# step-done call: VERI_CONDUCTOR_CTX_BUDGET=0100000 stops and relaunches it; every run exits 0.
@pytest.mark.parametrize("budget, kills, launched, restarted, contexts", [
    ("0100000", [], ["7"], [], ["context 7 50000", "context 7 500"]),
    ("08", [(FakeSupervisor.pid, signal.SIGTERM)], ["7", "7"], ["restarted 7"], ["context 7 50000"]),
    ("09", [(FakeSupervisor.pid, signal.SIGTERM)], ["7", "7"], ["restarted 7"], ["context 7 50000"]),
], ids=["0100000-is-decimal-#1127", "08-stops-over-8-tokens-with-no-base-error-#1127",
        "09-stops-over-9-tokens-with-no-base-error-#1127"])
@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_veri_conductor_ctx_budget_with_a_leading_zero_is_read_as_bash_s_bare_arithmetic_reads_it(
        budget, kills, launched, restarted, contexts, capsys, monkeypatch, tmp_path, parallel_conductors):
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

    supervisors = _boundaries(monkeypatch, tmp_path, on_launch, on_sleep, solvable=(0, "7\n8\n"))
    sent = []

    _sigterm_ends_the_live_conductor(monkeypatch, supervisors, sent=sent)

    code = parallel_conductors.main([])
    out, err = capsys.readouterr()

    assert ([s for s in sent if s[1] == signal.SIGTERM], launches,
            [line for line in out.splitlines() if line.startswith("restarted ")],
            [line for line in out.splitlines() if line.startswith("context ")], code,
            [line for line in err.splitlines() if "value too great for base" in line]) == (
        kills, launched, restarted, contexts, 0, [])


@pytest.mark.parametrize("budget, read, kills, launched, restarted, contexts", [
    ("100000", 100000, [], ["7"], [], ["context 7 100000", "context 7 500"]),
    ("100000", 100001, [(FakeSupervisor.pid, signal.SIGTERM)], ["7", "7"], ["restarted 7"], ["context 7 100001"]),
    (None, 120000, [], ["7"], [], ["context 7 120000", "context 7 500"]),
    (None, 120001, [(FakeSupervisor.pid, signal.SIGTERM)], ["7", "7"], ["restarted 7"], ["context 7 120001"]),
], ids=["100000-at-budget-#1127", "100000-over-budget-#1127", "unset-at-120000-#1127", "unset-over-120000-#1127"])
@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_veri_conductor_ctx_budget_of_100000_or_unset_stops_a_conductor_exactly_when_its_context_is_over_it_1127(
        budget, read, kills, launched, restarted, contexts, capsys, monkeypatch, tmp_path, parallel_conductors):
    if budget is not None:
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
                 b'"skills/tdd/scripts/event.sh step-done 3"}}],"usage":{"cache_creation_input_tokens":0,'
                 b'"cache_read_input_tokens":%d}}}\n' % read)
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

    supervisors = _boundaries(monkeypatch, tmp_path, on_launch, on_sleep, solvable=(0, "7\n8\n"))
    sent = []

    _sigterm_ends_the_live_conductor(monkeypatch, supervisors, sent=sent)

    code = parallel_conductors.main([])
    out, err = capsys.readouterr()

    assert ([s for s in sent if s[1] == signal.SIGTERM], launches,
            [line for line in out.splitlines() if line.startswith("restarted ")],
            [line for line in out.splitlines() if line.startswith("context ")], code, err) == (
        kills, launched, restarted, contexts, 0, "")


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_the_report_prints_one_line_per_issue_in_launch_order_killed_ahead_of_any_pr_parked_never_then_the_first_open_pr_closing_it_done_or_bailed(
        capsys, monkeypatch, tmp_path, parallel_conductors):
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
              "9": '{"event":"bail"}\n{"event":"resume"}\n'}
    for n, text in events.items():
        (work / ".tdd" / "wt" / n / ".tdd").mkdir(parents=True)
        (work / ".tdd" / "wt" / n / ".tdd" / "events.jsonl").write_text(text)
    monkeypatch.chdir(work)
    order = ["21", "3", "5", "6", "7", "8", "9", "10", "11", "12", "14"]
    numbers = []

    def on_launch(sup):
        n = sup.args[-1]
        numbers.append(n)
        (work / ".tdd" / ("conductor-%s.log" % n)).write_bytes(b"")
        sup.exit(2 if n == "21" else 0)

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None, solvable=(0, "\n".join(order) + "\n", (21,)))

    parallel_conductors.main(["--continue-on-bail"])
    out, _ = capsys.readouterr()

    assert numbers == order
    assert [line for line in out.splitlines() if line.startswith("#")] == [
        "#21 — killed after 60s",
        "#5 — done https://github.com/o/r/pull/105",
        "#6 — done ",
        "#7 — bailed https://github.com/o/r/pull/107",
        "#11 — done https://github.com/o/r/pull/111",
        "#14 — done https://github.com/o/r/pull/114",
    ]


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_the_cli_reports_a_ready_pr_done_a_draft_ending_in_a_bail_bailed_a_draft_not_ending_in_one_never_bailed_and_a_supervisor_exit_2_killed_one_line_each_in_launch_order_then_what_stopped_the_loop(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text(json.dumps([
        {"body": "Closes #7", "isDraft": False, "url": "https://example.test/pull/7"},
        {"body": "Closes #8", "isDraft": True, "url": "https://example.test/pull/8"},
        {"body": "Closes #9", "isDraft": True, "url": "https://example.test/pull/9"},
    ]))
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)
    events = {"8": '{"event": "launch"}\n{"event": "bail"}\n',
              "9": '{"event": "bail"}\n{"event": "launch"}\n'}
    for n, text in events.items():
        _event_log(work, n, text)

    def on_launch(sup):
        sup.exit(2 if sup.args[-1] == "10" else 0)

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None, solvable=(0, "7\n8\n9\n10\n"))

    code, out, err = run_cli(parallel_conductors, ["--continue-on-bail"], cwd=work,
                             env={"VERI_RUN_TIMEOUT": "60", "VERI_GH_JSON": str(gh)})

    assert out.splitlines() == [
        "#7 — done https://example.test/pull/7",
        "#8 — bailed https://example.test/pull/8",
        "#9 — bailed https://example.test/pull/9",
        "#10 — killed after 60s",
        "stopped: nothing solvable",
    ]
    assert code == 1


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_a_finished_run_ending_in_a_standing_done_mark_whose_pr_is_still_a_draft_is_reported_done_2009(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text(json.dumps([
        {"body": "Closes #7", "isDraft": True, "url": "https://example.test/pull/7"},
    ]))
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)
    _event_log(work, "7", '{"event": "launch", "issue": 7}\n{"event": "done", "issue": 7}\n')

    _boundaries(monkeypatch, tmp_path, lambda sup: sup.exit(0), lambda supervisors: None, solvable=(0, "7\n"))

    code, out, err = run_cli(parallel_conductors, [], cwd=work,
                             env={"VERI_RUN_TIMEOUT": "60", "VERI_GH_JSON": str(gh)})

    assert out.splitlines()[0] == "#7 — done https://example.test/pull/7"


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_a_finished_run_ending_in_a_standing_bail_mark_whose_pr_is_ready_for_review_is_reported_bailed_2009(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text(json.dumps([
        {"body": "Closes #7", "isDraft": False, "url": "https://example.test/pull/7"},
    ]))
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)
    _event_log(work, "7", '{"event":"launch","issue":7}\n{"event":"bail","issue":7}\n')

    _boundaries(monkeypatch, tmp_path, lambda sup: sup.exit(0), lambda supervisors: None, solvable=(0, "7\n"))

    code, out, err = run_cli(parallel_conductors, [], cwd=work,
                             env={"VERI_RUN_TIMEOUT": "60", "VERI_GH_JSON": str(gh)})

    assert (code, out.splitlines()[0]) == (1, "#7 — bailed https://example.test/pull/7")


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_the_report_over_a_run_whose_events_log_holds_one_non_utf_8_byte_prints_that_run_s_line_and_exits_0_2035(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text(json.dumps([
        {"body": "Closes #7", "isDraft": False, "url": "https://example.test/pull/7"},
    ]))
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)
    _event_log(work, "7", "")
    (work / ".tdd" / "wt" / "7" / ".tdd" / "events.jsonl").write_bytes(
        b'{"event":"launch","issue":7}\n{"event":"done","why":"cut \xff off"}\n')

    _boundaries(monkeypatch, tmp_path, lambda sup: sup.exit(0), lambda supervisors: None, solvable=(0, "7\n"))

    code, out, err = run_cli(parallel_conductors, [], cwd=work,
                             env={"VERI_RUN_TIMEOUT": "60", "VERI_GH_JSON": str(gh)})

    assert (out.splitlines()[0], code) == ("#7 — done https://example.test/pull/7", 0)


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_the_exit_code_the_parked_file_and_a_missing_pr_each_answer_beside_a_standing_mark_2009(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text(json.dumps([
        {"body": "Closes #7", "isDraft": False, "url": "https://example.test/pull/7"},
        {"body": "Closes #8", "isDraft": True, "url": "https://example.test/pull/8"},
    ]))
    work = tmp_path / "repo"
    (work / ".tdd" / "parked").mkdir(parents=True)
    (work / ".tdd" / "parked" / "8.md").write_text("parked\n")
    _event_log(work, "7", '{"event": "launch", "issue": 7}\n{"event": "done", "issue": 7}\n')
    _event_log(work, "8", '{"event": "launch", "issue": 8}\n{"event": "bail", "issue": 8}\n')
    _event_log(work, "9", '{"event": "launch", "issue": 9}\n{"event": "bail", "issue": 9}\n')

    _boundaries(monkeypatch, tmp_path, lambda sup: sup.exit(2 if sup.args[-1] == "7" else 0),
                lambda supervisors: None, solvable=(0, "7\n8\n9\n"))

    code, out, err = run_cli(parallel_conductors, ["--continue-on-bail"], cwd=work,
                             env={"VERI_RUN_TIMEOUT": "60", "VERI_GH_JSON": str(gh)})

    assert [line for line in out.splitlines() if line.startswith("#")] == ["#7 — killed after 60s"]


@pytest.mark.process("a faked supervise.sh over a VERI_GH_JSON listing, with the start of solvable-issues.sh refused")
def test_the_full_answer_is_the_same_when_starting_solvable_issues_sh_as_a_process_is_refused(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text(json.dumps([
        {"body": "Closes #7", "isDraft": False, "url": "https://example.test/pull/7"}]))
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)

    _boundaries(monkeypatch, tmp_path, lambda sup: sup.exit(0), lambda supervisors: None, solvable=(0, "7\n"))
    answered = subprocess.run

    def refusing(args, *rest, **kwargs):
        if pathlib.Path(args[0]).name == "solvable-issues.sh":
            raise PermissionError("starting %s is refused" % args[0])
        return answered(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", refusing)

    code, out, err = run_cli(parallel_conductors, [], cwd=work, env={"VERI_RUN_TIMEOUT": "60", "VERI_GH_JSON": str(gh)})

    assert (code, out.splitlines(), err) == (
        0, ["#7 — done https://example.test/pull/7", "stopped: nothing solvable"], "")


@pytest.mark.parametrize("name", ["VERI_LABEL", "VERI_PRIORITY_LABEL"])
@pytest.mark.process("a faked supervise.sh over a VERI_GH_JSON listing, with the start of solvable-issues.sh refused")
def test_an_empty_label_is_a_selection_that_could_not_answer_when_starting_solvable_issues_sh_as_a_process_is_refused(
        name, monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)

    _boundaries(monkeypatch, tmp_path, lambda sup: sup.exit(0), lambda supervisors: None, solvable=(0, "7\n"))
    answered = subprocess.run

    def refusing(args, *rest, **kwargs):
        if pathlib.Path(args[0]).name == "solvable-issues.sh":
            raise PermissionError("starting %s is refused" % args[0])
        return answered(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", refusing)

    code, out, err = run_cli(parallel_conductors, [], cwd=work, env={"VERI_GH_JSON": str(gh), name: ""})

    assert (code, out.splitlines(), err, (work / ".tdd" / "parallel.exit").read_text()) == (
        2, ["stopped: solvable-issues.sh could not answer"],
        "solvable-issues: %s is set but empty: name a label or leave it unset\n" % name, "2\n")


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_the_open_pr_list_is_read_through_gh_json_a_no_answer_at_the_report_returns_2_unwritten_at_a_finish_it_decides_over_the_pages_read_and_a_non_json_list_is_survived_as_bash_survives_it(
        capsys, monkeypatch, tmp_path, parallel_conductors):
    graphql = ["gh", "pr", "list", "--state", "open", "--limit", "10000", "--json", "body,isDraft,url"]
    rest = "repos/{owner}/{repo}/pulls?state=open&per_page=100&page=%d"
    bailed = json.dumps([{"body": "Closes #7", "draft": True, "html_url": "https://github.com/o/r/pull/107"}])

    applied = []

    def run(name, env, solvable, gh_answer):
        for var in applied:
            monkeypatch.delenv(var, raising=False)
        applied.clear()
        applied.extend(env)
        for var, value in env.items():
            monkeypatch.setenv(var, value)
        root = tmp_path / name
        work = root / "repo"
        (work / ".tdd" / "wt" / "7" / ".tdd").mkdir(parents=True)
        (work / ".tdd" / "wt" / "7" / ".tdd" / "events.jsonl").write_text('{"event": "red"}\n{"event": "bail"}\n')
        monkeypatch.chdir(work)
        numbers, gh_calls = [], []

        def on_launch(sup):
            numbers.append(sup.args[-1])
            (work / ".tdd" / ("conductor-%s.log" % sup.args[-1])).write_bytes(b"")
            sup.exit(0)

        _boundaries(monkeypatch, root, on_launch, lambda supervisors: None, solvable=solvable,
                    through_gh=True)
        faked_run = subprocess.run

        def gh_run(args, *rest_args, **kwargs):
            if args[0] != "gh" or selection_asked(args):
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

    code, lines, _, numbers, calls, _ = run("finish-no-answer", {}, (0, "7\n8\n"), paged)
    assert (code, lines, numbers) == (1, ["#7 — bailed https://github.com/o/r/pull/107", "stopped: #7 bailed"], ["7"])
    assert calls[:2] == [["gh", "api", rest % 1], ["gh", "api", rest % 2]]

    code, lines, err, numbers, _, _ = run(
        "not-json", {}, (0, "7\n8\n"), lambda i, args: (0, "not json\n") if i == 1 else (0, "[]\n"))
    assert (code, lines, numbers) == (0, ["stopped: nothing solvable"], ["7", "8"])
    assert "Traceback" in err and "JSONDecodeError" in err


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_a_finished_sweep_in_launch_order_restarts_past_a_stop_prints_parked_alone_stops_at_the_first_bail_or_kill_and_honours_continue_on_bail_only_as_argv_0(
        capsys, monkeypatch, tmp_path, parallel_conductors):
    step_done = (b'{"type":"assistant","message":{"content":[{"type":"tool_use","input":{"command":'
                 b'"skills/tdd/scripts/event.sh step-done 3"}}],"usage":{"cache_creation_input_tokens":1,'
                 b'"cache_read_input_tokens":100}}}\n')
    user = b'{"type":"user","message":{"content":[{"type":"tool_result","content":"ok"}]}}\n'

    applied = []

    def run(name, argv, env, solvable, exits):
        for var in applied:
            monkeypatch.delenv(var, raising=False)
        applied.clear()
        applied.extend(env)
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
    assert run("continue-not-first", ["--repo", "o/r", "--continue-on-bail"], {}, "6\n9\n", {"6": 0}) == (1, ["6"], [
        "#6 — bailed https://github.com/o/r/pull/106",
        "stopped: #6 bailed",
    ])


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_the_log_is_followed_as_bytes_waiting_veri_poll_seconds_for_it_joining_a_partial_line_reading_once_after_supervise_dies_and_dropping_an_unterminated_last_line(
        capsys, monkeypatch, tmp_path, parallel_conductors):
    monkeypatch.setenv("VERI_POLL", "3")
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(gh))
    work = tmp_path / "repo"
    work.mkdir()
    monkeypatch.chdir(work)
    log = work / ".tdd" / "conductor-7.log"

    def assistant(read, creation):
        return (b'{"type":"assistant","message":{"usage":{"cache_creation_input_tokens":%d,'
                b'"cache_read_input_tokens":%d}}}' % (creation, read))

    first = assistant(100, 1)
    ticks = [0]

    def on_sleep(supervisors):
        sup = supervisors[-1]
        if sup.returncode is not None:
            return
        ticks[0] += 1
        if ticks[0] == 1:
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_bytes(b'{"type":"system","text":"\xff\xfe caf\xe9"}\n' + first[:20])
        elif ticks[0] == 2:
            with open(log, "ab") as f:
                f.write(first[20:] + b"\n" + assistant(200, 2) + b"\n" + assistant(300, 3))
            sup.exit(0)

    _boundaries(monkeypatch, tmp_path, lambda sup: None, on_sleep)
    faked_sleep = time.sleep
    slept = []

    def recording_sleep(seconds):
        slept.append(float(seconds))
        faked_sleep(seconds)

    monkeypatch.setattr(time, "sleep", recording_sleep)

    code = parallel_conductors.main([])
    out, _ = capsys.readouterr()

    assert (slept, [line for line in out.splitlines() if line.startswith("context ")]) == (
        [3.0, 3.0], ["context 7 101", "context 7 202"])
    assert code in (0, 1, 2, 3)


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_a_stopped_conductor_s_context_is_no_longer_watched_and_the_conductor_beside_it_is_never_stopped(
        capsys, monkeypatch, tmp_path, parallel_conductors):
    monkeypatch.setenv("VERI_PARALLEL", "2")
    monkeypatch.setenv("VERI_CONDUCTOR_CTX_BUDGET", "50")
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(gh))
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)
    monkeypatch.chdir(work)
    logs = {n: work / ".tdd" / ("conductor-%s.log" % n) for n in ("7", "8")}
    step_done = (b'{"type":"assistant","message":{"content":[{"type":"tool_use","input":{"command":'
                 b'"skills/tdd/scripts/event.sh step-done 3"}}],"usage":{"cache_creation_input_tokens":1,'
                 b'"cache_read_input_tokens":100}}}\n')
    beside = b'{"type":"assistant","message":{"usage":{"cache_creation_input_tokens":0,"cache_read_input_tokens":900}}}\n'
    later = b'{"type":"assistant","message":{"usage":{"cache_creation_input_tokens":0,"cache_read_input_tokens":500}}}\n'
    user = b'{"type":"user","message":{"content":[{"type":"tool_result","content":"ok"}]}}\n'
    launches, sleeps = [], [0]

    def on_launch(sup):
        n = sup.args[-1]
        launches.append(n)
        sup.pid = 1000 + int(n) + 100 * (launches.count(n) - 1)
        if launches.count(n) > 1:
            logs[n].write_bytes(b"")
            sup.exit(0)
        else:
            logs[n].write_bytes(step_done if n == "7" else beside)

    def on_sleep(supervisors):
        sleeps[0] += 1
        if sleeps[0] == 1:
            for n in ("7", "8"):
                with open(logs[n], "ab") as f:
                    f.write(user)
        elif sleeps[0] == 2:
            with open(logs["7"], "ab") as f:
                f.write(later + step_done + user)
            with open(logs["8"], "ab") as f:
                f.write(beside + user)
        elif sleeps[0] == 3:
            supervisors[0].exit(143)
            supervisors[1].exit(0)

    supervisors = _boundaries(monkeypatch, tmp_path, on_launch, on_sleep, solvable=(0, "7\n8\n"))
    sent = []

    _sigterm_ends_the_live_conductor(monkeypatch, supervisors, sent=sent)

    code = parallel_conductors.main([])
    out, _ = capsys.readouterr()

    assert ([s for s in sent if s[1] == signal.SIGTERM],
            [line for line in out.splitlines() if line.startswith(("context ", "restarted "))]) == (
        [(1007, signal.SIGTERM)], ["context 7 101", "context 8 900", "context 8 900", "restarted 7"])
    assert code in (0, 1, 2, 3)


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_a_bad_veri_parallel_veri_max_issues_or_veri_conductor_ctx_budget_is_exit_2_naming_it_and_the_value_with_no_conductor_launched(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    work = tmp_path / "repo"
    work.mkdir()
    launched = []

    def on_launch(sup):
        launched.append(sup.args)

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None)
    bad = [("VERI_PARALLEL", "0", 1), ("VERI_PARALLEL", "two", 1), ("VERI_PARALLEL", "", 1),
           ("VERI_MAX_ISSUES", "abc", 1), ("VERI_MAX_ISSUES", "0", 1), ("VERI_MAX_ISSUES", "-1", 1),
           ("VERI_MAX_ISSUES", "1.5", 1), ("VERI_MAX_ISSUES", "", 1),
           ("VERI_CONDUCTOR_CTX_BUDGET", "abc", 0), ("VERI_CONDUCTOR_CTX_BUDGET", "1.5", 0),
           ("VERI_CONDUCTOR_CTX_BUDGET", "-1", 0)]
    seen, applied = [], []
    for name, value, floor in bad:
        for var in applied:
            monkeypatch.delenv(var, raising=False)
        applied.append(name)
        env = {"VERI_GH_JSON": str(gh), name: value}
        code, out, err = run_cli(parallel_conductors, [], env=env, cwd=work)
        seen.append((name, value, code, out, err.splitlines(), list(launched)))
    want = [(name, value, 2, "",
             ["parallel-conductors: %s must be a whole number >= %d: '%s'" % (name, floor, value)], [])
            for name, value, floor in bad]
    assert seen == want


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_the_schedule_launches_one_conductor_at_a_time_in_the_queue_s_printed_order_never_relaunches_a_finished_issue_takes_a_newly_solvable_one_next_and_caps_launches_only_under_veri_max_issues(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)
    in_flight_at_launch = []
    numbers = []

    def on_launch(sup):
        in_flight_at_launch.append(1 + sum(1 for s in supervisors if s is not sup and s.returncode is None))
        numbers.append(sup.args[-1])

    queue = [(0, "7\n8\n", (8,)), (0, "7\n8\n", (8,)), (0, "7\n8\n9\n", (8,)), (0, "7\n8\n9\n10\n", (8,))]

    seen = []
    for cap in ("3", None):
        env = {}
        if cap:
            env["VERI_MAX_ISSUES"] = cap
        supervisors = _boundaries(monkeypatch, tmp_path, on_launch, _exit_every_live_conductor, solvable=queue)
        del numbers[:], in_flight_at_launch[:]
        code, out, err = run_cli(parallel_conductors, [], env=env, cwd=work)
        seen.append((cap, code, list(numbers), set(in_flight_at_launch),
                     [line for line in out.splitlines() if line.startswith("stopped: ")]))
        monkeypatch.delenv("VERI_MAX_ISSUES", raising=False)
    assert seen == [
        ("3", 0, ["8", "7", "9"], {1}, ["stopped: VERI_MAX_ISSUES reached"]),
        (None, 0, ["8", "7", "9", "10"], {1}, ["stopped: nothing solvable"]),
    ]


@pytest.mark.parametrize("parks", [False, True], ids=["done", "parked"])
@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_with_veri_parallel_1_it_exits_0_once_nothing_is_left_to_take_after_launching_conductors_and_when_every_issue_still_solvable_is_parked(
        parks, monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]")
    work = tmp_path / "repo"
    (work / ".tdd").mkdir(parents=True)
    numbers = []

    def on_launch(sup):
        n = sup.args[-1]
        numbers.append(n)
        if parks:
            (work / ".tdd" / "parked").mkdir(exist_ok=True)
            (work / ".tdd" / "parked" / ("%s.md" % n)).write_text("Which test command should this run use?\n")

    _boundaries(monkeypatch, tmp_path, on_launch, _exit_every_live_conductor, solvable=(0, "7\n8\n"))
    code, out, err = run_cli(parallel_conductors, [], env={"VERI_PARALLEL": "1", "VERI_GH_JSON": str(gh)}, cwd=work)
    assert (code, numbers, [line for line in out.splitlines() if line.startswith(("parked ", "stopped: "))]) == (
        0, ["7", "8"],
        (["parked 7", "parked 8"] if parks else []) + ["stopped: nothing solvable"])
    assert (work / ".tdd" / "parallel.exit").read_text() == "0\n"


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_veri_parallel_2_starts_two_solvable_issues_conductors_before_either_ends(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh, work = _gh_and_work(tmp_path)
    starts = []

    def on_launch(sup):
        starts.append((sup.args[-1], sorted(s.args[-1] for s in supervisors if s is not sup and s.returncode is None)))

    supervisors = _boundaries(monkeypatch, tmp_path, on_launch, _exit_every_live_conductor, solvable=(0, "7\n8\n"))
    code, out, err = run_cli(parallel_conductors, [], env={"VERI_PARALLEL": "2", "VERI_GH_JSON": str(gh)}, cwd=work)
    assert (code, starts) == (0, [("7", []), ("8", ["7"])])


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_veri_parallel_2_prints_each_conductor_s_assistant_events_as_context_issue_cache_read_plus_cache_creation_attributed_to_its_own_issue_and_a_non_assistant_event_carrying_cache_usage_prints_none(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh, work = _gh_and_work(tmp_path)
    usage = '"usage":{"input_tokens":7,"cache_creation_input_tokens":%d,"cache_read_input_tokens":%d,"output_tokens":120}'
    events = {
        "7": ('{"type":"assistant","message":{"role":"assistant",%s}}\n' % (usage % (3438, 50000))),
        "8": ('{"type":"assistant","message":{"role":"assistant",%s}}\n' % (usage % (2000, 60000))),
    }
    user = '{"type":"user","message":{"role":"user",%s}}\n' % (usage % (9, 900))

    def on_launch(sup):
        n = sup.args[-1]
        (work / ".tdd" / ("conductor-%s.log" % n)).write_text(events[n] + user)

    _boundaries(monkeypatch, tmp_path, on_launch, _exit_every_live_conductor, solvable=(0, "7\n8\n"))
    code, out, err = run_cli(parallel_conductors, [], env={"VERI_PARALLEL": "2", "VERI_GH_JSON": str(gh)}, cwd=work)
    assert sorted(line for line in out.splitlines() if line.startswith("context ")) == [
        "context 7 53438", "context 8 62000"]


@pytest.mark.parametrize("env, step_done_tokens, events, launched", [
    ({"VERI_CONDUCTOR_CTX_BUDGET": "100000"}, 150000, ["kill 1007", "end 8"], ["7", "8", "7"]),
    ({}, 110000, ["end 7", "end 8"], ["7", "8"]),
], ids=["over-budget", "default-budget"])
@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_a_conductor_over_veri_conductor_ctx_budget_is_stopped_only_once_its_step_done_call_s_result_appears_a_default_budget_of_120000_stops_none_and_the_conductor_beside_it_runs_to_its_own_end(
        env, step_done_tokens, events, launched, monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh, work = _gh_and_work(tmp_path)
    logs = {n: work / ".tdd" / ("conductor-%s.log" % n) for n in ("7", "8")}
    usage = '"usage":{"cache_creation_input_tokens":0,"cache_read_input_tokens":%d}'
    step_done = ('{"type":"assistant","message":{"content":[{"type":"tool_use","input":{"command":'
                 '"skills/tdd/scripts/event.sh step-done"}}],%s}}\n' % (usage % step_done_tokens)).encode()
    later = ('{"type":"assistant","message":{"content":[{"type":"tool_use","input":{"command":"make test"}}],%s}}\n'
             % (usage % 150000)).encode()
    user = b'{"type":"user","message":{"content":[{"type":"tool_result","content":""}]}}\n'
    launches, events_seen, kills_before_result, ticks = [], [], [], [0]

    def on_launch(sup):
        n = sup.args[-1]
        launches.append(n)
        sup.pid = 1000 + int(n) + 100 * (launches.count(n) - 1)
        if launches.count(n) > 1:
            logs[n].write_bytes(b"")
            sup.exit(0)
        else:
            logs[n].write_bytes(step_done if n == "7" else b"")

    def on_sleep(live):
        ticks[0] += 1
        if ticks[0] == 1:
            kills_before_result.extend(events_seen)
            with open(logs["7"], "ab") as f:
                f.write(user)
        elif ticks[0] == 2:
            with open(logs["7"], "ab") as f:
                f.write(later + user)
        else:
            for sup in live:
                if sup.returncode is None:
                    events_seen.append("end %s" % sup.args[-1])
                    sup.exit(0)

    supervisors = _boundaries(monkeypatch, tmp_path, on_launch, on_sleep, solvable=(0, "7\n8\n"))

    _sigterm_ends_the_live_conductor(monkeypatch, supervisors, events_seen)
    code, out, err = run_cli(parallel_conductors, [],
                             env=dict(env, VERI_PARALLEL="2", VERI_GH_JSON=str(gh)), cwd=work)
    assert (kills_before_result, events_seen, launches) == ([], events, launched)
    assert code in (0, 1, 2, 3)


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_a_conductor_stopped_over_veri_conductor_ctx_budget_is_launched_again_for_the_same_issue_before_a_not_yet_launched_solvable_issue_takes_its_slot_and_prints_restarted_naming_its_issue(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh, work = _gh_and_work(tmp_path)
    log = work / ".tdd" / "conductor-7.log"
    step_done = (b'{"type":"assistant","message":{"content":[{"type":"tool_use","input":{"command":'
                 b'"skills/tdd/scripts/event.sh step-done"}}],"usage":{"cache_creation_input_tokens":0,'
                 b'"cache_read_input_tokens":150000}}}\n')
    user = b'{"type":"user","message":{"content":[{"type":"tool_result","content":""}]}}\n'
    launches = []

    def on_launch(sup):
        launches.append(sup.args[-1])
        if launches == ["7"]:
            log.write_bytes(step_done)
        else:
            sup.exit(0)

    def on_sleep(live):
        if live[0].returncode is None:
            with open(log, "ab") as f:
                f.write(user)

    supervisors = _boundaries(monkeypatch, tmp_path, on_launch, on_sleep, solvable=(0, "7\n8\n"))

    _sigterm_ends_the_live_conductor(monkeypatch, supervisors)
    code, out, err = run_cli(parallel_conductors, [],
                             env={"VERI_CONDUCTOR_CTX_BUDGET": "100000", "VERI_GH_JSON": str(gh)}, cwd=work)
    assert (launches, [line for line in out.splitlines() if line.startswith("restarted ")]) == (
        ["7", "7", "8"], ["restarted 7"])


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_with_veri_parallel_1_a_conductor_over_the_context_budget_is_stopped_only_after_its_step_done_result_and_relaunched_for_the_same_issue_while_each_launch_carries_the_caller_s_tunables_as_they_were_and_the_outer_supervisor_the_run_timeout_and_no_retries(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh, work = _gh_and_work(tmp_path)
    logs = {n: work / ".tdd" / ("conductor-%s.log" % n) for n in ("7", "8")}
    usage = '"usage":{"cache_creation_input_tokens":0,"cache_read_input_tokens":%d}'
    step_done = ('{"type":"assistant","message":{"content":[{"type":"tool_use","input":{"command":'
                 '"skills/tdd/scripts/event.sh step-done"}}],%s}}\n')
    user = b'{"type":"user","message":{"content":[{"type":"tool_result","content":""}]}}\n'
    launches, launched_with, events, kills_before_result, ticks = [], [], [], [], [0]
    alive_ticks = [0]

    def on_launch(sup):
        n = sup.args[-1]
        launches.append(n)
        sup.pid = 1000 + int(n) + 100 * (launches.count(n) - 1)
        if launches == ["7"]:
            logs[n].write_bytes((step_done % (usage % 150000)).encode())
        elif n == "8" and launches.count("8") <= 2:
            logs[n].write_bytes((step_done % (usage % 50000)).encode() + user)
        else:
            logs[n].write_bytes(b"")
            sup.exit(0)

    def on_sleep(live):
        ticks[0] += 1
        if ticks[0] == 1:
            kills_before_result.extend(events)
            with open(logs["7"], "ab") as f:
                f.write(user)
        eight = [s for s in live if s.args[-1] == "8" and s.returncode is None]
        if eight:
            alive_ticks[0] += 1
            if alive_ticks[0] > 3:
                eight[0].exit(0)

    supervisors = _boundaries(monkeypatch, tmp_path, on_launch, on_sleep, solvable=(0, "7\n8\n"))
    _sigterm_ends_the_live_conductor(monkeypatch, supervisors, events)
    faked_popen = subprocess.Popen

    def recording_popen(args, *rest, **kwargs):
        launched_with.append((list(args), dict(kwargs.get("env") or os.environ)))
        return faked_popen(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", recording_popen)
    code, out, err = run_cli(parallel_conductors, [], env={
        "VERI_PARALLEL": "1", "VERI_CONDUCTOR_CTX_BUDGET": "100000", "VERI_RUN_TIMEOUT": "60",
        "VERI_HEARTBEAT": "111", "VERI_POLL": "0.05", "VERI_STUCK_RETRIES": "3", "VERI_GH_JSON": str(gh)}, cwd=work)
    assert (launches, kills_before_result, events) == (["7", "7", "8"], [], ["kill 1007"])
    assert [line for line in out.splitlines() if line.startswith("restarted ")] == ["restarted 7"]
    for args, env in launched_with:
        assert args[3:11] == ["-u", "VERI_HEARTBEAT", "-u", "VERI_TIMEOUT", "-u", "VERI_STUCK_RETRIES", "-u", "VERI_POLL"]
        assert args[11:-2] == ["VERI_HEARTBEAT=111", "VERI_STUCK_RETRIES=3", "VERI_POLL=0.05"]
        assert (env["VERI_HEARTBEAT"], env["VERI_TIMEOUT"], env["VERI_STUCK_RETRIES"]) == ("60", "60", "0")


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_the_cli_prints_parked_for_a_conductor_that_halts_writing_its_parked_file_and_never_stops_launches_or_reports_a_bail_for_it_the_first_bail_stops_launches_while_running_conductors_finish_continue_on_bail_keeps_launching_and_the_first_kill_stops_launches(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    applied = []

    def run(name, argv, env, solvable, prs, bailed, parked, exits, slow=()):
        for var in applied:
            monkeypatch.delenv(var, raising=False)
        applied.clear()
        root = tmp_path / name
        gh = root / "gh"
        gh.mkdir(parents=True)
        (gh / "prs.json").write_text(json.dumps([
            {"body": "Closes #%s" % n, "isDraft": n in bailed, "url": "https://example.test/pull/%s" % n}
            for n in prs]))
        work = root / "repo"
        (work / ".tdd" / "parked").mkdir(parents=True)
        for n in bailed:
            _event_log(work, n, '{"event": "red"}\n{"event": "bail"}\n')
        launches = []

        def on_launch(sup):
            n = sup.args[-1]
            launches.append(n)
            sup.pid = 5000 + len(launches)
            if n in parked:
                (work / ".tdd" / "parked" / ("%s.md" % n)).write_text("Which test command?\n")
            if n not in slow:
                sup.exit(exits.get(n, 0))

        def on_sleep(supervisors):
            for sup in supervisors:
                if sup.returncode is None:
                    sup.exit(exits.get(sup.args[-1], 0))

        _boundaries(monkeypatch, root, on_launch, on_sleep, solvable=(0, solvable))
        code, out, err = run_cli(parallel_conductors, argv, cwd=work, env=dict(env, VERI_GH_JSON=str(gh)))
        applied.extend(dict(env, VERI_GH_JSON=""))
        return code, launches, [line for line in out.splitlines() if line.startswith(("parked ", "#", "stopped: "))]

    for flag in ([], ["--continue-on-bail"]):
        name = "park" + "".join(flag)
        assert run(name, flag, {}, "7\n8\n", ["7", "8"], {"7"}, {"7"}, {}) == (0, ["7", "8"], [
            "parked 7",
            "#8 — done https://example.test/pull/8",
            "stopped: nothing solvable",
        ])

    bail_prs = ["11", "12", "13"]
    assert run("bail-stop", [], {"VERI_PARALLEL": "2"}, "11\n12\n13\n", bail_prs, {"11"}, set(), {}, slow={"12"}) == (
        1, ["11", "12"], [
            "#11 — bailed https://example.test/pull/11",
            "#12 — done https://example.test/pull/12",
            "stopped: #11 bailed",
        ])
    assert run("bail-continue", ["--continue-on-bail"], {"VERI_PARALLEL": "2"}, "11\n12\n13\n", bail_prs, {"11"},
               set(), {}, slow={"12"}) == (1, ["11", "12", "13"], [
        "#11 — bailed https://example.test/pull/11",
        "#12 — done https://example.test/pull/12",
        "#13 — done https://example.test/pull/13",
        "stopped: nothing solvable",
    ])

    assert run("kill-stop", [], {"VERI_RUN_TIMEOUT": "60"}, "7\n8\n", ["8"], set(), set(), {"7": 2}) == (
        1, ["7"], [
            "#7 — killed after 60s",
            "stopped: #7 killed",
        ])


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_the_cli_exits_0_all_done_1_a_bail_or_a_kill_2_plumbing_and_3_nothing_solvable_with_parallel_exit_holding_the_code_and_prints_the_same_report_over_rest_in_two_or_three_pages_as_over_one_fixture(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    applied = []

    def prepare(name, solvable, exits=(), prs=(), bailed=(), through_gh=False):
        for var in applied:
            monkeypatch.delenv(var, raising=False)
        applied.clear()
        root = tmp_path / name
        work = root / "repo"
        (work / ".tdd").mkdir(parents=True)
        for n in bailed:
            _event_log(work, n, '{"event": "red"}\n{"event": "bail"}\n')
        launches = []

        def on_launch(sup):
            launches.append(sup.args[-1])
            sup.exit(2 if sup.args[-1] in exits else 0)

        _boundaries(monkeypatch, root, on_launch, lambda supervisors: None, solvable=solvable, through_gh=through_gh)
        gh = root / "gh"
        gh.mkdir(exist_ok=True)
        (gh / "prs.json").write_text(json.dumps([
            {"body": "Closes #7", "isDraft": draft, "url": "https://example.test/pull/7"} for draft in prs]))
        return work, gh, launches

    def report(code, out, work):
        lines = [line for line in out.splitlines() if line.startswith(("#", "stopped: "))]
        return code, lines, (work / ".tdd" / "parallel.exit").read_text()

    bailed_report = (1, ["#7 — bailed https://example.test/pull/7", "stopped: #7 bailed"], "1\n")
    shapes = [
        ("done", (0, "7\n"), {}, dict(prs=[False]), (0, ["#7 — done https://example.test/pull/7",
                                                        "stopped: nothing solvable"], "0\n")),
        ("bailed", (0, "7\n"), {}, dict(prs=[True], bailed=["7"]), bailed_report),
        ("killed", (0, "7\n"), {"VERI_RUN_TIMEOUT": "60"}, dict(exits=["7"]),
         (1, ["#7 — killed after 60s", "stopped: #7 killed"], "1\n")),
        ("plumbing", (2, ""), {}, {}, (2, ["stopped: solvable-issues.sh could not answer"], "2\n")),
        ("nothing", (3, ""), {}, {}, (3, ["stopped: nothing solvable"], "3\n")),
        ("bad-parallel", (0, "7\n"), {"VERI_PARALLEL": "0"}, {}, (2, [], "2\n")),
    ]
    for name, solvable, env, setup, want in shapes:
        work, gh, launches = prepare(name, solvable, **setup)
        code, out, err = run_cli(parallel_conductors, [], cwd=work, env=dict(env, VERI_GH_JSON=str(gh)))
        applied.extend(dict(env, VERI_GH_JSON=""))
        assert report(code, out, work) == want, name

    def pull(number, draft, url="https://example.test/pull/%s"):
        return {"number": number, "body": "Closes #%s" % number if number == 7 else "", "state": "open",
                "draft": draft, "html_url": url % number}

    pages = {
        "two": [[pull(901, False), pull(902, False)], [pull(7, True)]],
        "three": [[pull(901, True), pull(902, False)], [pull(903, False), pull(904, True)], [pull(7, True)]],
    }
    for name, served in pages.items():
        work, gh, launches = prepare("rest-" + name, (0, "7\n"), bailed=["7"], through_gh=True)
        faked_run, gh_calls = subprocess.run, []

        def gh_run(args, *rest, **kwargs):
            if args[0] != "gh" or selection_asked(args):
                return faked_run(args, *rest, **kwargs)
            gh_calls.append(list(args))
            path = args[2] if args[1:2] == ["api"] and len(args) == 3 else ""
            page = int(path.rsplit("page=", 1)[-1]) if "repos/{owner}/{repo}/pulls" in path else 0
            if not page:
                return subprocess.CompletedProcess(args, 1, "", "HTTP 403: GraphQL is not available")
            return subprocess.CompletedProcess(args, 0, json.dumps(served[page - 1] if page <= len(served) else []) + "\n", "")

        monkeypatch.setattr(subprocess, "run", gh_run)
        code, out, err = run_cli(parallel_conductors, [], cwd=work, env={})
        assert report(code, out, work) == bailed_report, name
        assert gh_calls and all(call[:2] == ["gh", "api"] for call in gh_calls), name
        assert [call[2].rsplit("page=", 1)[-1] for call in gh_calls[-(len(served) + 1):]] == [
            str(page) for page in range(1, len(served) + 2)], name


@pytest.mark.process("git: the target repository's own status and exclude file")
def test_a_launch_in_a_real_repository_leaves_its_git_status_empty_keeps_its_exclude_last_line_adds_tdd_once_over_two_launches_and_writes_nothing_into_another_repository(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    def git(*args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd, check=True, stdout=subprocess.PIPE, text=True).stdout

    def repo(name):
        path = tmp_path / name
        git("init", "-q", str(path))
        return path

    fresh, no_info, own, decoy = repo("fresh"), repo("no-info"), repo("own"), repo("decoy")
    shutil.rmtree(no_info / ".git" / "info")
    (own / ".git" / "info").mkdir(exist_ok=True)
    (own / ".git" / "info" / "exclude").write_bytes(b"*.scratch")
    decoy_exclude = decoy / ".git" / "info" / "exclude"
    decoy_before = decoy_exclude.read_bytes() if decoy_exclude.is_file() else None
    gh, _ = _gh_and_work(tmp_path)
    (gh / "issues.json").write_text(json.dumps([{
        "number": 7, "title": "issue 7", "labels": [{"name": "ready-for-agent"}], "state": "OPEN", "body": ""}]))

    ran = []
    real_popen = subprocess.Popen

    def popen(args, *rest, **kwargs):
        if pathlib.Path(args[0]).name != "supervise.sh":
            return real_popen(args, *rest, **kwargs)
        sup = FakeSupervisor(args)
        sup.exit(0)
        ran.append(pathlib.Path.cwd().name)
        os.makedirs(".tdd", exist_ok=True)
        (pathlib.Path(".tdd") / "conductor-7.log").write_text("")
        return sup

    monkeypatch.setattr(subprocess, "Popen", popen)
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

    statuses = {}
    for where in (fresh, no_info, own, own):
        code, out, err = run_cli(parallel_conductors, [], env={"VERI_GH_JSON": str(gh)}, cwd=where)
        assert code == 0, (where.name, out, err)
        statuses[where.name] = git("status", "--porcelain", cwd=where)

    assert ran == ["fresh", "no-info", "own", "own"]
    assert statuses == {"fresh": "", "no-info": "", "own": ""}
    assert (own / ".git" / "info" / "exclude").read_bytes() == b"*.scratch\n.tdd/*\n"
    assert (decoy_exclude.read_bytes() if decoy_exclude.is_file() else None) == decoy_before
    assert [p.name for p in decoy.rglob("*") if ".git" not in p.parts] == []


@pytest.mark.process("parallel-conductors.sh supervising a real conductor, run through a symlink to the skills directory")
@pytest.mark.tree_audit("every directory under skills/tdd/ but tests/")
def test_a_launch_run_through_a_symlink_to_the_skills_directory_from_another_cwd_answers_as_it_does_in_place_and_prints_no_leaf_role_refusal(
        tmp_path):
    copy = tmp_path / "copy" / "skills"
    shutil.copytree(SCRIPTS.parent, copy / "tdd", symlinks=True, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    (tmp_path / "skills").symlink_to(copy, target_is_directory=True)
    gh, _ = _gh_and_work(tmp_path)
    (gh / "issues.json").write_text(json.dumps([{
        "number": 7, "title": "issue 7", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
        "body": "## Blocked by\n\nNone.\n"}]))
    claude = tmp_path / "claude"
    claude.write_text("""#!/bin/sh
n="$(sed -n 's/^Solve issue #\\([0-9]*\\) .*/\\1/p')"
echo "start $n" >> "$VERI_STUB_RECORD"
printf '{"body": "Closes #%s", "state": "OPEN", "isDraft": false, "url": "https://example.test/pull/%s"}\\n' "$n" "$n" >> "GH/prs.lines"
printf '[%s]\\n' "$(paste -sd, "GH/prs.lines")" > "GH/prs.json"
mkdir -p ".tdd/wt/$n/.tdd"
echo '{"event": "done"}' >> ".tdd/wt/$n/.tdd/events.jsonl"
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
""".replace("GH", str(gh)))
    claude.chmod(0o755)
    env = {name: value for name, value in os.environ.items() if not name.startswith(("VERI_", "CLAUDE_"))}

    answers = {}
    for shape, launcher in (("in-place", copy / "tdd" / "scripts" / "parallel-conductors.sh"),
                            ("symlink", tmp_path / "skills" / "tdd" / "scripts" / "parallel-conductors.sh")):
        repo = tmp_path / shape
        subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                        "--allow-empty", "-m", "init"], check=True)
        (gh / "prs.lines").write_text("")
        (gh / "prs.json").write_text("[]\n")
        record = tmp_path / ("record-" + shape)
        ran = subprocess.run([str(launcher)], cwd=repo, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                             env={**env, "VERI_GH_JSON": str(gh), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.05",
                                  "VERI_STUB_RECORD": str(record)})
        output = ran.stdout + ran.stderr
        report = [line for line in output.splitlines() if line.startswith(("#", "stopped: "))]
        answers[shape] = (ran.returncode, report, (repo / ".tdd" / "parallel.exit").read_text().strip(),
                          record.read_text() if record.exists() else None,
                          [line for line in output.splitlines() if "leaf-role:" in line],
                          [json.loads(line).get("event")
                           for line in (repo / ".tdd" / "wt" / "7" / ".tdd" / "events.jsonl").read_text().splitlines()])

    assert answers["in-place"] == (0, ["#7 \u2014 done https://example.test/pull/7", "stopped: nothing solvable"],
                                   "0", "start 7\n", [], ["conductor-start", "done"])
    assert answers["symlink"] == answers["in-place"]


@pytest.mark.process("parallel-conductors.sh supervising a real conductor in place")
@pytest.mark.tree_audit("every directory under skills/tdd/ but tests/")
def test_an_in_place_launch_leaves_the_conductors_event_log_holding_done_for_the_issue_it_solved_2814(tmp_path):
    copy = tmp_path / "copy" / "skills"
    shutil.copytree(SCRIPTS.parent, copy / "tdd", symlinks=True, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    gh, _ = _gh_and_work(tmp_path)
    (gh / "issues.json").write_text(json.dumps([{
        "number": 7, "title": "issue 7", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
        "body": "## Blocked by\n\nNone.\n"}]))
    claude = tmp_path / "claude"
    claude.write_text("""#!/bin/sh
n="$(sed -n 's/^Solve issue #\\([0-9]*\\) .*/\\1/p')"
printf '{"body": "Closes #%s", "state": "OPEN", "isDraft": false, "url": "https://example.test/pull/%s"}\\n' "$n" "$n" >> "GH/prs.lines"
printf '[%s]\\n' "$(paste -sd, "GH/prs.lines")" > "GH/prs.json"
mkdir -p ".tdd/wt/$n/.tdd"
echo '{"event": "done"}' >> ".tdd/wt/$n/.tdd/events.jsonl"
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
""".replace("GH", str(gh)))
    claude.chmod(0o755)
    (gh / "prs.lines").write_text("")
    repo = tmp_path / "in-place"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                    "--allow-empty", "-m", "init"], check=True)
    env = {name: value for name, value in os.environ.items() if not name.startswith(("VERI_", "CLAUDE_"))}
    ran = subprocess.run([str(copy / "tdd" / "scripts" / "parallel-conductors.sh")], cwd=repo,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True,
                         env={**env, "VERI_GH_JSON": str(gh), "CLAUDE_BIN": str(claude), "VERI_POLL": "0.05"})
    log = repo / ".tdd" / "wt" / "7" / ".tdd" / "events.jsonl"
    assert (log.exists(), ran.returncode) == (True, 0), ran.stdout + ran.stderr
    assert [json.loads(line).get("event") for line in log.read_text().splitlines()] == ["conductor-start", "done"]


def test_a_resumed_conductor_launch_keeps_the_earlier_session_s_log_while_its_context_watch_reads_only_the_new_session(
        capsys, monkeypatch, tmp_path, parallel_conductors):
    monkeypatch.chdir(tmp_path)
    log = tmp_path / ".tdd" / "conductor-7.log"
    log.parent.mkdir()

    def assistant(read, creation):
        return b'{"type":"assistant","message":{"usage":{"cache_creation_input_tokens":%d,"cache_read_input_tokens":%d}}}\n' % (
            creation, read)

    earlier = assistant(100, 1)
    log.write_bytes(earlier)
    monkeypatch.setattr(subprocess, "Popen", lambda args, **kwargs: FakeSupervisor(args))

    conductor = parallel_conductors._Conductor("7")
    with open(log, "ab") as f:
        f.write(assistant(200, 2))
    conductor.follow()
    out, _ = capsys.readouterr()

    assert (log.read_bytes().startswith(earlier), [l for l in out.splitlines() if l.startswith("context ")]) == (
        True, ["context 7 202"])


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_the_cli_reports_a_draft_whose_compact_separator_log_ends_in_a_bail_bailed_and_one_whose_log_does_not_end_in_one_never_bailed(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh, work = _gh_and_work(tmp_path)
    (gh / "prs.json").write_text(json.dumps([
        {"body": "Closes #8", "isDraft": True, "url": "https://example.test/pull/8"},
        {"body": "Closes #9", "isDraft": True, "url": "https://example.test/pull/9"},
    ]))
    _event_log(work, "8", '{"event":"launch"}\n{"event":"bail","why":"stuck"}\n')
    _event_log(work, "9", '{"event":"bail"}\n{"event":"launch"}\n')
    _boundaries(monkeypatch, tmp_path, lambda sup: sup.exit(0), lambda supervisors: None, solvable=(0, "8\n9\n"))

    code, out, err = run_cli(parallel_conductors, ["--continue-on-bail"], cwd=work, env={"VERI_GH_JSON": str(gh)})

    assert (code, out.splitlines()) == (1, [
        "#8 — bailed https://example.test/pull/8",
        "#9 — bailed https://example.test/pull/9",
        "stopped: nothing solvable"])


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_a_draft_run_whose_bail_mark_is_spaced_or_compact_is_reported_bailed_either_way_2009(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh, work = _gh_and_work(tmp_path)
    (gh / "prs.json").write_text(json.dumps([
        {"body": "Closes #8", "isDraft": True, "url": "https://example.test/pull/8"},
        {"body": "Closes #9", "isDraft": True, "url": "https://example.test/pull/9"},
    ]))
    _event_log(work, "8", '{ "event" : "launch" }\n{ "event" : "bail" }\n')
    _event_log(work, "9", '{"event":"launch"}\n{"event":"bail"}\n')
    _boundaries(monkeypatch, tmp_path, lambda sup: sup.exit(0), lambda supervisors: None, solvable=(0, "8\n9\n"))

    code, out, err = run_cli(parallel_conductors, ["--continue-on-bail"], cwd=work, env={"VERI_GH_JSON": str(gh)})

    assert (code, out.splitlines()) == (1, [
        "#8 — bailed https://example.test/pull/8",
        "#9 — bailed https://example.test/pull/9",
        "stopped: nothing solvable"])


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_a_child_that_died_before_writing_any_event_is_answered_from_its_pr_and_exit_code_2009(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh, work = _gh_and_work(tmp_path)
    (gh / "prs.json").write_text(json.dumps([
        {"body": "Closes #7", "isDraft": False, "url": "https://example.test/pull/7"},
        {"body": "Closes #8", "isDraft": True, "url": "https://example.test/pull/8"},
    ]))

    def on_launch(sup):
        sup.exit(2 if sup.args[-1] == "9" else 0)

    _boundaries(monkeypatch, tmp_path, on_launch, lambda supervisors: None, solvable=(0, "7\n8\n9\n"))

    code, out, err = run_cli(parallel_conductors, ["--continue-on-bail"], cwd=work,
                             env={"VERI_RUN_TIMEOUT": "60", "VERI_GH_JSON": str(gh)})

    assert out.splitlines() == [
        "#7 — done https://example.test/pull/7",
        "#9 — killed after 60s",
        "stopped: nothing solvable"]


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_whether_a_run_has_ended_is_answered_only_from_run_end_not_from_the_events_log_2009(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh, work = _gh_and_work(tmp_path)
    (gh / "prs.json").write_text(json.dumps([
        {"body": "Closes #7", "isDraft": True, "url": "https://example.test/pull/7"},
        {"body": "Closes #8", "isDraft": False, "url": "https://example.test/pull/8"},
    ]))
    _event_log(work, "7", '{"event":"launch"}\n{"event":"bail"}\n')
    _event_log(work, "8", '{"event":"launch"}\n')
    answers = {"7": (True, "done", {"event": "done"}), "8": (True, "bailed", {"event": "bail"})}
    monkeypatch.setattr(parallel_conductors, "run_end",
                        lambda run_dir: answers[os.path.basename(run_dir)])
    _boundaries(monkeypatch, tmp_path, lambda sup: sup.exit(0), lambda supervisors: None, solvable=(0, "7\n8\n"))

    code, out, err = run_cli(parallel_conductors, ["--continue-on-bail"], cwd=work,
                             env={"VERI_RUN_TIMEOUT": "60", "VERI_GH_JSON": str(gh)})

    assert out.splitlines()[:2] == [
        "#7 — done https://example.test/pull/7",
        "#8 — bailed https://example.test/pull/8"]


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_run_from_a_subdirectory_of_the_repo_writes_parallel_exit_under_the_repo_root_and_leaves_no_tdd_in_the_subdirectory_1895(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh, work = _gh_and_work(tmp_path)
    sub = work / "skills"
    sub.mkdir()

    _boundaries(monkeypatch, tmp_path, lambda sup: sup.exit(0), _exit_every_live_conductor, solvable=(0, "7\n"))
    code, out, err = run_cli(parallel_conductors, [], env={"VERI_GH_JSON": str(gh)}, cwd=sub)

    assert (code, (work / ".tdd" / "parallel.exit").exists(), (sub / ".tdd").exists()) == (0, True, False)


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_run_from_a_subdirectory_of_the_repo_follows_each_conductor_log_at_the_repo_root_1895(
        monkeypatch, tmp_path, parallel_conductors, run_cli):
    gh, work = _gh_and_work(tmp_path)
    sub = work / "skills"
    sub.mkdir()
    event = b'{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":7,"cache_creation_input_tokens":3438,"cache_read_input_tokens":50000,"output_tokens":120}}}\n'

    def on_launch(sup):
        (work / ".tdd" / ("conductor-%s.log" % sup.args[-1])).write_bytes(event)

    _boundaries(monkeypatch, tmp_path, on_launch, _exit_every_live_conductor, solvable=(0, "7\n"))
    code, out, err = run_cli(parallel_conductors, [], env={"VERI_GH_JSON": str(gh)}, cwd=sub)

    assert [l for l in out.splitlines() if l.startswith("context ")] == ["context 7 53438"]
