"""In-process cases for veri/dashboard.py, the module dashboard.sh is a shim over."""
import http.server
import importlib
import io
import json
import os
import re
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.request

import pytest

from conftest import SCRIPTS


@pytest.fixture(autouse=True)
def keep_sigint():
    handler = signal.getsignal(signal.SIGINT)
    yield
    signal.signal(signal.SIGINT, handler)


@pytest.fixture
def dashboard():
    return importlib.import_module("veri.dashboard")


class FakeConnection:
    def __init__(self, request):
        self.rfile = io.BytesIO(request)
        self.sent = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        return self.rfile if "r" in mode else self.sent

    def sendall(self, data):
        self.sent.write(data)

    def settimeout(self, timeout):
        pass


def get(handler, server, path):
    """The raw HTTP answer <handler> gives a GET of <path>."""
    connection = FakeConnection(("GET %s HTTP/1.0\r\n\r\n" % path).encode())
    handler(connection, ("127.0.0.1", 50000), server)
    return connection.sent.getvalue()


def fake_server(monkeypatch, paths):
    """Replace ThreadingHTTPServer with one that records its address, GETs <paths> through the
    handler it was given, then raises KeyboardInterrupt; returns the list of (address, answers)."""
    served = []

    class FakeServer:
        def __init__(self, address, handler):
            self.server_address = address
            self.handler = handler
            served.append((address, []))

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def serve_forever(self, *args, **kwargs):
            for path in paths:
                served[-1][1].append(get(self.handler, self, path))
            raise KeyboardInterrupt

        def server_close(self):
            pass

    monkeypatch.setattr(http.server, "ThreadingHTTPServer", FakeServer)
    return served


def body(answer):
    return answer.partition(b"\r\n\r\n")[2]


FAKE_GIT = """#!/bin/sh
if [ "$1" = worktree ]; then
  printf 'worktree %s\\nHEAD abc\\nbranch refs/heads/main\\n\\n' "$MAIN_TREE"
elif [ "$3" = symbolic-ref ]; then
  printf 'tdd/%s-lamps\\n' "$(basename "$2")"
fi
"""


def fabricated_main_tree(tmp_path, monkeypatch):
    """A main tree holding run 31, with a git on PATH answering worktree list and symbolic-ref."""
    run = tmp_path / ".tdd" / "wt" / "31"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "issue-31.md").write_text("# Plan for #31 \u2014 lamps glow\n\n- [ ] a lamp glows\n")
    bin_dir = tmp_path / "fake-bin"
    bin_dir.mkdir()
    (bin_dir / "git").write_text(FAKE_GIT)
    (bin_dir / "git").chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ.get("PATH", ""))
    monkeypatch.setenv("MAIN_TREE", str(tmp_path))
    monkeypatch.delenv("VERI_LABEL", raising=False)
    monkeypatch.chdir(tmp_path)


def status_document(run_cli):
    import importlib
    code, out, err = run_cli(importlib.import_module("veri.status"), ["--json"])
    assert code == 0
    document = json.loads(out)
    assert document["runs"][0]["issue"] == "31"
    return out.encode()


@pytest.mark.process("the git status starts for /api/runs, a fake one first on PATH")
def test_main_serves_on_loopback_8765_or_the_first_argument_with_the_files_beside_the_scripts(
        tmp_path, monkeypatch, dashboard, run_cli):
    fabricated_main_tree(tmp_path, monkeypatch)
    served = fake_server(monkeypatch, ["/", "/api/runs"])

    dashboard.main([])
    dashboard.main([""])
    dashboard.main(["4242", "9999"])

    assert [address for address, _ in served] == [
        ("127.0.0.1", 8765), ("127.0.0.1", 8765), ("127.0.0.1", 4242)]
    page, runs = served[0][1]
    with open(os.path.join(SCRIPTS, "dashboard.html"), "rb") as f:
        assert body(page) == f.read()
    assert body(runs) == status_document(run_cli)


def status_code(answer):
    return answer.split(b"\r\n", 1)[0].split()[1]


@pytest.mark.process("the git status starts for /api/runs, a fake one first on PATH")
def test_main_binds_loopback_on_8765_or_the_port_argument_answers_gets_and_returns_0_on_keyboard_interrupt(
        tmp_path, monkeypatch, dashboard, run_cli):
    fabricated_main_tree(tmp_path, monkeypatch)
    served = fake_server(monkeypatch, ["/", "/api/runs"])

    codes = [dashboard.main([]), dashboard.main(["4243"])]

    assert [address for address, _ in served] == [("127.0.0.1", 8765), ("127.0.0.1", 4243)]
    assert [status_code(answer) for answer in served[0][1]] == [b"200", b"200"]
    assert body(served[0][1][1]) == status_document(run_cli)
    assert codes == [0, 0]


def test_importing_the_module_constructs_no_server_and_leaves_the_sigint_handler_alone(
        monkeypatch):
    def sentinel(signum, frame):
        pass

    signal.signal(signal.SIGINT, sentinel)
    served = fake_server(monkeypatch, [])
    monkeypatch.delitem(sys.modules, "veri.dashboard", raising=False)

    importlib.import_module("veri.dashboard")

    assert served == []
    assert signal.getsignal(signal.SIGINT) is sentinel


@pytest.mark.process("the git status starts for /api/runs, a fake one first on PATH")
def test_get_api_runs_through_main_answers_exactly_the_document_status_json_renders(
        tmp_path, monkeypatch, dashboard, run_cli):
    fabricated_main_tree(tmp_path, monkeypatch)
    served = fake_server(monkeypatch, ["/api/runs"])

    dashboard.main([])

    (runs,) = served[0][1]
    assert status_code(runs) == b"200"
    assert body(runs) == status_document(run_cli)


@pytest.mark.process("the git status starts for /api/runs, a fake one first on PATH")
def test_get_api_runs_gives_its_full_answer_when_starting_status_sh_as_a_process_is_refused(
        tmp_path, monkeypatch, dashboard, run_cli, capfd):
    fabricated_main_tree(tmp_path, monkeypatch)
    want = status_document(run_cli)
    capfd.readouterr()
    real_run = subprocess.run

    def refusing_run(argv, *args, **kwargs):
        if str(argv[0]).endswith("status.sh"):
            raise AssertionError("started status.sh as a process: %r" % (argv,))
        return real_run(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", refusing_run)
    served = fake_server(monkeypatch, ["/api/runs"])

    code = dashboard.main([])

    (runs,) = served[0][1]
    assert code == 0
    assert status_code(runs) == b"200"
    assert body(runs) == want
    assert capfd.readouterr().err == ""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def report_of(run_cli, issue, run):
    """The report metrics renders from <run>'s own events log and ledger."""
    import metrics
    code, out, _ = run_cli(metrics, [issue], cwd=run)
    assert code == 0
    assert out.strip()
    return out


def serve_with_real_metrics(monkeypatch, tmp_path):
    """Fake only `git worktree list`; metrics.report really runs."""
    real_run = subprocess.run

    def fake_run(args, *rest, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return real_run(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    return fake_server(monkeypatch, ["/api/metrics"])


def test_get_api_metrics_recomputes_a_live_run_and_quotes_the_committed_report_of_one_ended_by_done(
        tmp_path, monkeypatch, dashboard, run_cli):
    live = os.path.join(str(tmp_path), ".tdd", "wt", "31")
    ended = os.path.join(str(tmp_path), ".tdd", "wt", "32")
    write(os.path.join(live, ".tdd", "issue-31.md"), "# Plan for #31\n\n- [ ] a lamp glows\n")
    write(os.path.join(live, ".tdd", "events.jsonl"),
          '{"ts": 1, "issue": "31", "event": "step-start"}\n'
          '{"ts": 2, "issue": "31", "event": "launch", "name": "develop-red"}\n')
    write(os.path.join(live, ".tdd", "issue-31-metrics.md"), "# a stale committed report\n")
    committed = "# What solving #32 cost\n\n| phase | attempts |\n|---|---|\n| green | 1 |\n"
    write(os.path.join(ended, ".tdd", "issue-32.md"), "# Plan for #32\n\n- [x] a lamp dims\n")
    write(os.path.join(ended, ".tdd", "events.jsonl"),
          '{"ts": 1, "issue": "32", "event": "step-done"}\n'
          '{"ts": 2, "issue": "32", "event": "done"}\n')
    write(os.path.join(ended, ".tdd", "issue-32-metrics.md"), committed)
    recomputed = report_of(run_cli, "31", live)
    served = serve_with_real_metrics(monkeypatch, tmp_path)

    dashboard.main([])
    assert os.getcwd() == str(tmp_path)

    (metrics,) = served[0][1]
    issues = json.loads(body(metrics))["issues"]
    assert issues["31"] == recomputed
    assert issues["32"] == committed


def test_get_api_metrics_gives_its_full_answer_for_a_live_run_when_starting_metrics_sh_as_a_process_is_refused(
        tmp_path, monkeypatch, dashboard, run_cli, capfd):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "36")
    write(os.path.join(run, ".tdd", "issue-36.md"), "# Plan for #36\n\n- [ ] a lamp glows\n")
    write(os.path.join(run, ".tdd", "events.jsonl"),
          '{"ts": 1, "issue": "36", "event": "step-start"}\n'
          '{"ts": 2, "issue": "36", "event": "launch", "name": "develop-red"}\n')
    want = report_of(run_cli, "36", run)
    served = serve_with_real_metrics(monkeypatch, tmp_path)
    capfd.readouterr()
    git_aware_run = subprocess.run
    real_popen = subprocess.Popen

    def refuse(argv):
        if "metrics.sh" in str(argv):
            raise AssertionError("started metrics.sh as a process: %r" % (argv,))

    def refusing_run(argv, *args, **kwargs):
        refuse(argv)
        return git_aware_run(argv, *args, **kwargs)

    def refusing_popen(argv, *args, **kwargs):
        refuse(argv)
        return real_popen(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", refusing_run)
    monkeypatch.setattr(subprocess, "Popen", refusing_popen)

    code = dashboard.main([])

    (metrics,) = served[0][1]
    assert code == 0
    assert status_code(metrics) == b"200"
    assert json.loads(body(metrics))["issues"]["36"] == want
    assert os.getcwd() == str(tmp_path)
    assert capfd.readouterr().err == ""
    assert not os.path.exists(os.path.join(run, ".tdd", "issue-36-metrics.md"))


def test_get_api_metrics_quotes_the_committed_report_of_run_33_ended_by_bail(
        tmp_path, monkeypatch, dashboard):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "33")
    write(os.path.join(run, ".tdd", "issue-33.md"),
          "# Plan for #33 — lamps flicker\n\n- [x] a lamp exists\n- [ ] a lamp flickers\n")
    write(os.path.join(run, ".tdd", "events.jsonl"),
          '{"ts": 1, "issue": "33", "event": "step-start"}\n'
          '{"ts": 2, "issue": "33", "event": "launch", "name": "develop-red"}\n'
          '{"ts": 3, "issue": "33", "event": "bail", "reason": "killed-stuck"}\n')
    committed = ("# What solving #33 cost — the committed report of a bailed run, verbatim\n\n"
                 "| phase | attempts |\n|---|---|\n| red | 1 |\n")
    write(os.path.join(run, ".tdd", "issue-33-metrics.md"), committed)

    def fake_run(args, cwd=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    def recomputed(issue, events, ledger, stream=None):
        stream.write("# metrics.report 33, recomputed\n")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(dashboard.metrics, "report", recomputed)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/metrics"])

    dashboard.main([])

    (metrics,) = served[0][1]
    assert json.loads(body(metrics))["issues"]["33"] == committed


def test_get_api_metrics_answers_run_34_ended_by_bail_with_no_committed_report_with_a_marker_naming_the_file(
        tmp_path, monkeypatch, dashboard):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "34")
    write(os.path.join(run, ".tdd", "issue-34.md"),
          "# Plan for #34 — lamps gutter\n\n- [x] a lamp exists\n- [ ] a lamp gutters\n")
    write(os.path.join(run, ".tdd", "events.jsonl"),
          '{"ts": 1, "issue": "34", "event": "step-start"}\n'
          '{"ts": 2, "issue": "34", "event": "launch", "name": "develop-red"}\n'
          '{"ts": 3, "issue": "34", "event": "bail", "reason": "killed-stuck"}\n')

    def fake_run(args, cwd=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/metrics"])

    dashboard.main([])

    assert not os.path.exists(os.path.join(run, ".tdd", "issue-34-metrics.md"))
    (metrics,) = served[0][1]
    report = json.loads(body(metrics))["issues"]["34"]
    assert report.strip()
    assert "issue-34-metrics.md" in report


def test_get_api_metrics_recomputes_run_35_whose_log_carries_a_stop_mark_and_no_done_or_bail(
        tmp_path, monkeypatch, dashboard, run_cli):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "35")
    write(os.path.join(run, ".tdd", "issue-35.md"), "# Plan for #35\n\n- [ ] a lamp glows\n")
    write(os.path.join(run, ".tdd", "events.jsonl"),
          '{"ts": 1, "issue": "35", "event": "step-start"}\n'
          '{"ts": 2, "issue": "35", "event": "launch", "name": "develop-red"}\n'
          '{"ts": 3, "issue": "35", "event": "stop", "mode": "at-leaf", "at": "planned"}\n')
    recomputed = report_of(run_cli, "35", run)
    served = serve_with_real_metrics(monkeypatch, tmp_path)

    dashboard.main([])
    assert os.getcwd() == str(tmp_path)

    (metrics,) = served[0][1]
    assert json.loads(body(metrics))["issues"]["35"] == recomputed


def test_get_api_metrics_keys_issues_by_the_run_directory_7_alone_and_answers_the_report_of_its_own_log(
        tmp_path, monkeypatch, dashboard, run_cli):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "7")
    write(os.path.join(run, ".tdd", "issue-7.md"),
          "# Plan for #7 — lamps glow\n\n- [x] a lamp exists\n- [ ] a lamp glows\n")
    for other in ("3", "5"):
        write(os.path.join(run, ".tdd", "issue-%s.md" % other),
              "# Plan for #%s — an earlier run's committed plan\n\n- [x] a lamp is wired\n" % other)
    write(os.path.join(run, ".tdd", "events.jsonl"),
          '{"ts": 1, "issue": "7", "event": "step-start"}\n'
          '{"ts": 2, "issue": "7", "event": "launch", "name": "develop-red"}\n')
    want = report_of(run_cli, "7", run)
    served = serve_with_real_metrics(monkeypatch, tmp_path)

    dashboard.main([])
    assert os.getcwd() == str(tmp_path)

    (metrics,) = served[0][1]
    issues = json.loads(body(metrics))["issues"]
    assert sorted(issues) == ["7"]
    assert issues["7"] == want


def test_get_api_events_answers_run_51s_logged_events_in_file_order_and_none_for_issue_99(
        tmp_path, monkeypatch, dashboard):
    selected = os.path.join(str(tmp_path), ".tdd", "wt", "51")
    other = os.path.join(str(tmp_path), ".tdd", "wt", "52")
    write(os.path.join(selected, ".tdd", "issue-51.md"),
          "# Plan for #51 — lamps flicker\n\n- [x] a lamp exists\n- [ ] a lamp flickers\n")
    logged = [{"ts": 1000 + i * 10, "issue": "51", "actor": "developer", "phase": "red",
               "step": "a lamp flickers", "event": "launch", "attempt": str(i),
               "skill_commit": "abc", "name": "develop-red", "seq": i} for i in range(1, 31)]
    write(os.path.join(selected, ".tdd", "events.jsonl"),
          "".join(json.dumps(event) + "\n" for event in logged))
    write(os.path.join(other, ".tdd", "issue-52.md"), "# Plan for #52 — lamps dim\n\n- [ ] a lamp dims\n")
    write(os.path.join(other, ".tdd", "events.jsonl"),
          '{"ts": 2000, "issue": "52", "event": "step-start", "seq": 1}\n'
          '{"ts": 2100, "issue": "52", "event": "launch", "name": "develop-green", "seq": 2}\n')

    def fake_run(args, cwd=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/events?issue=51", "/api/events?issue=99"])

    dashboard.main([])

    events, none = served[0][1]
    assert json.loads(body(events))["events"] == logged
    assert json.loads(body(none)) == {"events": []}


def test_get_api_events_answers_the_empty_list_for_issue_3_held_only_as_a_ledger_copy_inside_run_7(
        tmp_path, monkeypatch, dashboard):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "7")
    write(os.path.join(run, ".tdd", "issue-7.md"),
          "# Plan for #7 — lamps glow\n\n- [x] a lamp exists\n- [ ] a lamp glows\n")
    write(os.path.join(run, ".tdd", "issue-3.md"),
          "# Plan for #3 — an earlier run's committed plan\n\n- [x] a lamp is wired\n")
    logged = [{"ts": 1000, "issue": "7", "actor": "conductor", "phase": "", "step": "a lamp glows",
               "event": "step-start", "attempt": "", "skill_commit": "abc", "seq": 1},
              {"ts": 1010, "issue": "7", "actor": "developer", "phase": "red",
               "step": "a lamp glows", "event": "launch", "attempt": "1", "skill_commit": "abc",
               "name": "develop-red", "seq": 2}]
    write(os.path.join(run, ".tdd", "events.jsonl"),
          "".join(json.dumps(event) + "\n" for event in logged))

    def fake_run(args, cwd=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/events?issue=3", "/api/events?issue=7"])

    dashboard.main([])

    three, seven = served[0][1]
    assert json.loads(body(three)) == {"events": []}
    assert json.loads(body(seven))["events"] == logged


def test_get_api_tests_answers_run_51s_two_make_test_runs_from_its_leaf_log_when_it_has_no_event_log(
        tmp_path, monkeypatch, dashboard):
    selected = os.path.join(str(tmp_path), ".tdd", "wt", "51")
    other = os.path.join(str(tmp_path), ".tdd", "wt", "52")
    write(os.path.join(selected, ".tdd", "issue-51.md"),
          "# Plan for #51 — lamps flicker\n\n- [ ] a lamp flickers\n")
    write(os.path.join(selected, ".tdd", "issue-51-spec.md"),
          "## What to build\n\nA lamp flickers.\n\nTest command: make test\n")
    red_fail = "FAIL - a lamp flickers\n----\n11 passed, 1 failed"
    red_pass = "----\n12 passed, 0 failed"

    def call(use_id, command):
        return {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": use_id, "name": "Bash",
             "input": {"command": command, "description": "a call"}}]}}

    def result(use_id, content, is_error):
        return {"type": "user", "message": {"role": "user", "content": [
            {"tool_use_id": use_id, "type": "tool_result", "content": content,
             "is_error": is_error}]}}

    records = [
        {"type": "system", "subtype": "init", "session_id": "s1", "tools": ["Bash"]},
        call("toolu_1", "git log --oneline -3"),
        result("toolu_1", "abc1234 plan: a lamp flickers", False),
        call("toolu_2", "make test"), result("toolu_2", red_fail, True),
        call("toolu_3", "make test"), result("toolu_3", red_pass, False),
        {"type": "result", "subtype": "success", "is_error": False, "result": "The case is added."},
    ]
    write(os.path.join(selected, ".tdd", "develop-red.out"),
          "".join(json.dumps(record) + "\n" for record in records))
    write(os.path.join(other, ".tdd", "issue-52.md"), "# Plan for #52 — lamps dim\n\n- [ ] a lamp dims\n")
    write(os.path.join(other, ".tdd", "issue-52-spec.md"),
          "## What to build\n\nA lamp dims.\n\nTest command: make test\n")
    write(os.path.join(other, ".tdd", "develop-green.out"),
          json.dumps(call("toolu_9", "make test")) + "\n"
          + json.dumps(result("toolu_9", "----\n7 passed, 0 failed  (run 52)", False)) + "\n")

    def fake_run(args, cwd=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/tests?issue=51"])

    dashboard.main([])

    assert not os.path.exists(os.path.join(selected, ".tdd", "events.jsonl"))
    (tests,) = served[0][1]
    runs = json.loads(body(tests))["tests"]
    assert [(entry["command"], entry["passed"]) for entry in runs] == [
        ("make test", False), ("make test", True)]
    for entry, output in zip(runs, (red_fail, red_pass)):
        assert entry["tail"] and output.endswith(entry["tail"])
        assert output.splitlines()[-1] in entry["tail"]


def test_get_api_tests_answers_run_53s_one_run_of_its_spec_command_and_never_executes_it(
        tmp_path, monkeypatch, dashboard):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "53")
    marker = os.path.join(str(tmp_path), "tests-noexec-trace")
    command = "sh -c 'echo executed > %s'" % marker
    write(os.path.join(run, ".tdd", "issue-53.md"), "# Plan for #53 — lamps hum\n\n- [ ] a lamp hums\n")
    write(os.path.join(run, ".tdd", "issue-53-spec.md"),
          "## What to build\n\nA lamp hums.\n\nTest command: %s\n" % command)
    records = [
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_1", "name": "Bash",
             "input": {"command": command, "description": "Run the suite"}}]}},
        {"type": "user", "message": {"role": "user", "content": [
            {"tool_use_id": "toolu_1", "type": "tool_result", "content": "----\n3 passed, 0 failed",
             "is_error": False}]}},
    ]
    write(os.path.join(run, ".tdd", "develop-red.out"),
          "".join(json.dumps(record) + "\n" for record in records))
    calls = []

    def fake_run(args, cwd=None, **kwargs):
        calls.append(args)
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/tests?issue=53"])

    dashboard.main([])

    (tests,) = served[0][1]
    assert [entry["command"] for entry in json.loads(body(tests))["tests"]] == [command]
    assert not os.path.exists(marker)
    assert not [args for args in calls if command in (args if isinstance(args, str) else " ".join(args))]


def test_get_api_tests_answers_run_54s_three_test_run_marks_not_its_one_make_test_leaf_call(
        tmp_path, monkeypatch, dashboard):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "54")
    write(os.path.join(run, ".tdd", "issue-54.md"), "# Plan for #54 — lamps buzz\n\n- [ ] a lamp buzzes\n")
    write(os.path.join(run, ".tdd", "issue-54-spec.md"),
          "## What to build\n\nA lamp buzzes.\n\nTest command: make test\n")
    suite = "skills/tdd/scripts/tests/lamp.test.sh"
    marks = [{"ts": 1000, "issue": "54", "actor": "conductor", "phase": "", "step": "a lamp buzzes",
              "event": "step-start", "attempt": "", "skill_commit": "abc"}]
    marks += [{"ts": 1060 + i * 60, "issue": "54", "actor": "", "phase": "", "step": "a lamp buzzes",
               "event": "test-run", "attempt": "", "skill_commit": "abc", "tier": tier,
               "suites": suites, "seconds": "3", "status": status}
              for i, (tier, suites, status) in enumerate(
                  [("fast", "", "0"), ("affected", suite, "1"), ("target", suite, "0")])]
    write(os.path.join(run, ".tdd", "events.jsonl"),
          "".join(json.dumps(mark) + "\n" for mark in marks))
    records = [
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_1", "name": "Bash",
             "input": {"command": "make test", "description": "Run the suite"}}]}},
        {"type": "user", "message": {"role": "user", "content": [
            {"tool_use_id": "toolu_1", "type": "tool_result", "content": "----\n4 passed, 0 failed",
             "is_error": False}]}},
    ]
    write(os.path.join(run, ".tdd", "develop-red.out"),
          "".join(json.dumps(record) + "\n" for record in records))

    def fake_run(args, cwd=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/tests?issue=54"])

    dashboard.main([])

    (tests,) = served[0][1]
    assert len(json.loads(body(tests))["tests"]) == 3


def test_get_api_tests_answers_run_56s_suites_and_passed_from_test_run_marks_of_status_0_1_0(
        tmp_path, monkeypatch, dashboard):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "56")
    write(os.path.join(run, ".tdd", "issue-56.md"),
          "# Plan for #56 — lamps gutter\n\n- [ ] a lamp gutters\n")
    write(os.path.join(run, ".tdd", "issue-56-spec.md"),
          "## What to build\n\nA lamp gutters.\n\nTest command: make test\n")
    gutter = "skills/tdd/scripts/tests/gutter.test.sh"
    flicker = "skills/tdd/scripts/tests/flicker.test.sh"
    marks = [{"ts": 1000, "issue": "56", "actor": "conductor", "phase": "", "step": "a lamp gutters",
              "event": "step-start", "attempt": "", "skill_commit": "abc"}]
    marks += [{"ts": 1060 + i * 60, "issue": "56", "actor": "", "phase": "", "step": "a lamp gutters",
               "event": "test-run", "attempt": "", "skill_commit": "abc", "tier": tier,
               "suites": suites, "seconds": "3", "status": status}
              for i, (tier, suites, status) in enumerate(
                  [("fast", "", "0"), ("affected", gutter, "1"), ("target", flicker, "0")])]
    write(os.path.join(run, ".tdd", "events.jsonl"),
          "".join(json.dumps(mark) + "\n" for mark in marks))

    def fake_run(args, cwd=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/tests?issue=56"])

    dashboard.main([])

    (tests,) = served[0][1]
    assert [(entry["suites"], entry["passed"]) for entry in json.loads(body(tests))["tests"]] == [
        ("", True), (gutter, False), (flicker, True)]


def test_get_api_tests_answers_run_57_with_no_test_run_mark_the_empty_list_beside_its_leaf_call_and_run_58s_marks(
        tmp_path, monkeypatch, dashboard):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "57")
    write(os.path.join(run, ".tdd", "issue-57.md"),
          "# Plan for #57 — lamps sputter\n\n- [ ] a lamp sputters\n")
    write(os.path.join(run, ".tdd", "issue-57-spec.md"),
          "## What to build\n\nA lamp sputters.\n\nTest command: make test\n")
    events = [{"ts": 1000, "issue": "57", "actor": "conductor", "phase": "", "step": "a lamp sputters",
               "event": "step-start", "attempt": "", "skill_commit": "abc"},
              {"ts": 1060, "issue": "57", "actor": "conductor", "phase": "develop-red",
               "step": "a lamp sputters", "event": "launch", "attempt": "1", "skill_commit": "abc",
               "name": "develop-red"}]
    write(os.path.join(run, ".tdd", "events.jsonl"),
          "".join(json.dumps(event) + "\n" for event in events))
    records = [
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_1", "name": "Bash",
             "input": {"command": "make test", "description": "Run the suite"}}]}},
        {"type": "user", "message": {"role": "user", "content": [
            {"tool_use_id": "toolu_1", "type": "tool_result", "content": "----\n5 passed, 0 failed",
             "is_error": False}]}},
    ]
    write(os.path.join(run, ".tdd", "develop-red.out"),
          "".join(json.dumps(record) + "\n" for record in records))
    other = os.path.join(str(tmp_path), ".tdd", "wt", "58")
    write(os.path.join(other, ".tdd", "issue-58.md"),
          "# Plan for #58 — lamps glare\n\n- [ ] a lamp glares\n")
    write(os.path.join(other, ".tdd", "issue-58-spec.md"),
          "## What to build\n\nA lamp glares.\n\nTest command: make test\n")
    suite = "skills/tdd/scripts/tests/glare.test.sh"
    marks = [{"ts": 1060 + i * 60, "issue": "58", "actor": "", "phase": "", "step": "a lamp glares",
              "event": "test-run", "attempt": "", "skill_commit": "abc", "tier": tier,
              "suites": suites, "seconds": "3", "status": "0"}
             for i, (tier, suites) in enumerate([("fast", ""), ("affected", suite), ("target", suite)])]
    write(os.path.join(other, ".tdd", "events.jsonl"),
          "".join(json.dumps(mark) + "\n" for mark in marks))

    def fake_run(args, cwd=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/tests?issue=57"])

    dashboard.main([])

    (tests,) = served[0][1]
    assert json.loads(body(tests))["tests"] == []


def test_get_api_chatter_answers_the_rendering_of_run_54s_verify_green_out_the_leaf_its_newest_launch_names(
        tmp_path, monkeypatch, dashboard):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "54")
    write(os.path.join(run, ".tdd", "issue-54.md"),
          "# Plan for #54 — lamps buzz\n\n- [x] a lamp buzzes\n- [ ] a lamp stops buzzing\n")
    red = [
        {"type": "system", "subtype": "init", "session_id": "s1", "tools": ["Bash"]},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "Adding the case that pins the buzz."}]}},
    ]
    green = [
        {"type": "system", "subtype": "init", "session_id": "s2", "tools": ["Bash"]},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "Reading the diff against the spec."}]}},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "VERDICT: PASS"}]}},
    ]
    red_log = "".join(json.dumps(record) + "\n" for record in red)
    green_log = "".join(json.dumps(record) + "\n" for record in green)
    write(os.path.join(run, ".tdd", "develop-red.out"), red_log)
    write(os.path.join(run, ".tdd", "verify-green.out"), green_log)
    events = [{"ts": 1000, "issue": "54", "actor": "conductor", "phase": "", "step": "a lamp stops buzzing",
               "event": "step-start", "attempt": "", "skill_commit": "abc"},
              {"ts": 1010, "issue": "54", "actor": "developer", "phase": "red",
               "step": "a lamp stops buzzing", "event": "launch", "attempt": "1",
               "skill_commit": "abc", "name": "develop-red"},
              {"ts": 1200, "issue": "54", "actor": "verifier", "phase": "green",
               "step": "a lamp stops buzzing", "event": "launch", "attempt": "1",
               "skill_commit": "abc", "name": "verify-green"}]
    write(os.path.join(run, ".tdd", "events.jsonl"),
          "".join(json.dumps(event) + "\n" for event in events))
    rendered = "Reading the diff against the spec.\nVERDICT: PASS\n"

    def fake_run(args, cwd=None, input=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/chatter?issue=54"])

    dashboard.main([])

    (chatter,) = served[0][1]
    assert json.loads(body(chatter)) == {"chatter": rendered}


def test_get_api_chatter_gives_its_full_answer_for_run_66_when_starting_render_leaf_log_sh_as_a_process_is_refused(
        tmp_path, monkeypatch, dashboard, capfd):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "66")
    write(os.path.join(run, ".tdd", "issue-66.md"),
          "# Plan for #66 — lamps hum\n\n- [ ] a lamp stops humming\n")
    records = [
        {"type": "system", "subtype": "init", "session_id": "s6", "tools": ["Bash"]},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "Making the hum case pass."}]}},
    ]
    write(os.path.join(run, ".tdd", "develop-green.out"),
          "".join(json.dumps(record) + "\n" for record in records))
    events = [{"ts": 1000, "issue": "66", "actor": "conductor", "phase": "", "step": "a lamp stops humming",
               "event": "step-start", "attempt": "", "skill_commit": "abc"},
              {"ts": 1010, "issue": "66", "actor": "developer", "phase": "green",
               "step": "a lamp stops humming", "event": "launch", "attempt": "1",
               "skill_commit": "abc", "name": "develop-green"}]
    write(os.path.join(run, ".tdd", "events.jsonl"),
          "".join(json.dumps(event) + "\n" for event in events))
    before = sorted(os.listdir(os.path.join(run, ".tdd")))
    real_popen = subprocess.Popen

    def refuse(argv):
        if "render-leaf-log.sh" in str(argv):
            raise AssertionError("started render-leaf-log.sh as a process: %r" % (argv,))

    def refusing_run(args, cwd=None, input=None, **kwargs):
        refuse(args)
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    def refusing_popen(argv, *args, **kwargs):
        refuse(argv)
        return real_popen(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", refusing_run)
    monkeypatch.setattr(subprocess, "Popen", refusing_popen)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/chatter?issue=66"])
    capfd.readouterr()

    code = dashboard.main([])

    (chatter,) = served[0][1]
    assert code == 0
    assert status_code(chatter) == b"200"
    assert json.loads(body(chatter)) == {"chatter": "Making the hum case pass.\n"}
    assert capfd.readouterr().err == ""
    assert sorted(os.listdir(os.path.join(run, ".tdd"))) == before


def test_get_api_chatter_answers_the_empty_rendering_with_nothing_on_stderr_for_runs_71_72_and_73_whose_leaf_logs_hold_a_json_line_render_leaf_log_cannot_render(
        tmp_path, monkeypatch, dashboard, capfd):
    lines = {
        "71": "42",
        "72": json.dumps({"message": {"content": "hi"}}),
        "73": json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "input": {"command": "ls"}}]}}),
    }
    for issue, line in lines.items():
        run = os.path.join(str(tmp_path), ".tdd", "wt", issue)
        write(os.path.join(run, ".tdd", "issue-%s.md" % issue),
              "# Plan for #%s — lamps hum\n\n- [ ] a lamp stops humming\n" % issue)
        write(os.path.join(run, ".tdd", "develop-green.out"), line + "\n")
        events = [{"ts": 1000, "issue": issue, "actor": "conductor", "phase": "",
                   "step": "a lamp stops humming", "event": "step-start", "attempt": "",
                   "skill_commit": "abc"},
                  {"ts": 1010, "issue": issue, "actor": "developer", "phase": "green",
                   "step": "a lamp stops humming", "event": "launch", "attempt": "1",
                   "skill_commit": "abc", "name": "develop-green"}]
        write(os.path.join(run, ".tdd", "events.jsonl"),
              "".join(json.dumps(event) + "\n" for event in events))

    def fake_run(args, cwd=None, input=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/chatter?issue=%s" % issue for issue in lines])
    capfd.readouterr()

    dashboard.main([])

    answers = served[0][1]
    assert [status_code(answer) for answer in answers] == [b"200"] * 3
    assert [json.loads(body(answer)) for answer in answers] == [{"chatter": ""}] * 3
    assert capfd.readouterr().err == ""


def test_get_api_chatter_answers_the_rendering_of_run_59s_verify_red_log_when_no_verify_red_out_exists(
        tmp_path, monkeypatch, dashboard):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "59")
    write(os.path.join(run, ".tdd", "issue-59.md"),
          "# Plan for #59 — lamps flare\n\n- [ ] a lamp stops flaring\n")
    records = [
        {"type": "system", "subtype": "init", "session_id": "s3", "tools": ["Bash"]},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "Reading the new case against the spec."}]}},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "VERDICT: PASS"}]}},
    ]
    verify_log = "".join(json.dumps(record) + "\n" for record in records)
    write(os.path.join(run, ".tdd", "verify-red.log"), verify_log)
    events = [{"ts": 1000, "issue": "59", "actor": "conductor", "phase": "", "step": "a lamp stops flaring",
               "event": "step-start", "attempt": "", "skill_commit": "abc"},
              {"ts": 1080, "issue": "59", "actor": "verifier", "phase": "red",
               "step": "a lamp stops flaring", "event": "launch", "attempt": "1",
               "skill_commit": "abc", "name": "verify-red"}]
    write(os.path.join(run, ".tdd", "events.jsonl"),
          "".join(json.dumps(event) + "\n" for event in events))
    rendered = "Reading the new case against the spec.\nVERDICT: PASS\n"

    def fake_run(args, cwd=None, input=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/chatter?issue=59"])

    dashboard.main([])

    (chatter,) = served[0][1]
    assert json.loads(body(chatter)) == {"chatter": rendered}


def test_get_api_chatter_answers_the_rendering_of_the_four_stream_json_lines_of_run_61s_develop_green_log(
        tmp_path, monkeypatch, dashboard):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "61")
    write(os.path.join(run, ".tdd", "issue-61.md"),
          "# Plan for #61 — lamps flicker\n\n- [ ] a lamp stops flickering\n")
    records = [
        {"type": "system", "subtype": "init", "session_id": "s4", "tools": ["Bash"]},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "Making the flicker case pass."}]}},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_9", "name": "Bash",
             "input": {"command": "make test", "description": "Run the suite"}}]}},
        {"type": "user", "message": {"role": "user", "content": [
            {"tool_use_id": "toolu_9", "type": "tool_result", "content": "10 passed, 0 failed",
             "is_error": False}]}},
    ]
    record_lines = "".join(json.dumps(record) + "\n" for record in records)
    write(os.path.join(run, ".tdd", "develop-green.log"),
          record_lines + "\n" + "The step is green: 10 passed, 0 failed.\n")
    events = [{"ts": 1000, "issue": "61", "actor": "conductor", "phase": "",
               "step": "a lamp stops flickering", "event": "step-start", "attempt": "",
               "skill_commit": "abc"},
              {"ts": 1250, "issue": "61", "actor": "developer", "phase": "green",
               "step": "a lamp stops flickering", "event": "launch", "attempt": "1",
               "skill_commit": "abc", "name": "develop-green"}]
    write(os.path.join(run, ".tdd", "events.jsonl"),
          "".join(json.dumps(event) + "\n" for event in events))
    rendered = "Making the flicker case pass.\n> Bash: make test\n< 10 passed, 0 failed\n"

    def fake_run(args, cwd=None, input=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/chatter?issue=61"])

    dashboard.main([])

    (chatter,) = served[0][1]
    assert json.loads(body(chatter)) == {"chatter": rendered}


def test_rendering_a_log_tailed_by_plain_text_does_not_open_the_log_in_dashboard_py_itself(
        tmp_path, monkeypatch, dashboard):
    record = {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "text", "text": "Making the flicker case pass."}]}}
    log = tmp_path / "develop-green.log"
    log.write_text(json.dumps(record) + "\n\nThe step is green.\n")

    def refuse(*args, **kwargs):
        raise AssertionError("dashboard.py opened " + str(args[0]))

    monkeypatch.setattr(dashboard, "open", refuse, raising=False)

    assert dashboard.rendered_log(str(log)) == "Making the flicker case pass.\n"


def test_get_api_chatter_answers_the_empty_rendering_for_run_63_on_no_leaf_and_run_65_whose_leaf_wrote_nothing(
        tmp_path, monkeypatch, dashboard):
    noleaf = os.path.join(str(tmp_path), ".tdd", "wt", "63")
    write(os.path.join(noleaf, ".tdd", "issue-63.md"),
          "# Plan for #63 — lamps dim\n\n- [ ] a lamp stops dimming\n")
    write(os.path.join(noleaf, ".tdd", "events.jsonl"),
          json.dumps({"ts": 1000, "issue": "63", "actor": "conductor", "phase": "",
                      "step": "a lamp stops dimming", "event": "step-start", "attempt": "",
                      "skill_commit": "abc"}) + "\n")
    nolog = os.path.join(str(tmp_path), ".tdd", "wt", "65")
    write(os.path.join(nolog, ".tdd", "issue-65.md"),
          "# Plan for #65 — lamps hum\n\n- [ ] a lamp stops humming\n")
    events = [{"ts": 1000, "issue": "65", "actor": "conductor", "phase": "",
               "step": "a lamp stops humming", "event": "step-start", "attempt": "",
               "skill_commit": "abc"},
              {"ts": 1060, "issue": "65", "actor": "developer", "phase": "red",
               "step": "a lamp stops humming", "event": "launch", "attempt": "1",
               "skill_commit": "abc", "name": "develop-red"}]
    write(os.path.join(nolog, ".tdd", "events.jsonl"),
          "".join(json.dumps(event) + "\n" for event in events))

    def fake_run(args, cwd=None, input=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/chatter?issue=63", "/api/chatter?issue=65"])

    dashboard.main([])

    (noleaf_chatter, nolog_chatter) = served[0][1]
    assert json.loads(body(noleaf_chatter)) == {"chatter": ""}
    assert json.loads(body(nolog_chatter)) == {"chatter": ""}


def test_get_api_chatter_for_run_55_twice_answers_the_rendering_of_develop_red_out_then_develop_green_out_after_its_launch(
        tmp_path, monkeypatch, dashboard):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "55")
    write(os.path.join(run, ".tdd", "issue-55.md"), "# Plan for #55 — lamps dim\n\n- [ ] a lamp dims\n")
    red = [
        {"type": "system", "subtype": "init", "session_id": "s1", "tools": ["Bash"]},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "Adding the case that pins the dimming."}]}},
    ]
    green = [
        {"type": "system", "subtype": "init", "session_id": "s2", "tools": ["Bash"]},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "Making the dimming case pass."}]}},
    ]
    red_log = "".join(json.dumps(record) + "\n" for record in red)
    green_log = "".join(json.dumps(record) + "\n" for record in green)
    write(os.path.join(run, ".tdd", "develop-red.out"), red_log)
    write(os.path.join(run, ".tdd", "develop-green.out"), green_log)
    log = os.path.join(run, ".tdd", "events.jsonl")
    events = [{"ts": 1000, "issue": "55", "actor": "conductor", "phase": "", "step": "a lamp dims",
               "event": "step-start", "attempt": "", "skill_commit": "abc"},
              {"ts": 1010, "issue": "55", "actor": "developer", "phase": "red", "step": "a lamp dims",
               "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}]
    write(log, "".join(json.dumps(event) + "\n" for event in events))

    def fake_run(args, cwd=None, input=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    def requests():
        yield "/api/chatter?issue=55"
        with open(log, "a") as f:
            f.write(json.dumps({"ts": 1300, "issue": "55", "actor": "developer", "phase": "green",
                                "step": "a lamp dims", "event": "launch", "attempt": "1",
                                "skill_commit": "abc", "name": "develop-green"}) + "\n")
        yield "/api/chatter?issue=55"

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, requests())

    dashboard.main([])

    (first, second) = served[0][1]
    assert json.loads(body(first)) == {"chatter": "Adding the case that pins the dimming.\n"}
    assert json.loads(body(second)) == {"chatter": "Making the dimming case pass.\n"}


ROOT = SCRIPTS.parents[2]
PAGE = SCRIPTS / "dashboard.html"
QUOTES = "\"'`"


@pytest.mark.process("make -n test starts to print the roster of suites make test runs")
def test_make_test_names_test_dashboard_py_in_its_roster():
    roster = subprocess.run(["make", "--no-print-directory", "-n", "-C", str(ROOT), "test"],
                            capture_output=True, text=True).stdout
    assert "skills/tdd/scripts/tests/py/test_dashboard.py" in roster


def fetched_paths(page):
    """Every path a fetch of a literal asks for, as the literal's text up to its closing quote."""
    return re.findall(r"fetch\s*\(\s*[\"'`]([^\"'`]*)", page)


def asks_for(page, path):
    return any(literal.startswith(path) for literal in fetched_paths(page))


def assert_page_fetches(*paths):
    page = PAGE.read_text()
    for path in paths:
        assert asks_for(page, path), "the page never fetches %s" % path


def test_dashboard_html_fetches_the_runs_metrics_and_events_endpoints():
    assert_page_fetches("/api/runs", "/api/metrics", "/api/events")


def test_dashboard_html_gives_the_tests_and_chatter_panes_an_endpoint_apiece_to_poll():
    assert_page_fetches("/api/tests", "/api/chatter")


def code_only(src):
    """<src> with the inside of every string literal and comment blanked, every index unchanged."""
    out, i, n = list(src), 0, len(src)
    while i < n:
        c = src[i]
        if c in QUOTES:
            i += 1
            while i < n and src[i] != c:
                if src[i] == "\\":
                    out[i] = " "
                    i += 1
                if i < n:
                    out[i] = " "
                    i += 1
            i += 1
        elif src[i:i + 2] == "//":
            while i < n and src[i] != "\n":
                out[i] = " "
                i += 1
        elif src[i:i + 2] == "/*":
            while i < n and src[i:i + 2] != "*/":
                out[i] = " "
                i += 1
            out[i:i + 2] = "  "
            i += 2
        else:
            i += 1
    return "".join(out)


def call_end(src, i):
    """The index just past the ")" closing a call whose "(" is at src[i - 1], or -1."""
    depth = 1
    while i < len(src):
        if src[i] in "([{":
            depth += 1
        elif src[i] in ")]}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def calls(code, pattern):
    for m in re.finditer(pattern + r"\s*\(", code):
        yield m, call_end(code, m.end())


def last_argument(args):
    depth, cut = 0, 0
    for j, c in enumerate(args):
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == "," and depth == 0:
            cut = j + 1
    return args[cut:].strip()


def test_dashboard_html_schedules_each_panes_next_request_only_from_the_previous_one_settling():
    code = code_only(PAGE.read_text())
    assert [m.group(0) for m, _ in calls(code, r"\bsetInterval")] == [], \
        "a pane fires on a fixed clock rather than on its previous request answering"
    spans = [(m.group(1), m.end(), end - 1)
             for m, end in calls(code, r"\.(then|catch|finally)") if end > 0]
    timers = list(calls(code, r"\bsetTimeout"))
    assert timers, "no pane schedules its next request from its previous one settling"
    resolve = reject = False
    for m, end in timers:
        kinds = [kind for kind, a, b in spans if a <= m.start() < b]
        assert kinds, "setTimeout outside every .then, .catch and .finally body"
        resolve = resolve or bool({"then", "finally"} & set(kinds))
        reject = reject or bool({"catch", "finally"} & set(kinds))
        assert end > 0 and last_argument(code[m.end():end - 1]) == "2000", \
            "a pane reschedules other than 2000 ms after the previous request settled"
    assert resolve, "no setTimeout sits in a .then or .finally body"
    assert reject, "no setTimeout sits in a .catch or .finally body"


def header(answer, name):
    head = answer.partition(b"\r\n\r\n")[0].decode().split("\r\n")[1:]
    return dict(line.split(": ", 1) for line in head).get(name)


def test_dashboard_sh_with_no_argument_serves_the_page_at_slash_on_port_8765_and_exits_0_when_sent_sigint(
        monkeypatch, dashboard, run_cli):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    served = fake_server(monkeypatch, ["/"])

    code, out, err = run_cli(dashboard, [])

    assert code == 0
    assert [address for address, _ in served] == [("127.0.0.1", 8765)]
    (page,) = served[0][1]
    assert status_code(page) == b"200"
    assert header(page, "Content-Type").startswith("text/html")
    assert b"<html" in body(page) and b"</html>" in body(page)
    assert signal.getsignal(signal.SIGINT) is signal.default_int_handler


def runs_without_elapsed(document):
    for run in document["runs"]:
        run.pop("elapsed_seconds", None)
    return document


@pytest.mark.process("the git status starts for /api/runs, a fake one first on PATH")
def test_dashboard_sh_with_a_port_argument_serves_the_page_on_that_port_binds_127_0_0_1_only_and_answers_every_pane_endpoint_with_json(
        tmp_path, monkeypatch, dashboard, run_cli):
    fabricated_main_tree(tmp_path, monkeypatch)
    run = tmp_path / ".tdd" / "wt" / "51"
    write(str(run / ".tdd" / "issue-51.md"), "# Plan for #51 \u2014 lamps hum\n\n- [x] a lamp exists\n- [ ] a lamp hums\n")
    write(str(run / ".tdd" / "events.jsonl"),
          '{"ts": 1, "issue": "51", "actor": "conductor", "phase": "", "step": "a lamp hums", '
          '"event": "step-start", "attempt": "", "skill_commit": "abc"}\n'
          '{"ts": 2, "issue": "51", "actor": "developer", "phase": "red", "step": "a lamp hums", '
          '"event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}\n')
    served = fake_server(monkeypatch, ["/", "/api/runs", "/api/metrics", "/api/events?issue=51"])

    code = dashboard.main(["4251"])

    assert code == 0
    assert [address for address, _ in served] == [("127.0.0.1", 4251)]
    page, runs, metrics, events = served[0][1]
    assert [status_code(a) for a in served[0][1]] == [b"200"] * 4
    assert header(page, "Content-Type").startswith("text/html")
    for answer in (runs, metrics, events):
        assert header(answer, "Content-Type").startswith("application/json")
    code, out, err = run_cli(importlib.import_module("veri.status"), ["--json"])
    assert code == 0
    served_51, = [run for run in json.loads(body(runs))["runs"] if run["issue"] == "51"]
    status_51, = [run for run in json.loads(out)["runs"] if run["issue"] == "51"]
    assert abs(served_51["elapsed_seconds"] - status_51["elapsed_seconds"]) <= 10
    assert runs_without_elapsed(json.loads(body(runs))) == runs_without_elapsed(json.loads(out))
    assert json.loads(body(runs))["runs"]
    assert json.loads(body(metrics))["issues"]["51"]
    assert [e["event"] for e in json.loads(body(events))["events"]] == ["step-start", "launch"]


def test_the_page_dashboard_sh_serves_at_slash_is_dashboard_html_byte_for_byte(
        monkeypatch, dashboard, run_cli):
    served = fake_server(monkeypatch, ["/"])

    code, out, err = run_cli(dashboard, [])

    assert code == 0
    (page,) = served[0][1]
    with open(os.path.join(SCRIPTS, "dashboard.html"), "rb") as f:
        assert body(page) == f.read()


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def fetch(url, deadline=10):
    """The body of GET <url>, retried while nothing listens yet."""
    end = time.time() + deadline
    while True:
        try:
            with urllib.request.urlopen(url, timeout=deadline) as answer:
                return answer.read()
        except ConnectionRefusedError:
            if time.time() > end:
                raise
            time.sleep(0.02)
        except urllib.error.URLError as exc:
            if not isinstance(exc.reason, ConnectionRefusedError) or time.time() > end:
                raise
            time.sleep(0.02)


@pytest.mark.process("a real listening server answers /api/events while /api/runs waits on a blocked git status starts")
def test_api_events_answers_while_an_api_runs_request_is_still_blocked_inside_a_process_status_starts(
        tmp_path, monkeypatch, dashboard):
    run = tmp_path / ".tdd" / "wt" / "77"
    write(str(run / ".tdd" / "issue-77.md"), "# Plan for #77 \u2014 a kettle boils\n\n- [ ] a kettle boils\n")
    write(str(run / ".tdd" / "events.jsonl"),
          '{"ts": 1, "issue": "77", "actor": "conductor", "phase": "", "step": "a kettle boils", '
          '"event": "step-start", "attempt": "", "skill_commit": "abc"}\n')
    monkeypatch.chdir(tmp_path)
    entered, release = threading.Event(), threading.Event()
    real_run = subprocess.run

    def fake_run(args, *rest, **kwargs):
        args = list(args)
        if args[:2] == ["git", "worktree"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out if kwargs.get("text") else out.encode(), "" if kwargs.get("text") else b"")
        if "symbolic-ref" in args:
            entered.set()
            release.wait(20)
            return subprocess.CompletedProcess(args, 0, "tdd/77-a-kettle-boils\n", "")
        return real_run(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", fake_run)
    port = free_port()
    base = "http://127.0.0.1:%d" % port
    seen = {}

    def runs_request():
        try:
            seen["runs"] = fetch(base + "/api/runs", 30)
        except Exception as exc:
            seen["runs_error"] = exc

    def client():
        try:
            fetch(base + "/")
            pending = threading.Thread(target=runs_request)
            pending.start()
            seen["entered"] = entered.wait(10)
            seen["events"] = fetch(base + "/api/events?issue=77", 5)
            seen["runs_settled"] = "runs" in seen
            release.set()
            pending.join(10)
        except Exception as exc:
            seen["error"] = exc
        finally:
            release.set()
            os.kill(os.getpid(), signal.SIGINT)

    helper = threading.Thread(target=client)
    helper.start()
    code = dashboard.main([str(port)])
    helper.join(10)

    assert code == 0
    assert "error" not in seen, seen
    assert seen["entered"], "the /api/runs request never reached the process status starts"
    assert seen["runs_settled"] is False
    assert [e["event"] for e in json.loads(seen["events"])["events"]] == ["step-start"]


@pytest.mark.process("a symlinked dashboard.sh run as a child from another working directory")
def test_dashboard_sh_run_through_a_symlink_to_the_skill_directory_and_from_another_working_directory_serves_dashboard_html_at_slash_and_status_sh_json_stdout_at_api_runs(
        tmp_path, monkeypatch, run_cli):
    fabricated_main_tree(tmp_path, monkeypatch)
    want = status_document(run_cli)
    link = tmp_path / "skill-link"
    link.symlink_to(os.path.dirname(SCRIPTS))
    port = free_port()
    base = "http://127.0.0.1:%d" % port
    log = open(tmp_path / "linked.log", "wb")
    child = subprocess.Popen(["skill-link/scripts/dashboard.sh", str(port)], cwd=tmp_path,
                             stdin=subprocess.DEVNULL, stdout=log, stderr=log)
    try:
        page = fetch(base + "/")
        runs = fetch(base + "/api/runs")
    finally:
        child.send_signal(signal.SIGINT)
        code = child.wait(10)
        log.close()

    with open(os.path.join(SCRIPTS, "dashboard.html"), "rb") as f:
        assert page == f.read()
    assert runs == want
    assert code == 0
