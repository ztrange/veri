"""unreplaced-cases.sh's answer: the bash cases a replaces-case step names that have no pytest replacement."""
import sys

USAGE = "usage: unreplaced-cases.sh"


def main(argv):
    sys.stderr.write(USAGE + "\n")
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
