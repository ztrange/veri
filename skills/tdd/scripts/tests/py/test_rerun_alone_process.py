"""rerun-alone.sh's entry point: the shim runs veri/rerun_alone.py and passes its exit code and output through.
The module's logic is tested in-process, in tests/py/unit/test_rerun_alone.py."""
import subprocess

from conftest import SCRIPTS

RERUN = str(SCRIPTS / "rerun-alone.sh")


def run(*argv, cwd=None):
    ran = subprocess.run([RERUN, *argv], cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return ran.returncode, ran.stdout, ran.stderr
