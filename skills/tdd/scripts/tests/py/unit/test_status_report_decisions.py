"""Small cases for veri.status --report: Waiting lists the judge's decisions recorded in .tdd/decisions.jsonl since
status-last, for the owner to audit."""
import importlib
import json

import pytest


def report_tree(tmp_path, monkeypatch, fake_processes, decisions):
    """veri.status over a main tree at <tmp_path> with no runs, status-last at 2026-11-02T10:00:00Z and
    .tdd/decisions.jsonl holding <decisions> (text)."""
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    (tmp_path / "home" / "runs" / "acme-widgets").mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "status-last").write_text(json.dumps({"time": "2026-11-02T10:00:00Z", "queue": {}}))
    (tmp_path / ".tdd" / "decisions.jsonl").write_text(decisions)
    fake_processes.answers({}, default=(0, "", ""))
    return status


def decision(question, at):
    return json.dumps({"question": question, "decision": "kept N at 3", "rule": "use plan capacity", "by": "dev",
                       "at": at}) + "\n"


def test_issue_4072_report_waiting_lists_each_decision_at_or_after_status_last_and_none_before_it(
        tmp_path, monkeypatch, run_cli, fake_processes):
    status = report_tree(tmp_path, monkeypatch, fake_processes,
                         decision("before?", "2026-11-02T09:59:59+00:00")
                         + decision("at, in another zone?", "2026-11-02T11:00:00+01:00")
                         + decision("after?", "2026-11-02T10:00:01+00:00")
                         + decision("after, in another zone?", "2026-11-02T06:30:00-04:00"))

    code, out, err = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    waiting = [line for line in lines[lines.index("Waiting") + 1:] if line]
    assert (code, waiting) == (0, ["decided: at, in another zone? → kept N at 3 (rule: use plan capacity)",
                                   "decided: after? → kept N at 3 (rule: use plan capacity)",
                                   "decided: after, in another zone? → kept N at 3 (rule: use plan capacity)"]), err


def test_issue_4072_report_writes_as_status_last_the_time_it_read_the_decision_log_at_not_a_later_one(
        tmp_path, monkeypatch, run_cli, fake_processes):
    status = report_tree(tmp_path, monkeypatch, fake_processes, decision("after?", "2026-11-02T10:30:00+00:00"))
    clock = [1793700000.75]
    monkeypatch.setattr(status.time, "time", lambda: clock[0])
    read = status.decision_log.read

    def read_then_an_hour_passes(main):
        records = read(main)
        clock[0] += 3600
        return records
    monkeypatch.setattr(status.decision_log, "read", read_then_an_hour_passes)

    code, _, err = run_cli(status, ["--report"])

    written = json.loads((tmp_path / ".tdd" / "status-last").read_text())["time"]
    assert (code, written) == (0, "2026-11-03T10:00:00Z"), err


@pytest.mark.parametrize("bad", [
    '{"question": "torn',
    '["a list"]',
    json.dumps({"question": "q", "decision": "d", "by": "dev", "at": "2026-11-02T10:30:00+00:00"}),
    json.dumps({"question": "q", "decision": "d", "rule": "r", "by": "dev", "at": "yesterday"}),
    json.dumps({"question": "q", "decision": "d", "rule": "r", "by": "dev", "at": "2026-11-02T10:30:00"}),
    json.dumps({"question": "q", "decision": 3, "rule": "r", "by": "dev", "at": "2026-11-02T10:30:00+00:00"}),
])
def test_issue_4072_report_exits_2_naming_the_line_when_the_decision_log_holds_one_that_is_not_a_decision_record(
        tmp_path, monkeypatch, run_cli, fake_processes, bad):
    status = report_tree(tmp_path, monkeypatch, fake_processes, decision("fine?", "2026-11-02T10:30:00+00:00") + bad + "\n")
    last = (tmp_path / ".tdd" / "status-last").read_text()

    code, out, err = run_cli(status, ["--report"])

    assert (code, out, err, (tmp_path / ".tdd" / "status-last").read_text()) == (
        2, "", "status.sh: %s:2 is not a decision record\n" % (tmp_path / ".tdd" / "decisions.jsonl"), last)


def test_issue_4072_report_prints_each_decision_on_one_line_its_control_characters_escaped_and_each_field_cut_at_300(
        tmp_path, monkeypatch, run_cli, fake_processes):
    forged = json.dumps({"question": "Forge?\n\nLanded\nv9.9 forged\x1b[31m", "decision": "x" * 301, "rule": "r\tr",
                         "by": "dev", "at": "2026-11-02T10:30:00+00:00"}) + "\n"
    status = report_tree(tmp_path, monkeypatch, fake_processes, forged)

    code, out, err = run_cli(status, ["--report"])

    lines = out.splitlines()
    waiting = [line for line in lines[lines.index("Waiting") + 1:] if line.strip()]
    assert (code, lines.count("Landed"), waiting) == (0, 1, [
        "decided: Forge?\\n\\nLanded\\nv9.9 forged\\x1b[31m → " + "x" * 300 + "… (rule: r\\tr)"]), err


def test_issue_4072_report_waiting_marks_an_owner_record_as_the_owners(tmp_path, monkeypatch, run_cli, fake_processes):
    owner = json.dumps({"question": "Raise N to 4?", "decision": "N=4", "rule": "the owner's override", "by": "owner",
                        "at": "2026-11-02T10:30:00+00:00"}) + "\n"
    status = report_tree(tmp_path, monkeypatch, fake_processes, decision("Raise N to 4?", "2026-11-02T10:20:00+00:00") + owner)

    code, out, err = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    waiting = [line for line in lines[lines.index("Waiting") + 1:] if line]
    assert (code, waiting) == (0, ["decided: Raise N to 4? → kept N at 3 (rule: use plan capacity)",
                                   "owner decided: Raise N to 4? → N=4 (rule: the owner's override)"]), err
