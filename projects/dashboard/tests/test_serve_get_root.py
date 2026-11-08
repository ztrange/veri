import json
import pathlib
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

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


def test_page_names_a_run_without_an_ending_event_with_its_awake_minutes(veri_home):
    first = {"ts": 1794089519, "awake": 1000, "issue": "4242", "event": "conductor-start"}
    last = {"ts": 1794090239, "awake": 1720, "issue": "4242", "event": "test-run"}
    (veri_home / "runs" / "4242.jsonl").write_text(
        "".join(json.dumps(e) + "\n" for e in (first, last))
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    running = [line for line in body.splitlines() if "4242" in line]
    assert (any("12m" in line for line in running), "3277" in body) == (True, False)


def test_page_lists_running_runs_in_sorted_order_skipping_blank_lines_and_empty_journals(veri_home):
    def line(issue, awake, event):
        return json.dumps({"ts": 1794089519, "awake": awake, "issue": issue, "event": event}) + "\n"

    runs = veri_home / "runs"
    (runs / "3333.jsonl").write_text(line("3333", 0, "conductor-start") + line("3333", 600, "test-run"))
    (runs / "2222.jsonl").write_text("")
    (runs / "1111.jsonl").write_text(
        line("1111", 0, "conductor-start") + "\n" + line("1111", 300, "test-run")
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    assert [l for l in body.splitlines() if l.startswith("<p>")] == [
        "<p>1111 5m</p>",
        "<p>3333 10m</p>",
    ]


def test_page_leaves_out_runs_whose_journal_has_a_bail_or_merged_ending_event(veri_home):
    def line(issue, awake, event):
        return json.dumps({"ts": 1794089519, "awake": awake, "issue": issue, "event": event}) + "\n"

    runs = veri_home / "runs"
    (runs / "5551.jsonl").write_text(line("5551", 0, "conductor-start") + line("5551", 600, "bail"))
    (runs / "5552.jsonl").write_text(line("5552", 0, "conductor-start") + line("5552", 600, "merged"))
    (runs / "5553.jsonl").write_text(line("5553", 0, "conductor-start") + line("5553", 600, "test-run"))
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    shown = [l for l in body.splitlines() if l.startswith("<p>555")]
    assert shown == ["<p>5553 10m</p>"]


def test_page_leaves_out_runs_whose_journal_has_a_done_ending_event(veri_home):
    def line(issue, awake, event):
        return json.dumps({"ts": 1794089519, "awake": awake, "issue": issue, "event": event}) + "\n"

    runs = veri_home / "runs"
    (runs / "6661.jsonl").write_text(line("6661", 0, "conductor-start") + line("6661", 600, "done"))
    (runs / "6662.jsonl").write_text(
        line("6662", 0, "conductor-start")
        + json.dumps({"ts": 1794089519, "awake": 300, "issue": "6662"}) + "\n"
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    shown = [l for l in body.splitlines() if l.startswith("<p>666")]
    assert shown == ["<p>6662 5m</p>"]


@pytest.mark.process("serve.py")
def test_page_shows_a_running_runs_steps_done_of_the_last_plans_steps(veri_home):
    def ev(awake, event, **extra):
        return json.dumps({"ts": 1794089519, "awake": awake, "issue": "7771", "event": event, **extra}) + "\n"

    (veri_home / "runs" / "7771.jsonl").write_text(
        ev(0, "conductor-start")
        + ev(10, "plan", steps=3)
        + ev(20, "step-done")
        + ev(30, "plan", steps=5)
        + ev(40, "step-done")
        + ev(50, "step-done")
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    entry = [l for l in body.splitlines() if "7771" in l]
    assert any("3/5" in l for l in entry)


@pytest.mark.process("serve.py")
def test_page_shows_a_running_runs_current_phase_and_its_attempt_count(veri_home):
    def ev(awake, event, **extra):
        return json.dumps({"ts": 1794089519, "awake": awake, "issue": "8881", "event": event, **extra}) + "\n"

    (veri_home / "runs" / "8881.jsonl").write_text(
        ev(0, "conductor-start")
        + ev(10, "launch", phase="red")
        + ev(20, "launch", phase="green")
        + ev(30, "launch", phase="red")
        + ev(40, "launch", phase="green")
        + ev(50, "launch", phase="green")
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    entry = [l for l in body.splitlines() if "8881" in l]
    assert any("green attempt 3" in l for l in entry)


@pytest.mark.process("serve.py")
def test_page_shows_a_running_runs_pass_and_reject_verdict_counts(veri_home):
    def ev(awake, event, **extra):
        return json.dumps({"ts": 1794089519, "awake": awake, "issue": "9991", "event": event, **extra}) + "\n"

    (veri_home / "runs" / "9991.jsonl").write_text(
        ev(0, "conductor-start")
        + ev(10, "verdict", verdict="PASS")
        + ev(20, "verdict", verdict="REJECT")
        + ev(30, "verdict", verdict="PASS")
        + ev(40, "verdict", verdict="PASS")
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    entry = [l for l in body.splitlines() if "9991" in l]
    assert any("PASS 3 REJECT 1" in l for l in entry)


@pytest.mark.process("serve.py")
def test_page_shows_a_running_runs_cost_in_dollars_summed_from_usage_events(veri_home):
    def ev(awake, event, **extra):
        return json.dumps({"ts": 1794089519, "awake": awake, "issue": "1212", "event": event, **extra}) + "\n"

    (veri_home / "runs" / "1212.jsonl").write_text(
        ev(0, "conductor-start")
        + ev(10, "usage", total_cost_usd="0.126")
        + ev(20, "usage", total_cost_usd="0.2")
        + ev(30, "usage", total_cost_usd="0.4")
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    entry = [l for l in body.splitlines() if "1212" in l]
    assert any("| total | $0.73" in l for l in entry)


@pytest.mark.process("serve.py")
def test_page_shows_a_running_runs_model_split_per_role(veri_home):
    def ev(awake, event, **extra):
        return json.dumps({"ts": 1794089519, "awake": awake, "issue": "1313", "event": event, **extra}) + "\n"

    (veri_home / "runs" / "1313.jsonl").write_text(
        ev(0, "conductor-start")
        + ev(10, "launch", phase="red", actor="developer", name="develop-red", model="sonnet")
        + ev(20, "launch", phase="red", actor="verifier", name="verify-red", model="haiku")
        + ev(30, "launch", phase="red", actor="developer", name="revise-red", model="opus")
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    entry = [l for l in body.splitlines() if "1313" in l]
    assert any("developer sonnet verifier haiku revise opus" in l for l in entry)


@pytest.mark.process("serve.py")
def test_page_shows_only_the_roles_with_a_model_in_a_running_runs_model_split(veri_home):
    def ev(awake, event, **extra):
        return json.dumps({"ts": 1794089519, "awake": awake, "issue": "1414", "event": event, **extra}) + "\n"

    (veri_home / "runs" / "1414.jsonl").write_text(
        ev(0, "conductor-start")
        + ev(10, "launch", phase="red", actor="developer", name="develop-red", model="sonnet")
        + ev(20, "launch", phase="red", actor="verifier", name="verify-red")
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    entry = [l for l in body.splitlines() if "1414" in l]
    assert any("developer sonnet" in l for l in entry)
    assert not any("verifier" in l or "revise" in l or "None" in l for l in entry)
