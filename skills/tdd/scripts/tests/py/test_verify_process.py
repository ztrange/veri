"""Cases for veri/verify.py that start a real process: the verify.sh entry point."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("verify.sh run as a real shim over veri/verify.py")
def test_verify_sh_forwards_its_arguments_to_the_module_and_returns_its_exit_code_and_reason(
        tmp_path):
    (tmp_path / "spec.md").write_text("the behavior spec\n")
    claude = tmp_path / "claude"
    claude.write_text("#!/bin/sh\nprintf 'VERDICT: REJECT\\nREASON: the reason.'\n")
    claude.chmod(0o755)
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"}

    done = subprocess.run([str(SCRIPTS / "verify.sh"), "red", "spec.md", "tests/x.test.sh", "case"],
                          cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True)

    assert (done.returncode, done.stdout) == (1, b"the reason.\n")
