"""Entry-point contract cases for cloud-setup.sh, the shim over veri/cloud_setup.py."""
import os
import subprocess
import sys

import pytest

from conftest import SCRIPTS
from stub_script import write_stub


@pytest.mark.process("cloud-setup.sh started for real with a python3 reporting 3.11.9 first on PATH and no venv")
def test_its_shim_runs_its_module_on_a_python3_below_the_floor(tmp_path):
    fake, venv = tmp_path / "fake", tmp_path / "venv"
    fake.mkdir()
    venv.mkdir()
    write_stub(fake / "python3",
               'case "$1 $2" in "-c import platform"*) echo 3.11.9; exit 0 ;; esac\n'
               'if [ "$1" = --version ]; then echo "Python 3.11.9"; exit 0; fi\n'
               'exec "%s" "$@"\n' % sys.executable)
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_REMOTE"}
    env.update(PATH=os.pathsep.join((str(fake), os.environ["PATH"])), VERI_VENV=str(venv))

    ran = subprocess.run([str(SCRIPTS / "cloud-setup.sh")], env=env, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert (ran.returncode, ran.stdout, ran.stderr) == (0, "", "")
