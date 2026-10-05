"""issue-worktree.sh's worktree handling, run in-process."""
import subprocess
import sys

USAGE = "usage: issue-worktree.sh <n> <slug> | --remove <n>"


def main(argv):
    if len(argv) < 2 or not argv[0] or not argv[1]:
        sys.stderr.write(USAGE + "\n")
        return 2
    registry = subprocess.run(["git", "worktree", "list", "--porcelain"], stdout=subprocess.PIPE, text=True)
    if registry.returncode != 0:
        return 2
    return 0
