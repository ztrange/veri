"""issue-worktree.sh's worktree handling, run in-process."""
import subprocess
import sys

USAGE = "usage: issue-worktree.sh <n> <slug> | --remove <n>"


def to_contract(status):
    return status if 0 <= status <= 3 else 2


def main(argv):
    if len(argv) < 2 or not argv[0] or not argv[1]:
        print(USAGE, file=sys.stderr)
        return 2
    registry = subprocess.run(["git", "worktree", "list", "--porcelain"], stdout=subprocess.PIPE, text=True)
    if registry.returncode:
        return to_contract(registry.returncode)
    lines = registry.stdout.split("\n")
    main_tree = lines[0].removeprefix("worktree ")
    path = "%s/.tdd/wt/%s" % (main_tree, argv[0])
    if "worktree " + path in lines:
        print(path)
    return 0

