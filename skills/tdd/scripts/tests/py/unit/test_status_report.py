"""Small cases for veri.status --report."""
import importlib


def test_2750_report_exits_0_and_prints_landed_running_queue_waiting_in_that_order(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))

    code, out, _ = run_cli(status, ["--report"])

    headings = [line.strip() for line in out.splitlines()
                if line.strip() in ("Landed", "Running", "Queue", "Waiting")]
    assert (code, headings) == (0, ["Landed", "Running", "Queue", "Waiting"])


def test_2750_report_without_snapshot_says_so_under_queue_and_still_prints_the_other_sections(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    queue = lines.index("Queue")
    after_queue = [line for line in lines[queue + 1:] if line][:1]
    headings = [line for line in lines if line in ("Landed", "Running", "Queue", "Waiting")]
    assert (code, headings, "no snapshot" in " ".join(after_queue).lower()) == (
        0, ["Landed", "Running", "Queue", "Waiting"], True)


def test_2750_report_empty_landed_running_and_waiting_keep_their_heading_and_say_none(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    first_after = {h: ([x for x in lines[lines.index(h) + 1:] if x] or [""])[0]
                   for h in ("Landed", "Running", "Waiting")}
    assert (code, first_after) == (0, {"Landed": "none", "Running": "none", "Waiting": "none"})
