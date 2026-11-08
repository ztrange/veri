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



def _other_local_addresses():
    addresses = ["127.0.0.2"]
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("192.0.2.1", 9))
            addresses.append(s.getsockname()[0])
        except OSError:
            pass
    return [a for a in addresses if a != "127.0.0.1"]


def _reachable(address, port):
    try:
        with urllib.request.urlopen(f"http://{address}:{port}/", timeout=2):
            return True
    except OSError:
        return False


def test_serve_listens_on_loopback_only(veri_home):
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + 10
        loopback = False
        while time.monotonic() < deadline and proc.poll() is None:
            loopback = _reachable("127.0.0.1", port)
            if loopback:
                break
            time.sleep(0.05)
        reachable_elsewhere = [a for a in _other_local_addresses() if _reachable(a, port)]
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    assert (loopback, reachable_elsewhere) == (True, [])


def _listening_ports(pid):
    out = subprocess.run(
        ["lsof", "-a", "-p", str(pid), "-iTCP", "-sTCP:LISTEN", "-Fn"],
        capture_output=True,
        text=True,
    ).stdout
    return [int(line.rsplit(":", 1)[1]) for line in out.splitlines() if line.startswith("n")]


def test_serve_without_port_still_serves_the_page(veri_home):
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        status = None
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None and status is None:
            for port in _listening_ports(proc.pid):
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                        status = r.status
                except OSError:
                    pass
            time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    assert status == 200
