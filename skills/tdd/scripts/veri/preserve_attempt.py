"""preserve-attempt.sh's computation, run in-process."""
import sys

USAGE = "usage: preserve-attempt.sh <issue> <step> <phase> <attempt> [<mark>]"


def main(argv):
    if len(argv) < 4 or not all(argv[:4]):
        print(USAGE, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
