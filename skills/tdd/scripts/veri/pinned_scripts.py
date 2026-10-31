"""pinned-scripts.sh: the directory holding a run's pinned scripts."""
import sys


def main(argv):
    if not argv:
        print("usage: pinned-scripts.sh <n>", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
