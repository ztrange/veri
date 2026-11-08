"""diff-leaf-deviation.sh's check, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import subprocess
import sys

import event

USAGE = "usage: diff-leaf-deviation.sh <leaf> <step-base-sha> <ledger>"


class GitFailure(Exception):
    pass


def _git(*args):
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise GitFailure("diff-leaf-deviation.sh: git " + " ".join(args) + " failed: " + exc.stderr.strip()) from None


def main(argv):
    try:
        return _main(argv)
    except GitFailure as exc:
        print(exc, file=sys.stderr)
        return 2


def _main(argv):
    if len(argv) == 3:
        leaf, base, ledger = argv
        count = int(_git("rev-list", "--count", base + "..HEAD"))
        touched = _git("diff", "--name-only", base + "..HEAD", "--", ledger)
        if count < 2 and not touched:
            return 3
        head = _git("rev-parse", "HEAD")
        return event.append(".", {}, "diff-leaf-deviation",
                            ["leaf=" + leaf, "base=" + base, "head=" + head, "commits=" + str(count)])
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
