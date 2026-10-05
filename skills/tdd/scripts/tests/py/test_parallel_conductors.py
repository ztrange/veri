"""In-process cases for veri/parallel_conductors.py, the module parallel-conductors.sh is a shim over."""
import importlib
import json
import os
import pathlib
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


def _boundaries(monkeypatch, tmp_path, on_launch, on_sleep):
    """Fake git, solvable-issues.sh (answering 7), supervise.sh, os.kill and the clock."""
    common = tmp_path / ".git"
    (common / "info").mkdir(parents=True)
    supervisors = []

    def answer(args):
        name = pathlib.Path(args[0]).name
        if name == "solvable-issues.sh":
            return subprocess.CompletedProcess(args, 0, "7\n", "")
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
