"""Process case for veri.status --report: Landed lists only the tags cut since .tdd/status-last."""
import importlib
import json
import os
import subprocess

import pytest


@pytest.mark.process("git started for real over a scratch repository holding annotated tags cut at set dates")
def test_2750_report_landed_leaves_out_a_tag_cut_before_the_time_in_status_last(tmp_path, run_cli):
    status = importlib.import_module("veri.status")

    def git(*words, date=None):
        env = {**os.environ, **({"GIT_COMMITTER_DATE": date} if date else {})}
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words],
                       cwd=tmp_path, check=True, capture_output=True, env=env)
    git("init", "-q")
    git("commit", "-q", "--allow-empty", "-m", "first")
    git("tag", "-a", "v0.1", "-m", "Old capability", date="2026-01-01T00:00:00Z")
    git("tag", "-a", "v0.2", "-m", "New capability", date="2026-09-01T00:00:00Z")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "status-last").write_text(json.dumps({"time": "2026-06-01T00:00:00Z"}))

    code, out, _ = run_cli(status, ["--report"], cwd=str(tmp_path))

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    landed = lines[lines.index("Landed") + 1:lines.index("Running")]
    assert (code, sorted(l.split()[0] for l in landed)) == (0, ["v0.2"]), landed
