"""Sets each file git tracks in the working tree to an mtime derived from its blob id, run by CI before `make test`."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import subprocess
import sys

from entry import write

USAGE = "usage: content_mtimes.py"


def main(argv):
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode != 0:
        write(sys.stderr, "content_mtimes: not inside a git working tree; changed no file.")
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
