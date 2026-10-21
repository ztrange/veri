"""Cases for orchestrate.sh that start a real process."""
import os
import subprocess
import sys

import pytest

from conftest import SCRIPTS


@pytest.mark.process("orchestrate.sh run for real, refusing a bad budget before any listing is asked")
def test_orchestrate_sh_forwards_its_arguments_to_the_module_and_the_modules_exit_code_as_its_own(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "orchestrate.sh")], cwd=tmp_path, capture_output=True, text=True,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin",
                              "VERI_CONDUCTOR_CTX_BUDGET": "120k", "PYTHONDONTWRITEBYTECODE": "1"})

    assert (ran.returncode, ran.stdout, ran.stderr) == (
        2, "", "orchestrate.sh: VERI_CONDUCTOR_CTX_BUDGET must be a whole number of tokens: 120k\n")
