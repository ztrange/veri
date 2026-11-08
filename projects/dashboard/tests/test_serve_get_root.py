import pathlib
import socket
import subprocess
import sys
import time
import urllib.request

SERVE = pathlib.Path(__file__).resolve().parents[1] / "serve.py"


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_serve_answers_get_root_with_200_html(veri_home):
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        status = content_type = None
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    status, content_type = r.status, r.headers.get_content_type()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    assert (status, content_type) == (200, "text/html")

