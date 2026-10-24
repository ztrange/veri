"""merge-lock.sh's verbs, run in-process."""
import os
import subprocess
import sys

VERBS = ("take", "release", "holder")


def main(argv):
    if not argv or argv[0] not in VERBS:
        print("usage: merge-lock.sh take|release|holder", file=sys.stderr)
        return 2
    if argv[0] == "holder":
        common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                stdout=subprocess.PIPE, text=True, check=True).stdout.strip()
        if not os.path.isdir(os.path.join(os.path.dirname(common), ".tdd", "merge.lock")):
            return 3
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
