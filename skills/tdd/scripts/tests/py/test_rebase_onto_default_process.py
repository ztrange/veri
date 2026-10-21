"""Cases for rebase-onto-default.sh that start a real process."""
import os
import subprocess
import sys

import pytest

from conftest import SCRIPTS


@pytest.mark.process("rebase-onto-default.sh run for real, in a directory that is no git repository")
def test_rebase_onto_default_sh_forwards_the_modules_exit_code_as_its_own(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "rebase-onto-default.sh")], cwd=tmp_path, capture_output=True, text=True,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin",
                              "PYTHONDONTWRITEBYTECODE": "1", "GIT_CEILING_DIRECTORIES": str(tmp_path.parent)})

    assert (ran.returncode, ran.stdout) == (2, "")
    assert ran.stderr.endswith("rebase-onto-default: refs/remotes/origin/HEAD is not set — no default branch to rebase onto\n")
