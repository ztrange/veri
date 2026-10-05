"""issue-worktree.sh's worktree handling, run in-process."""
import subprocess
import sys

USAGE = "usage: issue-worktree.sh <n> <slug> | --remove <n>"


def to_contract(code):
    return code if 0 <= code <= 3 else 2


def main(argv):
    if len(argv) < 2 or not argv[0] or not argv[1]:
        sys.stderr.write(USAGE + "\n")
        return 2
    registry = subprocess.run(["git", "worktree", "list", "--porcelain"], stdout=subprocess.PIPE, text=True)
    if registry.returncode != 0:
        return to_contract(registry.returncode)
    main_tree = registry.stdout.split("\n", 1)[0].removeprefix("worktree ")
    if argv[0] == "--remove":
        path = main_tree + "/.tdd/wt/" + argv[1]
        status = subprocess.run(["git", "-C", path, "status", "--porcelain"],
                                stdout=subprocess.PIPE, stderr=sys.stderr, text=True)
        if status.stdout:
            sys.stderr.write("issue-worktree: %s has uncommitted changes — refusing to remove it\n" % path)
            return 2
        removed = subprocess.run(["git", "worktree", "remove", path], stdout=sys.stderr, stderr=sys.stderr)
        if removed.returncode != 0:
            return to_contract(removed.returncode)
    return 0
