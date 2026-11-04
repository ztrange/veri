"""suite-flakes.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys


def main(argv):
    if not argv:
        sys.stderr.write("usage: suite-flakes.sh <run-dir> [<run-dir>...]\n")
        return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
