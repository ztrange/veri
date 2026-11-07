"""restart-conductor.sh's watch, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

USAGE = "usage: restart-conductor.sh <n>"


def main(argv):
    if not argv or not (argv[0].isascii() and argv[0].isdigit() and int(argv[0]) >= 1):
        print(USAGE, file=sys.stderr)
        return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
