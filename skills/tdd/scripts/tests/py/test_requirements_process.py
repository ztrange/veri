"""requirements.sh's entry point: the shim runs veri/requirements.py and passes its exit code and output through.
The module's logic is tested in-process, in tests/py/unit/test_requirements.py."""
import subprocess

from conftest import SCRIPTS

REQUIREMENTS = SCRIPTS / "requirements.sh"


def run(*argv):
    ran = subprocess.run([str(REQUIREMENTS), *argv], stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return ran.returncode, ran.stdout, ran.stderr
