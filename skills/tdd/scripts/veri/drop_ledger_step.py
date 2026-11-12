"""drop-ledger-step.sh's removal, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import ledger
from git import git
import pid_file
import reorder_ledger_steps

USAGE = "usage: drop-ledger-step.sh <ledger-file> <step-substring>"


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    live = pid_file.live_conductor(os.path.dirname(os.path.dirname(os.path.abspath(argv[0]))))
    if live:
        print(f"conductor {live} is live; refusing to drop a ledger step", file=sys.stderr)
        return 1
    lines = ledger.read_ledger(argv[0]).split("\n")
    index = reorder_ledger_steps._open_match(lines, argv[1], "cannot drop a ticked step")
    if index is None:
        return 1
    del lines[index]
    ledger.replace_ledger(argv[0], "\n".join(lines).encode(errors="surrogateescape"))
    directory = os.path.dirname(os.path.abspath(argv[0]))
    name = os.path.basename(argv[0])
    if git("rev-parse", "--is-inside-work-tree", cwd=directory, capture_output=True).returncode:
        return 0
    git("commit", "-q", "-m", "plan: drop a ledger step", "--", name, cwd=directory, check=True)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
