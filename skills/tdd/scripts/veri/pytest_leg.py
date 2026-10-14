"""The pytest leg's launcher: refuses an interpreter below the Python floor, then runs pytest."""
# Usage:   pytest_leg.py
# Exit:    2 the interpreter is below the floor in lib/venv-python.sh
import os
import platform
import re
import sys

import tunables


def main(argv):
    lib = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib", "venv-python.sh")
    with open(lib) as f:
        floor = re.search("^VENV_FLOOR=(.*)$", f.read(), re.M).group(1)
    version = tunables.read("VERI_PYTHON_VERSION") or platform.python_version()
    numbers = [int(part) for part in re.findall("[0-9]+", version)[:2]]
    if numbers < [int(part) for part in floor.split(".")[:2]]:
        sys.stderr.write("veri needs Python %s or newer for the suites under skills/tdd/scripts/tests/py/; %s is version %s.\n"
                         % (floor, sys.executable, version))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
