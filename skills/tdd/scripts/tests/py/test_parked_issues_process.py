"""parked-issues.sh's entry point: the shim runs veri/parked_issues.py and passes its exit code and output through.
The module's logic is tested in-process, in tests/py/unit/test_parked_issues.py."""
import subprocess

from conftest import SCRIPTS
