"""refactor-overflow.sh's logic, run in-process."""
import os
import re
import sys

USAGE = "refactor-overflow: usage: refactor-overflow.sh <n> <owed-file> <reached>"
NUMBER = re.compile(r"[0-9]+")


def main(argv):
    n, owed, reached, skipped = (list(argv[:4]) + [""] * 4)[:4]
    if not NUMBER.fullmatch(n) or not owed or not NUMBER.fullmatch(reached):
        print(USAGE, file=sys.stderr)
        return 2
    if skipped and not os.path.isfile(skipped):
        print(f"refactor-overflow: no such skipped file: {skipped}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
