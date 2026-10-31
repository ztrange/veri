"""issue-worktree.sh's worktree handling, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

import event_log
import paths
import tunables
from git import git, symref_default
from github import NoAnswer, gh_json
from json_documents import items
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


def origin_url():
    got = subprocess.run(["git", "remote", "get-url", "origin"],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return got.stdout if got.returncode == 0 else None


def default_branch_name(origin):
    head = git("symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD",
               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if head.returncode == 0:
        return head.stdout.rstrip("\n").removeprefix("origin/"), None
    if origin:
        answer = git("ls-remote", "--symref", "origin", "HEAD",
                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        name = symref_default(answer.stdout) or ""
        return name, ("cannot determine origin's default branch"
                      " (no refs/remotes/origin/HEAD, and the remote did not name one)")
    for name in ("main", "master"):
        if ref_exists("refs/heads/" + name):
            return name, None
    return "", "cannot determine the default branch (no origin/HEAD, no local main or master)"


def remote_issue_branch(issue):
    answer = git("ls-remote", "--heads", "origin", "refs/heads/%s-*" % issue,
                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if answer.returncode != 0:
        return None
    for line in answer.stdout.split("\n"):
        name = line.partition("\trefs/heads/")[2]
        if name:
            return name
    return ""


def claiming_pr(issue, url):
    if not tunables.read("VERI_GH_JSON") and not re.match(r"^(\w+://(?!/)|[^/@]+@[^/]+:)", url.strip()):
        return ""
    try:
        prs = gh_json("prs.json", "repos/{owner}/{repo}/pulls?state=open&per_page=100",
                      "pr", "list", "--state", "open", "--limit", "10000", "--json", "body,state,url")
    except (NoAnswer, OSError):
        return None
    for pr in items(prs):
        if str(pr.get("state", "")).upper() == "OPEN" and \
                issue in re.findall(r"\bCloses #(\d+)", pr.get("body") or ""):
            return pr.get("url") or "an open PR"
    return ""


def worktree_add(*args):
    return subprocess.run(["git", "worktree", "add", "-q", *args], stdout=sys.stderr).returncode


def wt_path(main_tree, n):
    return main_tree + "/.tdd/wt/" + n


def inside_own_scripts():
    scripts = paths.resolved_scripts_of(__file__)
    here = os.path.realpath(os.getcwd())
    return here == scripts or here.startswith(scripts + os.sep)


def ps_field(pid, field):
    ps = subprocess.Popen(["ps", "-p", str(pid), "-o", field + "="], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    out = ps.communicate()[0].strip()
    return out if ps.returncode == 0 else ""


def ancestors():
    found = set()
    pid = os.getpid()
    while pid > 1 and pid not in found:
        found.add(pid)
        parent = ps_field(pid, "ppid")
        pid = int(parent) if parent.isdigit() else 0
    return found


def main(argv):
    if len(argv) < 2 or not argv[0] or not argv[1] or not positive_whole(argv[1] if argv[0] == "--remove" else argv[0]):
        sys.stderr.write(USAGE + "\n")
        return 2
    if inside_own_scripts():
        sys.stderr.write("issue-worktree: type this from the repository the issue belongs to,"
                         " not from the skill's own scripts directory\n")
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
        try:
            with open(path + "/.tdd/pinned-scripts/.snapshot-dir") as where:
                snapshot = where.read()
        except OSError:
            snapshot = ""
        removed = subprocess.run(["git", "worktree", "remove", path], stdout=sys.stderr, stderr=sys.stderr)
        if removed.returncode == 0 and snapshot:
            shutil.rmtree(snapshot, ignore_errors=True)
        return to_contract(removed.returncode)
    path = wt_path(main_tree, argv[0])
    if "worktree " + path in registry.stdout.split("\n"):
        pid = live_conductor(path)
        if pid is not None and int(pid) not in ancestors():
            sys.stderr.write("issue-worktree: %s is held by a live conductor (pid %s)"
                             " — refusing to hand back a run in flight\n" % (path, pid))
            return 2
        if os.path.isdir(path + "/.tdd"):
            open(path + "/.tdd/handed-back", "w").close()
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
    aside = None
    names = []
    if os.path.isdir(tdd) and os.listdir(path) == [".tdd"]:
        found = os.listdir(tdd)
        if set(found) <= {"events.jsonl", "conductor.pid"}:
            names = found
            aside = tempfile.mkdtemp()
            for name in names:
                shutil.move(tdd + "/" + name, aside + "/" + name + ".kept")
            os.rmdir(tdd)
            os.rmdir(path)
    try:
        yield
    finally:
        if aside is not None:
            os.makedirs(tdd, exist_ok=True)
            for name in names:
                if name == "events.jsonl":
                    with open(aside + "/" + name + ".kept", "rb") as src:
                        event_log.append_bytes(tdd + "/" + name, src.read())
                else:
                    shutil.move(aside + "/" + name + ".kept", tdd + "/" + name)
            shutil.rmtree(aside)


def refuse(message):
    sys.stderr.write("issue-worktree: %s\n" % message)
    return 2


def issue_of(branch):
    return branch.split("-", 1)[0].removeprefix("tdd/")


def cut(path, branch):
    remote_ref = "refs/remotes/origin/" + branch
    if ref_exists("refs/heads/" + branch):
        code = worktree_add(path, branch)
    else:
        if ref_exists(remote_ref) and remote_issue_branch("tdd/" + issue_of(branch)):
            sys.stderr.write("issue-worktree: %s is already on origin — another run holds it;"
                             " to take it over run: git branch %s origin/%s\n" % (branch, branch, branch))
            return 2
        url = origin_url()
        origin = url is not None
        if origin:
            issue = issue_of(branch)
            claimed = remote_issue_branch("tdd/" + issue)
            if claimed is None:
                return refuse("git ls-remote origin got no answer"
                              " — cannot tell whether another run claimed the issue")
            if claimed:
                return refuse("%s is already on origin"
                              " — another run claimed the issue" % claimed)
            pr = claiming_pr(issue, url)
            if pr is None:
                return refuse("the open-PR lookup got no answer"
                              " — cannot tell whether another run claimed the issue")
            if pr:
                return refuse("%s claims the issue (Closes #%s)" % (pr, issue))
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
    import entry
    entry.run(main, sys.argv[1:])
