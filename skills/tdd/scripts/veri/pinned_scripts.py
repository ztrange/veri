"""pinned-scripts.sh: the directory holding a run's pinned scripts."""
import os
import sys


def main(argv):
    if not argv:
        print("usage: pinned-scripts.sh <n>", file=sys.stderr)
        return 2
    here = os.path.join(os.getcwd(), ".tdd", "pinned-scripts")
    if not os.path.isdir(here):
        here = os.path.join(os.getcwd(), ".tdd", "wt", argv[0], ".tdd", "pinned-scripts")
    print(here)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
