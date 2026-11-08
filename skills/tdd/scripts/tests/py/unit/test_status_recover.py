"""Small cases for veri.status --recover: the recovery report."""
import importlib
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
