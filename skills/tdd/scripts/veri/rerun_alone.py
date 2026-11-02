"""rerun-alone.sh's rerun of the test files a red run names, each alone."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys


def main(argv):
    if not argv:
        sys.stderr.write("usage: rerun-alone.sh <file>...\n")
        return 2
    with open(argv[1]) as red:
        if not re.search(r"[\w./-]+\.test\.\w+", red.read()):
            return 1
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
