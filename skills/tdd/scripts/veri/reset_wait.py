"""reset-wait.sh's waits, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

USAGE = "usage: reset-wait.sh marker|recovered|idle <coord|dev> [--lane <lane>] [<seconds>]"


def main(argv):
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
