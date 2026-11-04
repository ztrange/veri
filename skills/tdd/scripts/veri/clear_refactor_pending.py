"""clear-refactor-pending.sh's clear, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import ledger
from git import git

USAGE = "usage: clear-refactor-pending.sh <ledger-file> <matcher>"


def complain(path, message):
    print(f"clear-refactor-pending.sh: {path}: {message}", file=sys.stderr)


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        text = ledger.read_ledger(argv[0])
    except OSError as error:
        complain(argv[0], error.strerror)
        return 2
    cleared, new = ledger.ledger_clear_pending(text, argv[1] if len(argv) > 1 else "")
    if not cleared:
        return 3
    receipt = os.path.join(os.path.dirname(argv[0]), "pin-recheck-ok")
    if not os.path.exists(receipt):
        complain(argv[0], "no pin-recheck receipt: run pin-recheck.sh first")
        return 2
    with open(receipt) as handle:
        sha = handle.read().strip()
    changed = git("diff", "--name-only", sha, "HEAD", capture_output=True, text=True,
                  cwd=os.path.dirname(argv[0]) or None).stdout.split()
    if any(not path.startswith(".tdd/") for path in changed):
        complain(argv[0], "a path outside .tdd/ changed since the pin-recheck receipt: run pin-recheck.sh again")
        return 2
    left = ledger.rewrite_ledger(argv[0], new)
    if left is None:
        return 0
    if left:
        complain(argv[0], f"left {left} behind")
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
