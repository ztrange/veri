"""discarded-exit.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import subprocess
import sys

import entry


USAGE = "usage: discarded-exit.sh"


def _git(*args):
    """Runs git with args in the current directory; returns (code, stdout)."""
    done = subprocess.run(["git", *args], capture_output=True, text=True)
    return done.returncode, done.stdout


def main(argv):
    refused = entry.no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    code, _diff = _git("diff", "HEAD")
    if code != 0:
        return entry.refuse(usage=USAGE)
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
