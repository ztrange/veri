"""issue-worktree.sh's worktree handling, run in-process."""
import contextlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

from pid_file import live_conductor

USAGE = "usage: issue-worktree.sh <n> <slug> | --remove <n>"


def to_contract(code):
    return code if 0 <= code <= 3 else 2


def positive_whole(n):
    return re.fullmatch(r"[0-9]+", n) is not None and int(n) > 0


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


def has_origin():
    return subprocess.run(["git", "remote", "get-url", "origin"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def quiet_git(*args):
    return subprocess.run(["git", *args], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)


def default_branch_name(origin):
    head = quiet_git("symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if head.returncode == 0:
        return head.stdout.rstrip("\n").removeprefix("origin/"), None
    if origin:
        answer = quiet_git("ls-remote", "--symref", "origin", "HEAD")
        name = "\n".join(re.findall(r"^ref: refs/heads/(\S*)\s*HEAD$", answer.stdout, re.MULTILINE))
        return name, ("cannot determine origin's default branch"
                      " (no refs/remotes/origin/HEAD, and the remote did not name one)")
    for name in ("main", "master"):
        if ref_exists("refs/heads/" + name):
            return name, None
    return "", "cannot determine the default branch (no origin/HEAD, no local main or master)"


def worktree_add(*args):
    return subprocess.run(["git", "worktree", "add", "-q", *args], stdout=sys.stderr).returncode


def wt_path(main_tree, n):
    return main_tree + "/.tdd/wt/" + n


def main(argv):
    if len(argv) < 2 or not argv[0] or not argv[1] or not positive_whole(argv[1] if argv[0] == "--remove" else argv[0]):
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
    with seeded_log_set_aside(path):
        return cut(path, branch)


@contextlib.contextmanager
def seeded_log_set_aside(path):
    tdd = path + "/.tdd"
    log = tdd + "/events.jsonl"
    seeded_log = None
    if os.path.isfile(log) and os.listdir(path) == [".tdd"] and os.listdir(tdd) == ["events.jsonl"]:
        fd, seeded_log = tempfile.mkstemp()
        os.close(fd)
        shutil.move(log, seeded_log)
        os.rmdir(tdd)
        os.rmdir(path)
    try:
        yield
    finally:
        if seeded_log is not None:
            os.makedirs(tdd, exist_ok=True)
            with open(seeded_log, "rb") as src, open(log, "ab") as dst:
                dst.write(src.read())
            os.remove(seeded_log)


def cut(path, branch):
    remote_ref = "refs/remotes/origin/" + branch
    if ref_exists("refs/heads/" + branch):
        code = worktree_add(path, branch)
    elif ref_exists(remote_ref):
        code = worktree_add("-b", branch, path, remote_ref)
    else:
        origin = has_origin()
        name, refusal = default_branch_name(origin)
        if not name:
            if refusal:
                sys.stderr.write("issue-worktree: %s\n" % refusal)
            return 2
        if origin:
            if subprocess.run(["git", "fetch", "-q", "origin", name], stdout=sys.stderr).returncode != 0:
                sys.stderr.write("issue-worktree: git fetch origin %s failed"
                                 " — refusing to cut %s from a stale origin/%s\n" % (name, branch, name))
                return 2
            name = "origin/" + name
        code = worktree_add("--no-track", "-b", branch, path, name)
    if code != 0:
        return to_contract(code)
    sys.stdout.write(path + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
