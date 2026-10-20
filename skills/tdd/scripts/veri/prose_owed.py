"""prose-owed.sh's entry point, run in-process."""
import sys

USAGE = "usage: prose-owed.sh <repo-root>"


def main(argv):
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
