"""Cases for pin-fast-tier.sh that start a real process: the entry point, and the cases that also start git or a leaf.
The module's other logic is tested in-process, in tests/py/unit/test_pin_fast_tier.py."""
import os
import subprocess

import pytest

from conftest import SCRIPTS

CHECK = str(SCRIPTS / "pin-fast-tier.sh")


def stub(path, body):
    path.write_text("#!/bin/sh\n" + body)
    path.chmod(0o755)
    return str(path)


@pytest.mark.process("pin-fast-tier.sh and git run for real, from a subdirectory of a throwaway repo")
def test_pin_fast_tier_run_from_a_subdirectory_writes_the_reason_under_the_repo_root_1895(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    sub = tmp_path / "skills"
    sub.mkdir()
    fast = stub(tmp_path / "fast-red", "echo 'FAIL - a case'\nexit 1\n")

    ran = subprocess.run([CHECK, fast], cwd=sub, capture_output=True, text=True)

    assert ran.returncode == 1, ran.stderr
    assert ((tmp_path / ".tdd" / "verify-pin.reason").exists(), (sub / ".tdd").exists()) == (True, False)


@pytest.mark.process("pin-fast-tier.sh, build-develop-prompt.sh and run-leaf.sh chained, with a stub claude")
def test_a_reason_file_at_the_bound_builds_a_revise_prompt_run_leaf_launches_under_arg_max_2882(tmp_path):
    (tmp_path / ".tdd").mkdir()
    arg_max = os.sysconf("SC_ARG_MAX")
    fast = stub(tmp_path / "fast-noisy",
                f"yes '    at passing-noise-frame (src/component.tsx:1:10) padding padding' | head -c {2 * arg_max}\n"
                "echo\necho ' FAIL  src/widget.test.ts > widget > renders'\nexit 1\n")
    claude = stub(tmp_path / "claude", "echo '{\"type\":\"result\",\"result\":\"ok\"}'\n: > \"$STUB_RAN\"\n")
    spec = tmp_path / "spec.md"
    spec.write_text("## Problem\nA bug.\n")
    prompt_file = tmp_path / "revise.prompt"
    env = {**os.environ, "CLAUDE_BIN": claude, "STUB_RAN": str(tmp_path / "ran"), "VERI_ISSUE": "3123"}

    subprocess.run([CHECK, fast], cwd=tmp_path, capture_output=True)
    built = subprocess.run([str(SCRIPTS / "build-develop-prompt.sh"), "revise", "red", str(spec), "step", "make unit",
                            str(tmp_path / ".tdd" / "verify-pin.reason")],
                           cwd=tmp_path, capture_output=True, env=env)
    prompt_file.write_bytes(built.stdout)
    launched = subprocess.run([str(SCRIPTS / "run-leaf.sh"), str(prompt_file)], cwd=tmp_path,
                              capture_output=True, env=env)

    assert built.returncode == 0, built.stderr
    assert prompt_file.stat().st_size < arg_max
    assert (launched.returncode, (tmp_path / "ran").exists()) == (0, True), launched.stderr
