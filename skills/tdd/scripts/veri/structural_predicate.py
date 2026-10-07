"""structural-predicate.sh's answer, read off a predicate leaf's report on stdin."""
import sys

USAGE = "usage: structural-predicate.sh <record>"


def main(argv):
    if not argv or not argv[0]:
        sys.stderr.write(USAGE + "\n")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
