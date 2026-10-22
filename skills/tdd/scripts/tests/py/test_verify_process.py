"""Cases for veri/verify.py that start a real process: the verify.sh entry point."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("verify.sh run as a real shim over veri/verify.py, a real supervise.sh and run-leaf.sh"
                     " around a stub claude that answers VERDICT: PASS")
def test_verify_sh_green_rejects_a_pass_on_a_replaces_case_step_naming_each_case_its_suite_still_holds_1507(
        tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / "tests" / "x.test.sh").write_text("test\n")
    (tmp_path / "tests" / "demo.test.sh").write_text('verdict "kept case" 0\nverdict "stale second" 0\n')
    claude = tmp_path / "claude-pass"
    claude.write_text("#!/bin/sh\nprintf 'VERDICT: PASS\\nREASON: the named cases are gone.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), "--step", "the replacement takes over: replaces 'stale first', 'stale second'"
         " in tests/demo.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧", "--fast-cmd", "make unit", "green", "spec.md",
         "tests/x.test.sh"],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True)

    assert (done.returncode, b"stale second" in done.stdout, b"stale first" in done.stdout) == (1, True, False)


@pytest.mark.process("verify.sh run as a real shim over veri/verify.py and a real supervise.sh around a stub claude,"
                     " from a subdirectory of a throwaway git repo")
def test_verify_sh_run_from_a_subdirectory_writes_its_prompt_and_run_state_under_the_repo_root_1895(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    sub = tmp_path / "skills"
    sub.mkdir()
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    (tmp_path / "x_test.py").write_text("def test_x():\n    pass\n")
    claude = tmp_path / "claude-pass"
    claude.write_text("#!/bin/sh\nprintf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", "PYTHONDONTWRITEBYTECODE": "1"}

    done = subprocess.run(
        [str(SCRIPTS / "verify.sh"), "--fast-cmd", "make unit", "green", "../spec.md", "../x_test.py", "x_test.py::test_x"],
        cwd=sub, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert ((tmp_path / ".tdd" / "verify-green.prompt").exists(), (sub / ".tdd").exists()) == (True, False), done.stderr
