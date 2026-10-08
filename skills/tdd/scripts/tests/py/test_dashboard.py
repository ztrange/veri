"""In-process cases for veri/dashboard.py, the module dashboard.sh is a shim over."""
import http.server
import importlib
import io
import json
import os
import signal
import subprocess
import sys

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


def test_main_serves_on_loopback_8765_or_the_first_argument_with_the_files_beside_the_scripts(
        tmp_path, monkeypatch, dashboard):
    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        return subprocess.CompletedProcess(args, 0, b'{"runs": ["from status.sh"]}', b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/", "/api/runs"])

    dashboard.main([])
    dashboard.main([""])
    dashboard.main(["4242", "9999"])

    assert [address for address, _ in served] == [
        ("127.0.0.1", 8765), ("127.0.0.1", 8765), ("127.0.0.1", 4242)]
    page, runs = served[0][1]
    with open(os.path.join(SCRIPTS, "dashboard.html"), "rb") as f:
        assert body(page) == f.read()
    assert body(runs) == b'{"runs": ["from status.sh"]}'
    assert [os.path.join(SCRIPTS, "status.sh"), "--json"] in calls


def status_code(answer):
    return answer.split(b"\r\n", 1)[0].split()[1]


def test_main_binds_loopback_on_8765_or_the_port_argument_answers_gets_and_returns_0_on_keyboard_interrupt(
        tmp_path, monkeypatch, dashboard):
    monkeypatch.setattr(subprocess, "run", lambda args, **kwargs: subprocess.CompletedProcess(
        args, 0, b'{"runs": []}', b""))
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/", "/api/runs"])

    codes = [dashboard.main([]), dashboard.main(["4243"])]

    assert [address for address, _ in served] == [("127.0.0.1", 8765), ("127.0.0.1", 4243)]
    assert [status_code(answer) for answer in served[0][1]] == [b"200", b"200"]
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


def test_get_api_runs_through_main_answers_exactly_the_stdout_status_sh_json_printed(
        tmp_path, monkeypatch, dashboard):
    printed = b'{"runs": [{"issue": 7, "state": "running"}]}\n\xe2\x9f\x82 \t trailing  \n'

    def fake_run(args, **kwargs):
        if list(args) == [os.path.join(SCRIPTS, "status.sh"), "--json"]:
            return subprocess.CompletedProcess(args, 3, printed, b"status.sh: diagnostic\n")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/runs"])

    dashboard.main([])

    (runs,) = served[0][1]
    assert status_code(runs) == b"200"
    assert body(runs) == printed


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def test_get_api_metrics_recomputes_a_live_run_and_quotes_the_committed_report_of_one_ended_by_done(
        tmp_path, monkeypatch, dashboard):
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
    recomputed = "# metrics.sh 31, recomputed in its run\n"

    def fake_run(args, cwd=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        if list(args) == [os.path.join(SCRIPTS, "metrics.sh"), "31"] and cwd == live:
            return subprocess.CompletedProcess(args, 0, recomputed.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/metrics"])

    dashboard.main([])

    (metrics,) = served[0][1]
    issues = json.loads(body(metrics))["issues"]
    assert issues["31"] == recomputed
    assert issues["32"] == committed


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
        if list(args) == [os.path.join(SCRIPTS, "metrics.sh"), "33"]:
            return subprocess.CompletedProcess(args, 0, b"# metrics.sh 33, recomputed\n", b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
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
        tmp_path, monkeypatch, dashboard):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "35")
    write(os.path.join(run, ".tdd", "issue-35.md"), "# Plan for #35\n\n- [ ] a lamp glows\n")
    write(os.path.join(run, ".tdd", "events.jsonl"),
          '{"ts": 1, "issue": "35", "event": "step-start"}\n'
          '{"ts": 2, "issue": "35", "event": "launch", "name": "develop-red"}\n'
          '{"ts": 3, "issue": "35", "event": "stop", "mode": "at-leaf", "at": "planned"}\n')
    recomputed = "# metrics.sh 35, recomputed in its run\n"

    def fake_run(args, cwd=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        if list(args) == [os.path.join(SCRIPTS, "metrics.sh"), "35"] and cwd == run:
            return subprocess.CompletedProcess(args, 0, recomputed.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/metrics"])

    dashboard.main([])

    (metrics,) = served[0][1]
    assert json.loads(body(metrics))["issues"]["35"] == recomputed


def test_get_api_metrics_keys_issues_by_the_run_directory_7_alone_and_runs_metrics_sh_once_in_it(
        tmp_path, monkeypatch, dashboard):
    run = os.path.join(str(tmp_path), ".tdd", "wt", "7")
    write(os.path.join(run, ".tdd", "issue-7.md"),
          "# Plan for #7 — lamps glow\n\n- [x] a lamp exists\n- [ ] a lamp glows\n")
    for other in ("3", "5"):
        write(os.path.join(run, ".tdd", "issue-%s.md" % other),
              "# Plan for #%s — an earlier run's committed plan\n\n- [x] a lamp is wired\n" % other)
    write(os.path.join(run, ".tdd", "events.jsonl"),
          '{"ts": 1, "issue": "7", "event": "step-start"}\n'
          '{"ts": 2, "issue": "7", "event": "launch", "name": "develop-red"}\n')
    metrics_calls = []

    def fake_run(args, cwd=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        if list(args)[:1] == [os.path.join(SCRIPTS, "metrics.sh")]:
            metrics_calls.append((list(args), cwd))
            return subprocess.CompletedProcess(args, 0, b"a stub report\n", b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/metrics"])

    dashboard.main([])

    (metrics,) = served[0][1]
    assert sorted(json.loads(body(metrics))["issues"]) == ["7"]
    assert metrics_calls == [([os.path.join(SCRIPTS, "metrics.sh"), "7"], run)]


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


def test_get_api_chatter_hands_the_renderer_run_54s_verify_green_out_the_leaf_its_newest_launch_names(
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
    rendered = "[verifier] Reading the diff against the spec.\n[verifier] VERDICT: PASS\n"
    fed = []

    def fake_run(args, cwd=None, input=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        if list(args) == [os.path.join(SCRIPTS, "render-leaf-log.sh")]:
            fed.append(input)
            return subprocess.CompletedProcess(args, 0, rendered.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/chatter?issue=54"])

    dashboard.main([])

    (chatter,) = served[0][1]
    assert fed == [green_log.encode()]
    assert json.loads(body(chatter)) == {"chatter": rendered}


def test_get_api_chatter_hands_the_renderer_run_59s_verify_red_log_when_no_verify_red_out_exists(
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
    rendered = "[verifier] Reading the new case against the spec.\n[verifier] VERDICT: PASS\n"
    fed = []

    def fake_run(args, cwd=None, input=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        if list(args) == [os.path.join(SCRIPTS, "render-leaf-log.sh")]:
            fed.append(input)
            return subprocess.CompletedProcess(args, 0, rendered.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/chatter?issue=59"])

    dashboard.main([])

    (chatter,) = served[0][1]
    assert fed == [verify_log.encode()]
    assert json.loads(body(chatter)) == {"chatter": rendered}


def test_get_api_chatter_hands_the_renderer_only_the_four_stream_json_lines_of_run_61s_develop_green_log(
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
    rendered = "[developer] Making the flicker case pass.\n[developer] $ make test\n"
    fed = []

    def fake_run(args, cwd=None, input=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        if list(args) == [os.path.join(SCRIPTS, "render-leaf-log.sh")]:
            fed.append(input)
            return subprocess.CompletedProcess(args, 0, rendered.encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/chatter?issue=61"])

    dashboard.main([])

    (chatter,) = served[0][1]
    assert fed == [record_lines.encode()]
    assert json.loads(body(chatter)) == {"chatter": rendered}


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
    fed = []

    def fake_run(args, cwd=None, input=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        if list(args) == [os.path.join(SCRIPTS, "render-leaf-log.sh")]:
            fed.append(input)
            return subprocess.CompletedProcess(args, 0, b"[developer] another leaf's chatter\n", b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    served = fake_server(monkeypatch, ["/api/chatter?issue=63", "/api/chatter?issue=65"])

    dashboard.main([])

    (noleaf_chatter, nolog_chatter) = served[0][1]
    assert json.loads(body(noleaf_chatter)) == {"chatter": ""}
    assert json.loads(body(nolog_chatter)) == {"chatter": ""}
    assert fed == []


def test_get_api_chatter_for_run_55_twice_hands_the_renderer_develop_red_out_then_develop_green_out_after_its_launch(
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
    fed = []

    def fake_run(args, cwd=None, input=None, **kwargs):
        if list(args) == ["git", "worktree", "list", "--porcelain"]:
            out = "worktree %s\nHEAD abc\nbranch refs/heads/main\n" % tmp_path
            return subprocess.CompletedProcess(args, 0, out.encode(), b"")
        if list(args) == [os.path.join(SCRIPTS, "render-leaf-log.sh")]:
            fed.append(input)
            return subprocess.CompletedProcess(args, 0, b"rendered %d\n" % len(fed), b"")
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
    assert fed == [red_log.encode(), green_log.encode()]
    assert json.loads(body(first)) == {"chatter": "rendered 1\n"}
    assert json.loads(body(second)) == {"chatter": "rendered 2\n"}
