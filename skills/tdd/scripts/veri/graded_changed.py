"""graded-changed.sh's entry point, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

USAGE = "usage: graded-changed.sh <base-sha>"


def main(argv):
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
