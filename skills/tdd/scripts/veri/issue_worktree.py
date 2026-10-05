"""issue-worktree.sh's worktree handling, run in-process."""
import os
import re
import subprocess
import sys

USAGE = "usage: issue-worktree.sh <n> <slug> | --remove <n>"


def to_contract(code):
    return code if 0 <= code <= 3 else 2


def number_in(file):
    if not os.path.isfile(file):
        return None
    with open(file, newline="") as f:
        n = f.readline().rstrip("\n").strip(" \t")
    return n if re.fullmatch(r"[0-9]+", n) else None


def live_conductor(path):
    pid = number_in(path + "/.tdd/conductor.pid")
    if pid is None:
        return None
    try:
        os.kill(int(pid), 0)
    except (OSError, OverflowError):
        return None
    return pid


def checkout_holder(registry, branch):
    seen = ""
    for line in registry.split("\n"):
        key, _, value = line.partition(" ")
        if key == "worktree":
            seen = value
        elif key == "branch" and value == "refs/heads/" + branch:
            return seen
    return ""


def ref_exists(ref):
    return subprocess.run(["git", "show-ref", "--verify", "--quiet", ref]).returncode == 0


def worktree_add(*args):
    return subprocess.run(["git", "worktree", "add", "-q", *args], stdout=sys.stderr).returncode


def wt_path(main_tree, n):
    return main_tree + "/.tdd/wt/" + n


def main(argv):
    if len(argv) < 2 or not argv[0] or not argv[1]:
        sys.stderr.write(USAGE + "\n")
        return 2
    registry = subprocess.run(["git", "worktree", "list", "--porcelain"], stdout=subprocess.PIPE, text=True)
    if registry.returncode != 0:
        return to_contract(registry.returncode)
    main_tree = registry.stdout.split("\n", 1)[0].removeprefix("worktree ")
    if argv[0] == "--remove":
        path = wt_path(main_tree, argv[1])
        status = subprocess.run(["git", "-C", path, "status", "--porcelain"],
                                stdout=subprocess.PIPE, stderr=sys.stderr, text=True)
        if status.stdout:
            sys.stderr.write("issue-worktree: %s has uncommitted changes — refusing to remove it\n" % path)
            return 2
        removed = subprocess.run(["git", "worktree", "remove", path], stdout=sys.stderr, stderr=sys.stderr)
        return to_contract(removed.returncode)
    path = wt_path(main_tree, argv[0])
    if "worktree " + path in registry.stdout.split("\n"):
        pid = live_conductor(path)
        if pid is not None:
            sys.stderr.write("issue-worktree: %s is held by a live conductor (pid %s)"
                             " — refusing to hand back a run in flight\n" % (path, pid))
            return 2
        sys.stdout.write(path + "\n")
        return 0
    branch = "tdd/%s-%s" % (argv[0], argv[1])
    holder = checkout_holder(registry.stdout, branch)
    if holder:
        sys.stderr.write("issue-worktree: branch %s is already checked out in %s"
                         " — another conductor owns it\n" % (branch, holder))
        return 2
    if ref_exists("refs/heads/" + branch):
        code = worktree_add(path, branch)
    elif ref_exists("refs/remotes/origin/" + branch):
        code = worktree_add("-b", branch, path, "refs/remotes/origin/" + branch)
    else:
        return 0
    if code != 0:
        return to_contract(code)
    sys.stdout.write(path + "\n")
    return 0
