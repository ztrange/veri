import datetime
import json
import pathlib
import socket
import subprocess
import sys
import time
import urllib.parse
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


@pytest.mark.process("serve.py")
def test_serve_answers_report_on_loopback_and_on_no_other_local_address(report_repo):
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    def reachable(address):
        try:
            with urllib.request.urlopen(f"http://{address}:{port}/report", timeout=2):
                return True
        except OSError:
            return False

    try:
        deadline = time.monotonic() + 10
        loopback = False
        while time.monotonic() < deadline and proc.poll() is None:
            loopback = reachable("127.0.0.1")
            if loopback:
                break
            time.sleep(0.05)
        reachable_elsewhere = [a for a in _other_local_addresses() if reachable(a)]
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
    running_div = body.split("<div id=running>", 1)[1].split("</div>", 1)[0]
    assert (any("12m" in line for line in running), "3277" in running_div) == (True, False)


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


@pytest.mark.process("serve.py")
def test_page_fetches_fresh_running_data_so_an_appended_journal_line_shows_without_reload(veri_home):
    import re

    def ev(awake, event, **extra):
        return json.dumps({"ts": 1794089519, "awake": awake, "issue": "1515", "event": event, **extra}) + "\n"

    journal = veri_home / "runs" / "1515.jsonl"
    journal.write_text(ev(0, "conductor-start") + ev(10, "verdict", verdict="PASS"))
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"

    def get(url):
        with urllib.request.urlopen(url, timeout=2) as r:
            return r.read().decode()

    try:
        page = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                page = get(base + "/")
                break
            except OSError:
                time.sleep(0.05)

        found = re.search(r"""fetch\(\s*["']([^"']+)["']""", page)
        assert found is not None
        data_url = urllib.parse.urljoin(base + "/", found.group(1))
        before = get(data_url)
        with journal.open("a") as f:
            f.write(ev(20, "verdict", verdict="REJECT"))
        after = get(data_url)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    assert ("PASS 1 REJECT 0" in before, "PASS 1 REJECT 1" in after) == (True, True)


@pytest.mark.process("serve.py and node running the page's script")
def test_open_page_script_rerenders_freshly_fetched_running_data_into_the_page_without_reload(veri_home, tmp_path):
    import re
    import shutil

    node = shutil.which("node")
    if node is None:
        pytest.skip("node is needed to run the page's script")

    def ev(awake, event, **extra):
        return json.dumps({"ts": 1794089519, "awake": awake, "issue": "1616", "event": event, **extra}) + "\n"

    journal = veri_home / "runs" / "1616.jsonl"
    journal.write_text(ev(0, "conductor-start") + ev(10, "verdict", verdict="PASS"))
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        page = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(base + "/", timeout=2) as r:
                    page = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)

        scripts = re.findall(r"<script[^>]*>(.*?)</script>", page, re.S)
        element_ids = re.findall(r"""\bid=["']?([\w-]+)""", page)
        harness = tmp_path / "harness.mjs"
        harness.write_text(
            """
const [base, ids] = [process.argv[2], JSON.parse(process.argv[3])];
const els = {};
globalThis.document = { getElementById: (id) => ids.includes(id) ? (els[id] ??= { innerHTML: "" }) : null };
globalThis.setInterval = (cb) => { cb(); return 1; };
const realFetch = globalThis.fetch;
globalThis.fetch = (u, ...rest) => realFetch(new URL(u, base + "/"), ...rest);
const src = JSON.parse(process.argv[4]);
for (const s of src) (0, eval)(s);
setTimeout(() => { console.log(JSON.stringify(els)); }, 1500);
"""
        )

        def rendered():
            out = subprocess.run(
                [node, str(harness), base, json.dumps(element_ids), json.dumps(scripts)],
                capture_output=True, text=True, timeout=20,
            )
            return " ".join(el["innerHTML"] for el in json.loads(out.stdout).values())

        before = rendered()
        with journal.open("a") as f:
            f.write(ev(20, "verdict", verdict="REJECT"))
        after = rendered()
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    assert ("PASS 1 REJECT 0" in before, "PASS 1 REJECT 1" in after) == (True, True)


def test_page_script_fetches_a_data_only_endpoint_holding_running_lines_and_no_page_markup(veri_home):
    import re

    journal = veri_home / "runs" / "1515.jsonl"
    journal.write_text(
        json.dumps({"ts": 1794089519, "awake": 0, "issue": "1515", "event": "conductor-start"}) + "\n"
        + json.dumps({"ts": 1794089519, "awake": 10, "issue": "1515", "event": "verdict", "verdict": "PASS"}) + "\n"
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"

    def get(url):
        with urllib.request.urlopen(url, timeout=2) as r:
            return r.read().decode()

    try:
        page = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                page = get(base + "/")
                break
            except OSError:
                time.sleep(0.05)

        found = re.search(r"""fetch\(\s*["']([^"']+)["']""", page)
        assert found is not None
        data = get(urllib.parse.urljoin(base + "/", found.group(1)))
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    assert ("1515" in data and "PASS 1 REJECT 0" in data, "<script" in data, "<h2" in data) == (True, False, False)


@pytest.mark.process("serve.py")
def test_report_page_has_one_headed_block_per_open_prd_in_ascending_prd_order(report_repo):
    import re

    def issue(number, title, state="OPEN"):
        return {"number": number, "title": title, "state": state, "updatedAt": "2026-11-01T00:00:00Z"}

    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            issue(50, "PRD 14 later duplicate"),
            issue(40, "PRD 14 dashboard"),
            issue(30, "PRD 9 collector"),
            issue(20, "PRD 3 finished", state="CLOSED"),
            issue(60, "not a prd"),
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        status = content_type = None
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    status, content_type = r.status, r.headers.get_content_type()
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    headings = re.findall(r"PRD \d+ \(#\d+\) — [^<\n]*", body)
    assert (status, content_type, headings) == (
        200,
        "text/html",
        ["PRD 9 (#30) — PRD 9 collector", "PRD 14 (#40) — PRD 14 dashboard"],
    )


@pytest.mark.process("serve.py")
def test_report_page_orders_blocks_by_prd_number_not_by_issue_number(report_repo):
    import re

    def issue(number, title):
        return {"number": number, "title": title, "state": "OPEN", "updatedAt": "2026-11-01T00:00:00Z"}

    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [issue(10, "PRD 14 dashboard"), issue(20, "PRD 9 collector")]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    assert re.findall(r"PRD \d+ \(#\d+\)", body) == ["PRD 9 (#20)", "PRD 14 (#10)"]


@pytest.mark.process("serve.py")
def test_report_page_marks_owed_stale_for_a_prd_with_no_entry_or_a_differing_updated_at(report_repo):
    def issue(number, title, updated):
        return {"number": number, "title": title, "state": "OPEN", "updatedAt": updated}

    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            issue(40, "PRD 14 dashboard", "2026-11-02T10:00:00Z"),
            issue(30, "PRD 9 collector", "2026-11-01T10:00:00Z"),
        ]})
    )
    (report_repo / ".tdd" / "report-owed.json").write_text(
        json.dumps({"014": {"updatedAt": "2026-11-01T10:00:00Z", "answer": {"count": 0, "sections": []}}})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    blocks = body.split("<h2>")[1:]
    assert [(b.split("</h2>")[0][:6], "owed: stale" in b) for b in blocks] == [
        ("PRD 9 ", True),
        ("PRD 14", True),
    ]


@pytest.mark.process("serve.py")
def test_report_page_does_not_mark_owed_stale_when_the_entry_has_the_snapshot_updated_at(report_repo):
    def issue(number, title, updated):
        return {"number": number, "title": title, "state": "OPEN", "updatedAt": updated}

    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            issue(40, "PRD 14 dashboard", "2026-11-02T10:00:00Z"),
            issue(30, "PRD 9 collector", "2026-11-01T10:00:00Z"),
        ]})
    )
    (report_repo / ".tdd" / "report-owed.json").write_text(
        json.dumps({"014": {"updatedAt": "2026-11-02T10:00:00Z", "answer": {"count": 0, "sections": []}}})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    blocks = body.split("<h2>")[1:]
    assert [(b.split("</h2>")[0][:6], "owed: stale" in b) for b in blocks] == [
        ("PRD 9 ", True),
        ("PRD 14", False),
    ]


@pytest.mark.process("serve.py")
def test_report_page_shows_owed_none_when_the_entry_has_the_snapshot_updated_at_and_a_zero_count(report_repo):
    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z"},
        ]})
    )
    (report_repo / ".tdd" / "report-owed.json").write_text(
        json.dumps({"014": {"updatedAt": "2026-11-02T10:00:00Z", "answer": {"count": 0, "sections": []}}})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = body.split("<h2>")[1]
    assert "owed: none" in block


@pytest.mark.process("serve.py")
def test_report_page_does_not_show_owed_none_when_the_current_entry_has_a_non_zero_count(report_repo):
    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z"},
        ]})
    )
    (report_repo / ".tdd" / "report-owed.json").write_text(
        json.dumps({"014": {"updatedAt": "2026-11-02T10:00:00Z", "answer": {"count": 3, "sections": []}}})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = body.split("<h2>")[1]
    assert "owed: none" not in block


@pytest.mark.process("serve.py")
def test_report_page_shows_owed_count_and_sections_when_the_current_entry_has_a_non_zero_count(report_repo):
    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z"},
        ]})
    )
    (report_repo / ".tdd" / "report-owed.json").write_text(
        json.dumps({"014": {"updatedAt": "2026-11-02T10:00:00Z",
                            "answer": {"count": 3, "sections": ["Goals", "Risks"]}}})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = body.split("<h2>")[1]
    assert "owed: 3 (Goals, Risks)" in block


@pytest.mark.process("serve.py")
def test_report_page_shows_solved_count_of_closed_prd_titled_issues_and_those_closed_in_the_last_7_days(report_repo):
    now = datetime.datetime.now(datetime.timezone.utc)

    def stamp(days):
        return (now - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def closed(number, title, days):
        return {"number": number, "title": title, "state": "CLOSED", "updatedAt": stamp(days), "closedAt": stamp(days)}

    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z"},
            closed(41, "PRD 14.1 first slice", 2),
            closed(42, "PRD 14.2 second slice", 20),
            closed(43, "PRD 9 other slice", 1),
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = body.split("<h2>")[1]
    assert "solved: 2 (1 in the last 7 days)" in block


@pytest.mark.process("serve.py")
def test_report_page_counts_in_solved_closed_unnumbered_issues_listed_in_the_prd_links(report_repo):
    now = datetime.datetime.now(datetime.timezone.utc)

    def stamp(days):
        return (now - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def closed(number, title, days):
        return {"number": number, "title": title, "state": "CLOSED", "updatedAt": stamp(days), "closedAt": stamp(days)}

    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "links": [41, 44, 45]},
            closed(41, "PRD 14.1 first slice", 2),
            closed(44, "fix the flaky thing", 1),
            closed(45, "tidy the other thing", 20),
            closed(46, "unrelated fix not listed", 1),
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = body.split("<h2>")[1]
    assert "solved: 3 (2 in the last 7 days)" in block


@pytest.mark.process("serve.py")
def test_report_page_shows_left_line_with_solvable_waiting_and_unheld_counts_of_open_children(report_repo):
    def child(number, labels, blocked_by=()):
        return {"number": number, "title": "PRD 14.%d slice" % number, "state": "OPEN",
                "updatedAt": "2026-11-02T10:00:00Z", "blockedBy": list(blocked_by),
                "labels": [{"name": l} for l in labels]}

    ready = "ready-for-agent:mu"
    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": []},
            child(41, [ready]),
            child(42, [ready], [41]),
            child(43, [ready], [41]),
            child(44, [ready, "taken:mu"]),
            child(45, []),
            child(46, [ready], [99]),
            {"number": 99, "title": "old blocker", "state": "CLOSED", "updatedAt": "2026-11-02T10:00:00Z",
             "closedAt": "2026-11-01T10:00:00Z", "blockedBy": [], "labels": []},
            {"number": 60, "title": "PRD 9.1 other", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": [{"name": ready}]},
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = next(b for b in body.split("<h2>") if b.startswith("PRD 14 "))
    assert "left: solvable now 2, waiting 2 on #41, held by no lane 1" in block


@pytest.mark.process("serve.py")
def test_report_page_left_line_ignores_closed_children_of_the_prd(report_repo):
    def child(number, state, labels, blocked_by=()):
        issue = {"number": number, "title": "PRD 14.%d slice" % number, "state": state,
                 "updatedAt": "2026-11-02T10:00:00Z", "blockedBy": list(blocked_by),
                 "labels": [{"name": l} for l in labels]}
        if state == "CLOSED":
            issue["closedAt"] = "2026-11-01T10:00:00Z"
        return issue

    ready = "ready-for-agent:mu"
    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": []},
            child(41, "OPEN", [ready]),
            child(42, "OPEN", [ready], [41]),
            child(45, "OPEN", []),
            child(51, "CLOSED", [ready]),
            child(52, "CLOSED", [ready], [41]),
            child(53, "CLOSED", []),
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = next(b for b in body.split("<h2>") if b.startswith("PRD 14 "))
    assert "left: solvable now 1, waiting 1 on #41, held by no lane 1" in block


@pytest.mark.process("serve.py")
def test_report_page_shows_no_lane_no_eta_when_no_open_child_has_a_lane(report_repo):
    def child(number, labels):
        return {"number": number, "title": "PRD 14.%d slice" % number, "state": "OPEN",
                "updatedAt": "2026-11-02T10:00:00Z", "blockedBy": [],
                "labels": [{"name": l} for l in labels]}

    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": []},
            child(41, []),
            child(42, ["bug"]),
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = next(b for b in body.split("<h2>") if b.startswith("PRD 14 "))
    assert "ETA: no lane: no ETA" in block


@pytest.mark.process("serve.py")
def test_report_page_omits_no_eta_when_an_open_child_has_a_lane(report_repo):
    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": []},
            {"number": 41, "title": "PRD 14.1 slice", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": [], "lane": "mu"},
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = next(b for b in body.split("<h2>") if b.startswith("PRD 14 "))
    assert "ETA: no lane: no ETA" not in block


@pytest.mark.process("serve.py")
def test_report_page_shows_no_eta_when_only_the_prd_itself_has_a_lane(report_repo):
    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": [], "lane": "mu"},
            {"number": 41, "title": "PRD 14.1 slice", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": []},
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = next(b for b in body.split("<h2>") if b.startswith("PRD 14 "))
    assert "ETA: no lane: no ETA" in block


@pytest.mark.process("serve.py")
def test_report_page_shows_no_eta_when_the_laned_issues_are_closed_or_of_another_prd(report_repo):
    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": []},
            {"number": 41, "title": "PRD 14.1 slice", "state": "CLOSED", "updatedAt": "2026-11-02T10:00:00Z", "closedAt": "2026-11-02T10:00:00+00:00",
             "blockedBy": [], "labels": [], "lane": "mu"},
            {"number": 50, "title": "PRD 15 other", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": []},
            {"number": 51, "title": "PRD 15.1 slice", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": [], "lane": "mu"},
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = next(b for b in body.split("<h2>") if b.startswith("PRD 14 "))
    assert "ETA: no lane: no ETA" in block


@pytest.mark.process("serve.py")
def test_report_page_shows_no_rate_yet_when_fewer_than_three_lane_issues_closed_in_7_days(report_repo):
    now = datetime.datetime.now(datetime.timezone.utc)
    recent = (now - datetime.timedelta(days=1)).isoformat()

    def closed(number):
        return {"number": number, "title": "other work %d" % number, "state": "CLOSED",
                "updatedAt": recent, "closedAt": recent, "blockedBy": [], "labels": [], "lane": "mu"}

    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": []},
            {"number": 41, "title": "PRD 14.1 slice", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": [], "lane": "mu"},
            closed(60),
            closed(61),
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = next(b for b in body.split("<h2>") if b.startswith("PRD 14 "))
    assert "ETA: no rate yet" in block


@pytest.mark.process("serve.py")
def test_report_page_shows_no_rate_yet_when_closed_issues_outside_the_lanes_or_older_than_7_days_make_up_the_three(report_repo):
    now = datetime.datetime.now(datetime.timezone.utc)
    recent = (now - datetime.timedelta(days=1)).isoformat()
    old = (now - datetime.timedelta(days=10)).isoformat()

    def closed(number, lane, closed_at):
        return {"number": number, "title": "other work %d" % number, "state": "CLOSED",
                "updatedAt": closed_at, "closedAt": closed_at, "blockedBy": [], "labels": [], "lane": lane}

    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": []},
            {"number": 41, "title": "PRD 14.1 slice", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": [], "lane": "mu"},
            closed(60, "mu", recent),
            closed(61, "mu", recent),
            closed(62, "other", recent),
            closed(63, "other", recent),
            closed(64, "mu", old),
            closed(65, "mu", old),
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = next(b for b in body.split("<h2>") if b.startswith("PRD 14 "))
    assert "ETA: no rate yet" in block


@pytest.mark.process("serve.py")
def test_report_page_shows_the_eta_range_from_the_lane_quartile_wall_seconds(report_repo):
    now = datetime.datetime.now(datetime.timezone.utc)
    recent = (now - datetime.timedelta(days=1)).isoformat()

    def closed(number, wall):
        return {"number": number, "title": "other work %d" % number, "state": "CLOSED",
                "updatedAt": recent, "closedAt": recent, "blockedBy": [], "labels": [],
                "lane": "mu", "wallSeconds": wall}

    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": []},
            {"number": 41, "title": "PRD 14.1 slice", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": [], "lane": "mu"},
            {"number": 42, "title": "PRD 14.2 slice", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": [], "lane": "mu"},
            closed(60, 10000),
            closed(61, 20000),
            closed(62, 40000),
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = next(b for b in body.split("<h2>") if b.startswith("PRD 14 "))
    assert "ETA: 0.23 to 0.93 days" in block


@pytest.mark.process("serve.py")
def test_report_page_shows_the_eta_range_with_the_longest_open_blocked_by_chain_when_longer_than_the_child_count(report_repo):
    now = datetime.datetime.now(datetime.timezone.utc)
    recent = (now - datetime.timedelta(days=1)).isoformat()

    def closed(number, wall):
        return {"number": number, "title": "other work %d" % number, "state": "CLOSED",
                "updatedAt": recent, "closedAt": recent, "blockedBy": [], "labels": [],
                "lane": "mu", "wallSeconds": wall}

    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": []},
            {"number": 41, "title": "PRD 14.1 slice", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [42], "labels": [], "lane": "mu"},
            {"number": 42, "title": "PRD 14.2 slice", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [50], "labels": [], "lane": "mu"},
            {"number": 50, "title": "unrelated blocker", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": []},
            closed(60, 10000),
            closed(61, 20000),
            closed(62, 40000),
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = next(b for b in body.split("<h2>") if b.startswith("PRD 14 "))
    assert "ETA: 0.23 to 1.39 days" in block


@pytest.mark.process("serve.py")
def test_report_page_eta_uses_lower_and_upper_quartile_wall_seconds_not_min_and_max_with_five_closed_issues(report_repo):
    now = datetime.datetime.now(datetime.timezone.utc)
    recent = (now - datetime.timedelta(days=1)).isoformat()

    def closed(number, wall):
        return {"number": number, "title": "other work %d" % number, "state": "CLOSED",
                "updatedAt": recent, "closedAt": recent, "blockedBy": [], "labels": [],
                "lane": "mu", "wallSeconds": wall}

    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": []},
            {"number": 41, "title": "PRD 14.1 slice", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": [], "lane": "mu"},
            {"number": 42, "title": "PRD 14.2 slice", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": [], "lane": "mu"},
            closed(60, 1000),
            closed(61, 10000),
            closed(62, 20000),
            closed(63, 40000),
            closed(64, 400000),
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = next(b for b in body.split("<h2>") if b.startswith("PRD 14 "))
    assert "ETA: 0.23 to 0.93 days" in block


@pytest.mark.process("serve.py")
def test_report_page_eta_uses_fastest_lanes_fast_rate_and_slowest_lanes_slow_rate_and_counts_only_open_blockers(report_repo):
    now = datetime.datetime.now(datetime.timezone.utc)
    recent = (now - datetime.timedelta(days=1)).isoformat()

    def closed(number, wall, lane):
        return {"number": number, "title": "other work %d" % number, "state": "CLOSED",
                "updatedAt": recent, "closedAt": recent, "blockedBy": [], "labels": [],
                "lane": lane, "wallSeconds": wall}

    def child(number, lane, blocked_by):
        return {"number": number, "title": "PRD 14.%d slice" % number, "state": "OPEN",
                "updatedAt": "2026-11-02T10:00:00Z", "blockedBy": blocked_by, "labels": [], "lane": lane}

    (report_repo / ".tdd" / "report-cache.json").write_text(
        json.dumps({"issues": [
            {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z",
             "blockedBy": [], "labels": []},
            child(41, "la", [60]),
            child(42, "lb", []),
            child(43, "lc", []),
            child(44, "ld", []),
            closed(60, 8640, "la"),
            closed(61, 17280, "lb"),
            closed(62, 43200, "lc"),
            closed(63, 86400, "ld"),
        ]})
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    block = next(b for b in body.split("<h2>") if b.startswith("PRD 14 "))
    assert "ETA: 0.40 to 4.00 days" in block


@pytest.mark.process("serve.py")
def test_report_page_for_a_stale_owed_leaves_report_owed_json_byte_identical_and_creates_no_file(report_repo):
    tdd = report_repo / ".tdd"
    (tdd / "report-cache.json").write_text(json.dumps({"issues": [
        {"number": 40, "title": "PRD 14 dashboard", "state": "OPEN", "updatedAt": "2026-11-02T10:00:00Z"},
    ]}))
    owed = tdd / "report-owed.json"
    owed.write_text(json.dumps({"014": {"updatedAt": "2026-11-01T10:00:00Z", "answer": {"count": 2, "sections": ["Goals"]}}}))
    before_bytes = owed.read_bytes()
    before_names = sorted(p.name for p in tdd.iterdir())
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(report_repo), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/report", timeout=2) as r:
                    body = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    assert "owed: stale" in body
    assert owed.read_bytes() == before_bytes
    assert sorted(p.name for p in tdd.iterdir()) == before_names


@pytest.mark.process("serve.py")
def test_page_landed_section_lists_each_merged_tag_in_status_report_shape(veri_home, monkeypatch):
    import os
    import re

    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={**os.environ, "TZ": "America/Chicago"},
    )
    try:
        page = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    page = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    section = re.search(r"<h2>Landed</h2>(.*?)(?:<h2|<script|\Z)", page, re.S)
    lines = [l for l in (section.group(1).splitlines() if section else []) if l.strip()]
    expected = (
        "v0.1136  2026-11-07 19:13  A red-phase leaf's overwrite of the step's uncommitted "
        "production code is restored and recorded, and the develop prompt forbids it"
    )
    assert [l for l in lines if l.startswith("<p>")] == []
    assert [re.sub(r"<[^>]+>", "", l).strip() for l in lines if "v0.1136" in l] == [expected]


@pytest.mark.process("serve.py")
def test_page_waiting_section_lists_each_bail_as_run_and_cause_in_journal_order(veri_home):
    import re

    (veri_home / "runs" / "1200.jsonl").write_text(
        json.dumps({"ts": 1794089519, "awake": 0, "issue": "1200", "event": "bail"}) + "\n"
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        page = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    page = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    section = re.search(r"<h2>Waiting</h2>(.*?)(?:<h2|<script|\Z)", page, re.S)
    lines = [l for l in (section.group(1).splitlines() if section else []) if l.strip()]
    text = [re.sub(r"<[^>]+>", "", l).strip() for l in lines]
    assert [l for l in lines if l.startswith("<p>")] == []
    assert [t for t in text if t.startswith("#3277")] == ["#3277 untestable-criterion", "#3277 no-verdict"]
    assert len([t for t in text if t.startswith("#1200")]) == 1


@pytest.mark.process("serve.py")
def test_page_waiting_section_lists_a_done_pr_not_followed_by_merged_as_ready_to_merge(veri_home):
    import re

    pr = "https://github.com/ztrange/veri/pull/4000"
    (veri_home / "runs" / "4000.jsonl").write_text(
        json.dumps({"ts": 1794089519, "awake": 0, "issue": "4000", "event": "conductor-start"}) + "\n"
        + json.dumps({"ts": 1794089600, "awake": 50, "issue": "4000", "event": "done", "pr": pr}) + "\n"
    )
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        page = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    page = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    section = re.search(r"<h2>Waiting</h2>(.*?)(?:<h2|<script|\Z)", page, re.S)
    lines = [l for l in (section.group(1).splitlines() if section else []) if l.strip()]
    text = [re.sub(r"<[^>]+>", "", l).strip() for l in lines]
    assert [t for t in text if "ready to merge" in t] == [f"#4000 PR {pr} ready to merge"]


@pytest.mark.process("serve.py")
def test_page_waiting_section_lists_ready_to_merge_when_the_only_merged_event_precedes_the_last_done_pr(veri_home):
    import re

    first = "https://github.com/ztrange/veri/pull/4100"
    last = "https://github.com/ztrange/veri/pull/4101"
    events = [
        {"ts": 1794089519, "awake": 0, "issue": "4100", "event": "conductor-start"},
        {"ts": 1794089600, "awake": 50, "issue": "4100", "event": "done", "pr": first},
        {"ts": 1794089700, "awake": 60, "issue": "4100", "event": "merged", "pr": first},
        {"ts": 1794089800, "awake": 70, "issue": "4100", "event": "done", "pr": last},
    ]
    (veri_home / "runs" / "4100.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        page = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    page = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    section = re.search(r"<h2>Waiting</h2>(.*?)(?:<h2|<script|\Z)", page, re.S)
    lines = [l for l in (section.group(1).splitlines() if section else []) if l.strip()]
    text = [re.sub(r"<[^>]+>", "", l).strip() for l in lines]
    assert [t for t in text if "ready to merge" in t] == [f"#4100 PR {last} ready to merge"]


@pytest.mark.process("serve.py")
def test_page_landed_section_reads_none_when_no_journal_holds_a_merged_event_with_a_tag(veri_home):
    import re

    (veri_home / "runs" / "3277.jsonl").unlink()
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        page = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    page = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    section = re.search(r"<h2>Landed</h2>(.*?)(?:<h2|<script|\Z)", page, re.S)
    lines = [l for l in (section.group(1).splitlines() if section else []) if l.strip()]
    assert [re.sub(r"<[^>]+>", "", l).strip() for l in lines] == ["none"]



@pytest.mark.process("serve.py")
def test_page_waiting_section_reads_none_when_no_journal_holds_a_bail_or_unmerged_done_pr(veri_home):
    import re

    (veri_home / "runs" / "3277.jsonl").unlink()
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE), "--repo", str(veri_home), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        page = ""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    page = r.read().decode()
                break
            except OSError:
                time.sleep(0.05)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    section = re.search(r"<h2>Waiting</h2>(.*?)(?:<h2|<script|\Z)", page, re.S)
    lines = [l for l in (section.group(1).splitlines() if section else []) if l.strip()]
    assert [re.sub(r"<[^>]+>", "", l).strip() for l in lines] == ["none"]
