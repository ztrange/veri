"""Cases for run-done.sh (PRD 027.12, #4034) that start a real process: the shim's usage, and the done comment posted
and a stop request cleared by the real stop-requested.sh and comment.sh, against a stub gh."""
import importlib
import os
import subprocess

import pytest

from conftest import SCRIPTS
from stub_script import write_stub

URL = "https://github.com/o/r/pull/42"


@pytest.mark.process("run-done.sh's /bin/sh shim exec'd on the interpreter with no argument")
def test_4034_the_shim_with_no_argument_prints_its_usage_and_exits_2(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "run-done.sh")], cwd=tmp_path, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=60)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: run-done.sh <n>\n")


@pytest.mark.process("git, event.sh, stop-requested.sh and comment.sh, all real, against a stub gh")
def test_4034_the_done_comment_is_posted_and_the_stop_request_cleared_for_real(tmp_path, run_cli):
    run_done = importlib.import_module("veri.run_done")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=wt, capture_output=True, check=True, timeout=60)
    (wt / ".git" / "info" / "exclude").write_text(".tdd/\n")
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-metrics.md").write_text("## 📊 Metrics\n\nnothing much\n")
    (wt / ".tdd" / "stop").write_text("at-ledger\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    calls = tmp_path / "calls"
    calls.write_text("")
    write_stub(bin_dir / "gh", 'echo "$*" >> "$CALLS"\nfor a; do case $a in body=*) printf "%s" "${a#body=}" >> "$POSTED" ;; '
                               'esac; done\necho https://github.com/o/r/issues/12#issuecomment-1\n')
    env = {"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"], "CALLS": str(calls),
           "POSTED": str(tmp_path / "posted"), "VERI_GH_DRIVER": "auto"}
    subprocess.run([str(SCRIPTS / "event.sh"), "done", "pr=" + URL], cwd=wt, check=True, capture_output=True,
                   timeout=60, env=dict(os.environ, VERI_ISSUE="12", VERI_ACTOR="conductor"))

    code, out, err = run_cli(run_done, ["12"], cwd=str(tmp_path), env=env)

    assert code == 0, out + err + calls.read_text()
    assert out.splitlines()[-2:] == ["stop_requested=0", "cleared=1"]
    assert "### ✅ Done — " + URL in (tmp_path / "posted").read_text()
    assert not (wt / ".tdd" / "stop").exists()
    assert not [line for line in calls.read_text().splitlines() if "merge" in line]
