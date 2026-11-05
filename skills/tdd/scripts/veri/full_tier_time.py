"""full-tier-time.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

USAGE = "usage: full-tier-time.sh [--record <seconds>] <command>"


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    return 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
