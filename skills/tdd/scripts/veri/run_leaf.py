"""run-leaf.sh's logic, run in-process."""
import sys

USAGE = "usage: run-leaf.sh <prompt-file|-> [claude args...]"


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
