"""cloud-setup.sh's computations, run in-process."""
# hazard: runs on a python3 below VENV_FLOOR, so nothing here may need more than Python 3.9.
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry

USAGE = "usage: cloud-setup.sh"


def main(argv):
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
