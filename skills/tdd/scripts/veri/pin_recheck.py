"""pin-recheck.sh's re-run of the recorded pin mutations a range touches."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys


def main(argv):
    if not argv:
        sys.stderr.write("usage: pin-recheck.sh <base-sha>\n")
        return 2
    return 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
