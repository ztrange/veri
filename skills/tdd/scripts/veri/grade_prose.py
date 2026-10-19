"""grade-prose.sh's entry point, run in-process."""
import sys

USAGE = "usage: grade-prose.sh <requirements-file> <unit>"


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
