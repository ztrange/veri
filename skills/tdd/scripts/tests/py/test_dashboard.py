"""In-process cases for veri/dashboard.py, the module dashboard.sh is a shim over."""
import http.server
import importlib
import io
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
