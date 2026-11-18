"""bail.sh's one-call bail, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

USAGE = "usage: bail.sh <n> <cause> <phase> --note-file <path> [--attempt <k>]"


def _bad_arguments():
    sys.stderr.write("%s\nbail: bad arguments; bail by BAIL.md sub-step 1\n" % USAGE)
    return 2


def _valid(argv):
    if len(argv) not in (5, 7) or not argv[0].isdigit() or argv[3] != "--note-file":
        return False
    return len(argv) == 5 or (argv[5] == "--attempt" and argv[6].isdigit())


def main(argv):
    if not _valid(argv):
        return _bad_arguments()
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    classified = subprocess.run([os.path.join(here, "classify-bail.sh"), argv[1]], capture_output=True, text=True)
    if classified.returncode != 0:
        sys.stderr.write("bail: unknown cause %s; bail by BAIL.md sub-step 1\n" % argv[1])
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
