"""Small cases for veri.status --report: Waiting lists the judge's decisions recorded in .tdd/decisions.jsonl since
status-last, for the owner to audit."""
import importlib
import json


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


def test_issue_4072_report_waiting_lists_each_decision_after_status_last_and_none_at_or_before_it(
        tmp_path, monkeypatch, run_cli, fake_processes):
    status = report_tree(tmp_path, monkeypatch, fake_processes,
                         decision("before?", "2026-11-02T09:59:59+00:00")
                         + decision("at, in another zone?", "2026-11-02T11:00:00+01:00")
                         + decision("after?", "2026-11-02T10:00:01+00:00")
                         + decision("after, in another zone?", "2026-11-02T06:30:00-04:00"))

    code, out, err = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    waiting = [line for line in lines[lines.index("Waiting") + 1:] if line]
    assert (code, waiting) == (0, ["decided: after? → kept N at 3 (rule: use plan capacity)",
                                   "decided: after, in another zone? → kept N at 3 (rule: use plan capacity)"]), err
