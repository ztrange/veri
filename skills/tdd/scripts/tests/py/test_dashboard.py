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

SCRIPTS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for path in (SCRIPTS, os.path.join(SCRIPTS, "veri")):
    if path not in sys.path:
        sys.path.insert(0, path)


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
