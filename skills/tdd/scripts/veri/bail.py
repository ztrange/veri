"""bail.sh's one-call bail, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

USAGE = "usage: bail.sh <n> <cause> <phase> --note-file <path> [--attempt <k>]"


def main(argv):
    sys.stderr.write("%s\nbail: bad arguments; bail by BAIL.md sub-step 1\n" % USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
