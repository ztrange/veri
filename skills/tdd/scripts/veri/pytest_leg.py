"""The pytest leg's launcher: refuses an interpreter below the Python floor, then runs pytest."""
# Usage:   pytest_leg.py
# Exit:    2 the interpreter is below the floor in lib/venv-python.sh, or cannot import pytest or pytest_timeout
import importlib.util
import platform
import re
import sys

import launch_floor
import tunables


def main(argv):
    floor = launch_floor.python_floor()
    version = tunables.read("VERI_PYTHON_VERSION") or platform.python_version()
    numbers = [int(part) for part in re.findall("[0-9]+", version)[:2]]
    if numbers < [int(part) for part in floor.split(".")[:2]]:
        sys.stderr.write("veri needs Python %s or newer for the suites under skills/tdd/scripts/tests/py/; %s is version %s.\n"
                         % (floor, sys.executable, version))
        return 2
    importable = tunables.read("VERI_PYTEST_IMPORTABLE") or ("1" if importlib.util.find_spec("pytest") else "0")
    if importable != "1":
        sys.stderr.write("veri needs pytest for the suites under skills/tdd/scripts/tests/py/; %s cannot import pytest. "
                         "Install it with `make install-dev`.\n" % sys.executable)
        return 2
    timeout_importable = tunables.read("VERI_PYTEST_TIMEOUT_IMPORTABLE") or ("1" if importlib.util.find_spec("pytest_timeout") else "0")
    if timeout_importable != "1":
        sys.stderr.write("veri needs pytest-timeout for the suites under skills/tdd/scripts/tests/py/; %s cannot import pytest_timeout. "
                         "Install it with `make install-dev`.\n" % sys.executable)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
