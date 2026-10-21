"""Cases for supervise.sh that start a real process."""
import os
import subprocess
import sys

import pytest

from conftest import SCRIPTS


@pytest.mark.process("supervise.sh run for real, supervising a real leaf that echoes its arguments and exits 1")
def test_supervise_sh_forwards_its_arguments_to_the_leaf_and_the_leafs_exit_code_as_its_own(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "supervise.sh"), "develop-red", "sh", "-c", 'echo "$1"; exit 1', "sh", "forwarded"],
                         cwd=tmp_path, capture_output=True, text=True,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_STUCK_RETRIES": "0",
                              "VERI_POLL": "0.05", "PYTHONDONTWRITEBYTECODE": "1"})

    assert (ran.returncode, ran.stdout) == (1, "forwarded\n"), ran.stderr
