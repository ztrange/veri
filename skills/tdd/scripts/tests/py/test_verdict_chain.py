"""The verdict launch SKILL.md prescribes, run through every real script between the launch and the exit code."""
import hashlib
import importlib
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
    (work / ".tdd" / "issue-2206.md").write_text("# Plan for #2206\n\n- [ ] first step\n")
    identity = {"GIT_AUTHOR_NAME": "veri", "GIT_AUTHOR_EMAIL": "veri@example.test", "GIT_COMMITTER_NAME": "veri",
                "GIT_COMMITTER_EMAIL": "veri@example.test", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    git = {**os.environ, **identity}
    (work / ".gitignore").write_text(".tdd/\n")
    subprocess.run(["git", "-C", str(work), "init", "-q", "-b", "main"], check=True, env=git)
    subprocess.run(["git", "-C", str(work), "add", "-A"], check=True, env=git)
    subprocess.run(["git", "-C", str(work), "commit", "-q", "-m", "initial"], check=True, env=git)
    here = os.getcwd()
    os.chdir(work)
    try:
        tests_frozen = importlib.import_module("veri.tests_frozen")
        tests_frozen._write_pass_marker("first step", tests_frozen._work_tree_hash())
    finally:
        os.chdir(here)
    stub = tmp_path / "claude"
    stub.write_text(STUB)
    stub.chmod(0o755)
    home = tmp_path / "home"
    home.mkdir()
    env = {name: value for name, value in os.environ.items() if not name.startswith("VERI_")}
    env.update(S=str(SCRIPTS), CLAUDE_BIN=str(stub), HOME=str(home), VERDICT_RESULT=result,
               VERI_ISSUE="2206", VERI_STEP="1", VERI_STUCK_RETRIES="0", VERI_NO_VERDICT_RETRIES="0", VERI_HEARTBEAT="30", VERI_TIMEOUT="60", VERI_POLL="0.2")
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
