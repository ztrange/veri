"""skill-edit-guard.sh's entry point, run in-process."""
import sys

USAGE = "usage: skill-edit-guard.sh <unit-file> <base-sha>"


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
