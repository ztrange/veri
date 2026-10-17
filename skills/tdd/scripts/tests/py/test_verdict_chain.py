"""The verdict launch SKILL.md prescribes, run through every real script between the launch and the exit code."""
import json
import os
import subprocess

import pytest

from conftest import SCRIPTS

STUB = """#!/bin/sh
printf '%s\\n' "$VERDICT_RESULT" | awk '{printf "{\\"type\\":\\"result\\",\\"subtype\\":\\"success\\",\\"is_error\\":false,\\"result\\":\\"%s\\"}\\n", $0}'
"""


def launch_verdict(tmp_path, result):
    tmp_path.mkdir()
    work = tmp_path / "work"
    work.mkdir()
    (work / ".tdd").mkdir()
    (work / "spec.md").write_text("## Acceptance criteria\n\n- [ ] it works\n")
    (work / "probe.test.sh").write_text("true\n")
    stub = tmp_path / "claude"
    stub.write_text(STUB)
    stub.chmod(0o755)
    home = tmp_path / "home"
    home.mkdir()
    env = {name: value for name, value in os.environ.items() if not name.startswith("VERI_")}
    env.update(S=str(SCRIPTS), CLAUDE_BIN=str(stub), HOME=str(home), VERDICT_RESULT=result,
               VERI_STUCK_RETRIES="0", VERI_NO_VERDICT_RETRIES="0", VERI_HEARTBEAT="30", VERI_TIMEOUT="60", VERI_POLL="0.2")
    launch = ('$S/detach-leaf.sh $S/supervise.sh verdict-red $S/run-verdict.sh red spec.md probe.test.sh probe-target'
              ' > .tdd/verify-red.reason && $S/wait-leaf.sh verdict-red 60')
    done = subprocess.run(["bash", "-c", launch], cwd=work, env=env, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
    return done.returncode, (work / ".tdd" / "verify-red.reason").read_text()


@pytest.mark.process("detach-leaf.sh, supervise.sh, run-verdict.sh, verify.sh and wait-leaf.sh chained as SKILL.md launches a verdict, over a stub claude")
def test_1463_wait_leaf_returns_the_verdict_the_stub_verifier_gave_through_the_real_chain(tmp_path):
    passed = launch_verdict(tmp_path / "pass", "VERDICT: PASS\\nthe test pins the behaviour")
    rejected = launch_verdict(tmp_path / "reject", "VERDICT: REJECT\\nthe test is trivial")
    assert (passed[0], "the test pins the behaviour" in passed[1]) == (0, True)
    assert (rejected[0], "the test is trivial" in rejected[1]) == (1, True)
