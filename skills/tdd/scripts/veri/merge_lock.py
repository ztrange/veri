"""merge-lock.sh's verbs, run in-process."""
import sys

VERBS = ("take", "release", "holder")


def main(argv):
    if not argv or argv[0] not in VERBS:
        print("usage: merge-lock.sh take|release|holder", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
