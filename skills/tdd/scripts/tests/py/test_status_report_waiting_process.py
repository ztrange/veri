"""Process case for veri.status --report: Waiting drops a PR whose (#N) subject is on main."""
import importlib
import json
import subprocess

import pytest


@pytest.mark.process("git started for real over a scratch repository whose main holds a (#N) subject")
def test_3250_report_waiting_drops_a_pr_whose_issue_subject_is_on_real_main(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*words):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words],
                       cwd=repo, check=True, capture_output=True)
    git("init", "-q", "-b", "main")
    git("remote", "add", "origin", "git@github.com:acme/widgets.git")
    git("commit", "-q", "--allow-empty", "-m", "fix: Waiting drops merged PRs (#2751)")
    git("checkout", "-q", "-b", "side")
    git("commit", "-q", "--allow-empty", "-m", "fix: not yet on main (#2750)")
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)

    def journal(number, pr):
        events = [{"ts": 1793600000, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"},
                  {"ts": 1793600050, "awake": 50, "event": "done", "pr": pr}]
        (runs / ("%d.jsonl" % number)).write_text("".join(json.dumps(e) + "\n" for e in events))
    journal(2750, 99)
    journal(2751, 98)

    code, out, err = run_cli(status, ["--report"], cwd=str(repo))

    lines = [line.strip() for line in out.splitlines()]
    waiting = lines[lines.index("Waiting") + 1:]
    assert (code, [l.split()[:3] for l in waiting if l]) == (0, [["#2750", "PR", "99"]]), (waiting, err)
