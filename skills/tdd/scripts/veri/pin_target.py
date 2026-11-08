"""pin-target.sh, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

USAGE = "usage: pin-target.sh <step-red-report> [<red-missing-report>…]"


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    for line in open(argv[0], encoding="utf-8").read().splitlines():
        if line.startswith("TARGET_TEST:"):
            print(line.split(":", 1)[1].strip())
            return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
