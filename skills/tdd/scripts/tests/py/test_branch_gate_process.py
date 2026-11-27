"""Cases for branch-gate.sh (PRD 027.7, #4030) that start a real process: the shim's usage, and a local full run made
by the real branch-suite.sh, event.sh, detach-command.sh start and wait, and full-tier-time.sh."""
import importlib
import os
import subprocess

import pytest

from conftest import SCRIPTS

LEDGER = "# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n- [ ] the full suite is green ⟦full-suite⟧ ⟦criterion 2⟧\n"


@pytest.mark.process("branch-gate.sh's /bin/sh shim exec'd on the interpreter with no argument")
def test_4030_the_shim_with_no_argument_prints_its_usage_and_exits_2(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "branch-gate.sh")], cwd=tmp_path, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=60)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: branch-gate.sh <n>\n")


@pytest.mark.process("branch-suite.sh, event.sh, detach-command.sh start and wait and full-tier-time.sh, all real")
@pytest.mark.parametrize("status", [0, 1])
def test_4030_a_local_full_run_is_started_detached_waited_on_and_timed_or_stops_on_its_red(
        tmp_path, monkeypatch, run_cli, status):
    fused = importlib.import_module("veri.fused")
    branch_gate = importlib.import_module("veri.branch_gate")
    real = fused.run_script
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=wt, capture_output=True, check=True, timeout=60)
    (wt / ".tdd" / "issue-12.md").write_text(LEDGER)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    full = "sh -c 'echo suite-said-%d; exit %d'" % (status, status)

    def answer(name, *args, **kw):
        if os.path.basename(name) == "detect-test-command.sh":
            return 0, full + "\n", ""
        return real(name, *args, **kw)

    monkeypatch.setattr(fused, "run_script", answer)
    code, out, err = run_cli(branch_gate, ["12"], cwd=str(tmp_path),
                             env={"VERI_BRANCH_SUITE": "", "VERI_CI_ON_PR": "", "VERI_POLL": "0.05"})

    assert code == status, out + err
    assert (wt / ".tdd" / "issue-12.md").read_text() == LEDGER
    stages = [line for line in (wt / ".tdd" / "events.jsonl").read_text().splitlines() if "full-suite" in line]
    assert ['"stage-start"' in stages[0], '"status": "%d"' % status in stages[1].replace('"status":"', '"status": "')] \
        == [True, True]
    if status == 0:
        assert out.splitlines()[-1] == "branch_suite=local"
        assert subprocess.run([str(SCRIPTS / "full-tier-time.sh"), full], cwd=wt, capture_output=True, text=True,
                              timeout=60).returncode == 0
    else:
        assert out.splitlines()[-1] == "stopped at opening detach-command.sh wait branch-full-12 exit 1"
