"""supervise.sh's watchdog, run in-process."""
import sys

USAGE = "usage: supervise.sh <name> <cmd> [args...]"


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    if len(argv) < 2:
        print("supervise: missing <cmd>", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
