"""suite-reported.sh's computation, run in-process."""
import sys

USAGE = "usage: suite-reported.sh <leaf-name>"


def main(argv):
    if len(argv) != 1 or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    print(f"suite-reported.sh: {argv[0]} left no SUITE: line", file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
