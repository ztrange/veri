"""Small cases for veri.status --recover: the recovery report."""
import importlib
import os
import subprocess


HEADINGS = ["Runs", "Bailed", "PRs", "Merge lock", "State", "Pending decisions", "Pending messages"]


def test_3224_recover_with_nothing_taken_prints_the_seven_headings_in_order_with_none_under_each_empty_one_and_free_for_the_lock(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    expected = []
    for heading in HEADINGS:
        expected += [heading, "free" if heading == "Merge lock" else "none"]
    assert (code, lines) == (0, expected)


def test_3224_recover_lists_under_runs_a_taken_run_held_by_a_live_conductor_with_its_issue_title_and_pid(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    state = tmp_path / ".tdd" / "wt" / "3300" / ".tdd"
    state.mkdir(parents=True)
    (state / "issue-3300.md").write_text("# Plan for #3300 — Teach the widget to sing\n\n- [ ] one\n")
    (state / "conductor.pid").write_text("%d\n" % os.getpid())

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    runs = lines[lines.index("Runs") + 1:lines.index("Bailed")]
    assert code == 0 and len(runs) == 1, runs
    assert all(word in runs[0] for word in ("3300", "Teach the widget to sing", str(os.getpid()))), runs


def test_3224_recover_runs_line_carries_the_issue_title_without_the_ledger_heading_prefix(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    state = tmp_path / ".tdd" / "wt" / "3301" / ".tdd"
    state.mkdir(parents=True)
    (state / "issue-3301.md").write_text("# Plan for #3301 — Teach the widget to sing\n\n- [ ] one\n")
    (state / "conductor.pid").write_text("%d\n" % os.getpid())

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    runs = lines[lines.index("Runs") + 1:lines.index("Bailed")]
    assert code == 0 and len(runs) == 1, runs
    assert "Plan for" not in runs[0] and "—" not in runs[0] and "Teach the widget to sing" in runs[0], runs
