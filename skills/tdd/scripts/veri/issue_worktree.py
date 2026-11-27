"""issue-worktree.sh's worktree handling, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

import entry
import event_log
import git as git_module
import github
import paths
import pinned_scripts
import run_dir
import stack_branch
import tunables
from git import default_branch, git, symref_default
from github import NoAnswer
from pid_file import ancestors, live_conductor

USAGE = "usage: issue-worktree.sh [--take-over] <n> <slug> | --remove <n>"
PREFIX = "issue-worktree: "


def positive_whole(n):
    return entry.whole_number(n) is not None


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
    head = default_branch(remote=False)
    if head:
        return head, None
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


def github_origin(url):
    """Whether GitHub can be asked about origin's pull requests:
    a fixture directory is set, or <url> is a remote URL."""
    return bool(tunables.read("VERI_GH_JSON") or re.match(r"^(\w+://(?!/)|[^/@]+@[^/]+:)", url.strip()))


def claiming_pr(issue, url):
    if not github_origin(url):
        return ""
    try:
        prs = github.open_pulls("body,state,url,isCrossRepository")
    except (NoAnswer, OSError):
        return None
    for pr in prs:
        if pr.state == "OPEN" and not pr.cross_repository and issue in github.closed_issues(pr.body):
            return pr.url or "an open PR"
    return ""


def joined_claim(issue, url, stack):
    """True when a pull request merged into <stack> closes <issue> (its run joined the stack), False when none does or
    origin is not one GitHub can be asked about, None when GitHub gave no answer."""
    if not github_origin(url):
        return False
    try:
        return int(issue) in github.joined_issues(stack)
    except (NoAnswer, OSError, ValueError):
        return None


def worktree_add(*args):
    return subprocess.run(["git", "worktree", "add", "-q", *args], stdout=sys.stderr).returncode


def main(argv):
    take_over = argv[:1] == ["--take-over"]
    if take_over:
        argv = argv[1:]
    if take_over and argv[:1] == ["--remove"]:
        return entry.refuse(usage=USAGE)
    if len(argv) < 2 or not argv[0] or not argv[1] or not positive_whole(argv[1] if argv[0] == "--remove" else argv[0]):
        return entry.refuse(usage=USAGE)
    if paths.inside_scripts(__file__):
        return entry.refuse("type this from the repository the issue belongs to,"
                            " not from the skill's own scripts directory", prefix=PREFIX)
    registry = subprocess.run(["git", "worktree", "list", "--porcelain"], stdout=subprocess.PIPE, text=True)
    if registry.returncode != 0:
        return entry.to_contract(registry.returncode)
    main_tree = registry.stdout.split("\n", 1)[0].removeprefix("worktree ")
    if argv[0] == "--remove":
        path = run_dir.worktree(main_tree, argv[1])
        status = subprocess.run(["git", "-C", path, "status", "--porcelain"],
                                stdout=subprocess.PIPE, stderr=sys.stderr, text=True)
        if status.stdout:
            sys.stderr.write("issue-worktree: %s has uncommitted changes — refusing to remove it\n" % path)
            return 2
        try:
            with open(run_dir.run_file(path, "pinned-scripts/.snapshot-dir")) as where:
                snapshot = where.read()
        except OSError:
            snapshot = ""
        ours = pinned_scripts.snapshot_made_for(snapshot, path)
        removed = subprocess.run(["git", "worktree", "remove", path], stdout=sys.stderr, stderr=sys.stderr)
        if removed.returncode == 0 and ours:
            try:
                pinned_scripts.remove_tree(snapshot)
            except OSError as error:
                sys.stderr.write("issue-worktree: could not remove the snapshot %s: %s\n" % (snapshot, error))
                return 2
        elif removed.returncode == 0 and snapshot and not pinned_scripts.snapshot_gone(snapshot):
            sys.stderr.write("issue-worktree: %s is not a snapshot veri made for %s — left in place\n"
                             % (snapshot, path))
        return entry.to_contract(removed.returncode)
    path = run_dir.worktree(main_tree, argv[0])
    if "worktree " + path in registry.stdout.split("\n"):
        pid = live_conductor(path)
        if pid is not None and int(pid) not in ancestors():
            sys.stderr.write("issue-worktree: %s is held by a live conductor (pid %s)"
                             " — refusing to hand back a run in flight\n" % (path, pid))
            return 2
        if os.path.isdir(path + "/.tdd"):
            open(run_dir.run_file(path, "handed-back"), "w").close()
        sys.stdout.write(path + "\n")
        return 0
    branch = "tdd/%s-%s" % (argv[0], argv[1])
    holder = checkout_holder(registry.stdout, branch)
    if holder:
        sys.stderr.write("issue-worktree: branch %s is already checked out in %s"
                         " — another conductor owns it\n" % (branch, holder))
        return 2
    with seeded_log_set_aside(path):
        return cut(path, branch, take_over, root=main_tree)


@contextlib.contextmanager
def seeded_log_set_aside(path):
    tdd = path + "/.tdd"
    aside = None
    names = []
    if os.path.isdir(tdd) and os.listdir(path) == [".tdd"]:
        found = os.listdir(tdd)
        # A launch may seed the run directory with its journal, its pid and the timeout pin it restored from origin.
        if all(name in ("events.jsonl", "conductor.pid") or re.fullmatch(r"issue-\d+-timeout", name) for name in found):
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


def issue_of(branch):
    return branch.split("-", 1)[0].removeprefix("tdd/")


def took_by_this_lane(issue):
    opt_in = tunables.get("VERI_LABEL")
    return tunables.taken_label(opt_in) in github.gh_issue_view(issue, "labels").split("\n")


def issue_branches(issue, *ref_dir):
    root = "refs/" + "/".join(ref_dir) + "/"
    listed = git("for-each-ref", "--format=%(refname)", root + "tdd/%s-*" % issue,
                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout
    return sorted(line.removeprefix(root) for line in listed.splitlines())


def local_issue_branches(issue):
    return issue_branches(issue, "heads")


def origin_issue_branches(issue):
    return issue_branches(issue, "remotes", "origin")


def take_over_cut(path, branch):
    """--take-over: ask origin which `tdd/<n>-*` branch it holds (the requested one, else its only one), fetch it, and
    cut the worktree on a local branch from origin's tip as just fetched; a local branch of that name is used only when
    it is at that same tip. Every network call is bounded by VERI_GIT_NETWORK_TIMEOUT."""
    issue = issue_of(branch)
    listed = git_module.network("ls-remote", "--heads", "origin", "refs/heads/tdd/%s-*" % issue)
    if listed.returncode != 0:
        return entry.refuse("git ls-remote origin got no answer (%s) — cannot tell which branch to take over"
                            % " ".join((listed.stderr or "").split()), prefix=PREFIX)
    names = sorted(line.partition("\trefs/heads/")[2] for line in listed.stdout.splitlines() if "\trefs/heads/" in line)
    if branch not in names:
        if len(names) != 1:
            return entry.refuse("origin holds %s — nothing to take over as %s"
                                % (", ".join(names) or "no tdd/%s-* branch" % issue, branch), prefix=PREFIX)
        branch = names[0]
    remote_ref = "refs/remotes/origin/" + branch
    fetched = git_module.network("fetch", "-q", "origin", "+refs/heads/%s:%s" % (branch, remote_ref))
    if fetched.returncode != 0:
        return entry.refuse("git fetch origin %s got no answer (%s) — refusing to take over a run from a stale "
                            "origin/%s"
                            % (branch, " ".join((fetched.stderr or "").split()), branch), prefix=PREFIX)
    if ref_exists("refs/heads/" + branch):
        local, remote = (git("rev-parse", "--verify", "-q", ref, stdout=subprocess.PIPE, text=True).stdout.strip()
                         for ref in ("refs/heads/" + branch, remote_ref))
        if local != remote:
            return entry.refuse("the local branch %s is at %s but origin's is at %s — run git branch -f %s origin/%s to"
                                " take origin's run, or push the local branch first to keep it, then run again"
                                % (branch, local, remote, branch, branch), prefix=PREFIX)
        code = worktree_add(path, branch)
    else:
        code = worktree_add("--no-track", "-b", branch, path, "origin/" + branch)
    if code != 0:
        return entry.to_contract(code)
    sys.stdout.write(path + "\n")
    return 0


def created_meanwhile(stack):
    """True when origin now holds refs/heads/<stack>: a push of it was refused because another machine created it."""
    listed = git_module.network("ls-remote", "--heads", "origin", "refs/heads/" + stack)
    return listed.returncode == 0 and bool(listed.stdout.strip())


def stack_cut(path, branch, stack):
    """Cut <branch> at <path> from origin/<stack> as just fetched. Every network call is bounded by
    VERI_GIT_NETWORK_TIMEOUT."""
    listed = git_module.network("ls-remote", "--heads", "origin", "refs/heads/" + stack)
    if listed.returncode != 0:
        return entry.refuse("git ls-remote origin %s got no answer (%s) — cannot tell whether the stack branch exists"
                            % (stack, " ".join((listed.stderr or "").split())), prefix=PREFIX)
    if not listed.stdout.strip():
        default, refusal = default_branch_name(True)
        if not default:
            return entry.refuse(refusal, prefix=PREFIX)
        fetched = git_module.network("fetch", "-q", "origin",
                                     "+refs/heads/%s:refs/remotes/origin/%s" % (default, default))
        if fetched.returncode != 0:
            return entry.refuse("git fetch origin %s got no answer (%s) — refusing to create the stack branch %s from a"
                                " stale origin/%s"
                                % (default, " ".join((fetched.stderr or "").split()), stack, default),
                                prefix=PREFIX)
        pushed = git_module.network("push", "origin", "refs/remotes/origin/%s:refs/heads/%s" % (default, stack))
        if pushed.returncode != 0 and not created_meanwhile(stack):
            return entry.refuse("pushing the stack branch %s to origin at origin/%s was refused or got no answer (%s)"
                                " — no branch and no worktree made"
                                % (stack, default, " ".join((pushed.stderr or "").split())), prefix=PREFIX)
    fetched = git_module.network("fetch", "-q", "origin", "+refs/heads/%s:refs/remotes/origin/%s" % (stack, stack))
    if fetched.returncode != 0:
        return entry.refuse("git fetch origin %s got no answer (%s) — refusing to cut %s from a stale origin/%s"
                            % (stack, " ".join((fetched.stderr or "").split()), branch, stack), prefix=PREFIX)
    read = git_module.git("rev-parse", "--verify", "--quiet", "refs/remotes/origin/%s^{commit}" % stack,
                          capture_output=True, text=True)
    base_sha = read.stdout.strip() if read.returncode == 0 else ""
    if not base_sha:
        return entry.refuse("git rev-parse origin/%s got no answer (exit %d) — no branch and no worktree made"
                            % (stack, read.returncode), prefix=PREFIX)
    code = worktree_add("--no-track", "-b", branch, path, "origin/" + stack)
    if code == 0:
        record_base(path, issue_of(branch), stack, base_sha)
    return code


def record_base(path, issue, stack, base_sha):
    """Record in the run's own state the base its branch was cut from: `.tdd/issue-<n>-base`, the stack's name, written
    once at the cut, never rewritten, read by stack_branch.run_base; and `.tdd/issue-<n>-base-sha`, origin/<stack>'s sha
    as read for the cut, the `<old-base>` a join's `git rebase --onto` starts from (D27), rewritten by the join."""
    record = run_dir.issue_file(path, issue, "-base")
    os.makedirs(os.path.dirname(record), exist_ok=True)
    if not os.path.exists(record):
        with open(record, "w") as f:
            f.write(stack + "\n")
    with open(run_dir.issue_file(path, issue, "-base-sha"), "w") as f:
        f.write(base_sha + "\n")


def cut(path, branch, take_over=False, root="."):
    if take_over:
        return take_over_cut(path, branch)
    remote_ref = "refs/remotes/origin/" + branch
    if ref_exists("refs/heads/" + branch):
        code = worktree_add(path, branch)
    elif (on_origin := ref_exists(remote_ref)) and took_by_this_lane(issue_of(branch)):
        code = worktree_add("--no-track", "-b", branch, path, "origin/" + branch)
    elif len(names := sorted({*(own := local_issue_branches(issue_of(branch))),
                              *origin_issue_branches(issue_of(branch))})) == 1 and own:
        branch = names[0]
        code = worktree_add(path, branch)
    elif len(names) == 1 and took_by_this_lane(issue_of(branch)):
        branch = names[0]
        code = worktree_add("--no-track", "-b", branch, path, "origin/" + branch)
    else:
        if len(names) > 1:
            return entry.refuse("%s exist for the issue — cannot pick one for the requested %s"
                                % (", ".join(names), branch), prefix=PREFIX)
        if on_origin and remote_issue_branch("tdd/" + issue_of(branch)):
            sys.stderr.write("issue-worktree: %s is already on origin — another run holds it;"
                             " to take it over run: issue-worktree.sh --take-over %s\n"
                             % (branch, " ".join(branch.removeprefix("tdd/").split("-", 1))))
            return 2
        url = origin_url()
        origin = url is not None
        if origin:
            issue = issue_of(branch)
            claimed = remote_issue_branch("tdd/" + issue)
            if claimed is None:
                return entry.refuse("git ls-remote origin got no answer"
                                    " — cannot tell whether another run claimed the issue", prefix=PREFIX)
            if claimed:
                return entry.refuse("%s is already on origin"
                                    " — another run claimed the issue" % claimed, prefix=PREFIX)
            pr = claiming_pr(issue, url)
            if pr is None:
                return entry.refuse("the open-PR lookup got no answer"
                                    " — cannot tell whether another run claimed the issue", prefix=PREFIX)
            if pr:
                return entry.refuse("%s claims the issue (Closes #%s)" % (pr, issue), prefix=PREFIX)
        try:
            stack = stack_branch.named(root)
        except stack_branch.Refused as refused:
            return entry.refuse(str(refused), prefix=PREFIX)
        if stack and origin:
            joined = joined_claim(issue_of(branch), url, stack)
            if joined is None:
                return entry.refuse("the lookup of pull requests merged into %s got no answer"
                                    " — cannot tell whether a joined run claims the issue" % stack, prefix=PREFIX)
            if joined:
                return entry.refuse("a pull request merged into the stack branch %s claims the issue (Closes #%s):"
                                    " its run has joined and the issue stays claimed until it lands"
                                    % (stack, issue_of(branch)), prefix=PREFIX)
        if stack:
            code = stack_cut(path, branch, stack)
            if code != 0:
                return entry.to_contract(code)
            sys.stdout.write(path + "\n")
            return 0
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
        return entry.to_contract(code)
    sys.stdout.write(path + "\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
