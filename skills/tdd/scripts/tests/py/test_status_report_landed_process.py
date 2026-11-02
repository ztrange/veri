"""Process case for veri.status --report: Landed lists the local version tags."""
import importlib
import subprocess

import pytest


@pytest.mark.process("git started for real over a scratch repository holding annotated vN.M tags")
def test_2750_report_landed_lists_one_line_per_local_tag_with_its_message(tmp_path, run_cli):
    status = importlib.import_module("veri.status")

    def git(*words):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words],
                       cwd=tmp_path, check=True, capture_output=True)
    git("init", "-q")
    git("commit", "-q", "--allow-empty", "-m", "first")
    git("tag", "-a", "v0.9", "-m", "Queue counts open issues")
    git("tag", "-a", "v0.10", "-m", "Landed lists local tags")

    code, out, _ = run_cli(status, ["--report"], cwd=str(tmp_path))

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    landed = lines[lines.index("Landed") + 1:lines.index("Running")]
    assert (code, [("v0.10" in l, "Landed lists local tags" in l) for l in landed[:1]],
            [("v0.9" in l, "Queue counts open issues" in l) for l in landed[1:2]]) == \
        (0, [(True, True)], [(True, True)]), landed
