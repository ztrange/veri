"""leaf-launchable.sh's launch probe, run in-process."""
# hazard: runs on the python3 it may refuse, so nothing here may need more than Python 3.9.
import os
import subprocess
import sys


def main(argv):
    leaf_bin = os.environ.get("CLAUDE_BIN")
    if subprocess.call([leaf_bin, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
