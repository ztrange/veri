"""role-growth.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

USAGE = "usage: role-growth.sh <coord|dev> [--lane <lane>]\n"


def main(argv):
    sys.stderr.write(USAGE)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
