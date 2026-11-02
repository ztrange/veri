"""queued-merge.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

try:
    import tunables
    from github import gh_api
except ImportError:
    from . import tunables
    from .github import gh_api

USAGE = "usage: queued-merge.sh <pr-url> <worktree> <branch> <tag-message|->"
FETCH_ATTEMPTS = 5
SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RELEASE_FILES = ("merge-lock.sh", "lib/shim-python.sh", "lib/venv-python.sh", "veri/merge_lock.py",
                 "veri/tunables.py", "veri/entry.py", "veri/pycache_prefix.py")


def _script(name, *args, scripts=SCRIPTS, cwd=None):
    try:
        return subprocess.run([os.path.join(scripts, name), *args], cwd=cwd).returncode
    except OSError:
        return 2


def _gate(pid, *cmd, keep=False):
    return _script("merge-lock.sh", "gate", *(["--keep"] if keep else []), "--pid", pid, "--", *cmd)


def _git(worktree, *args):
    return subprocess.run(["git", "-C", worktree, *args], capture_output=True, text=True)


def _repo(pr):
    return pr.removeprefix("https://github.com/").rsplit("/pull/", 1)[0]


def _number(pr):
    return pr.rsplit("/pull/", 1)[-1]


def _say(message):
    print("queued-merge: %s" % message, file=sys.stderr)


def _release(pid, scripts=SCRIPTS, cwd=None):
    code = _script("merge-lock.sh", "release", "--pid", pid, scripts=scripts, cwd=cwd)
    if code:
        _say("releasing the merge lock failed (exit %d)" % code)
    return code


def _rev(worktree, ref):
    run = _git(worktree, "rev-parse", "--verify", ref)
    return run.stdout.strip() if run.returncode == 0 else ""


def _merged(repo, pr):
    """GitHub's pull record when it answers merged: true; None when it answers anything else."""
    run = gh_api("repos/%s/pulls/%s" % (repo, _number(pr)))
    try:
        pull = json.loads(run.stdout) if run.returncode == 0 else None
    except ValueError:
        return None
    return pull if isinstance(pull, dict) and pull.get("merged") is True else None


def _merge_commit(worktree, pull, pr):
    """The merge commit GitHub reports for <pr>, fetched into <worktree>; "" when either step fails."""
    sha = pull.get("merge_commit_sha") or ""
    if not isinstance(sha, str) or not sha:
        _say("GitHub reports no merge commit for %s" % pr)
        return ""
    for attempt in range(FETCH_ATTEMPTS):
        if attempt:
            time.sleep(float(tunables.read("VERI_FETCH_RETRY_SLEEP") or "1"))
        fetch = _git(worktree, "fetch", "origin")
        if not fetch.returncode and not _git(worktree, "cat-file", "-e", sha + "^{commit}").returncode:
            return sha
    if fetch.returncode:
        _say("git fetch origin failed (exit %d): %s" % (fetch.returncode, fetch.stderr.strip()))
        return ""
    _say("merge commit %s of %s is not in the clone after a fetch" % (sha, pr))
    return ""


def _tag(worktree, message, pull, pr):
    """Tag the PR's own merge commit, never a re-read origin/main: a concurrent merge may already sit on it."""
    target = _merge_commit(worktree, pull, pr)
    if not target:
        return False
    tags = _git(worktree, "tag", "--sort=-v:refname").stdout.split()
    if not tags:
        _say("no vN.M tag to bump from; no tag cut")
        return False
    major, minor = tags[0].removeprefix("v").split(".")
    name = "v%s.%d" % (major, int(minor) + 1)
    for args in (("tag", "-a", name, "-m", message, target), ("push", "origin", name)):
        if _git(worktree, *args).returncode:
            _say("git %s failed; tag %s not published" % (args[0], name))
            return False
    return True


def _step(failed, what, cwd, *args, label=None):
    run = _git(cwd, *args)
    if run.returncode:
        _say("%s failed (exit %d): %s" % (what, run.returncode, run.stderr.strip()))
        failed.append(label or what)


def _cleanup(pid, pr, pull, worktree, branch, message):
    """Tag, delete the branch, remove the worktree, release the lock: every step runs, each failure is named."""
    failed = []
    clone = os.path.dirname(_git(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    spare = tempfile.mkdtemp(prefix="queued-merge-scripts-")
    scripts = os.path.join(spare, "scripts")
    for name in RELEASE_FILES:
        os.makedirs(os.path.dirname(os.path.join(scripts, name)), exist_ok=True)
        shutil.copy2(os.path.join(SCRIPTS, name), os.path.join(scripts, name))
    if message != "-" and not _tag(worktree, message, pull, pr):
        failed.append("tag")
    _step(failed, "branch delete", worktree, "push", "origin", "--delete", branch)
    _step(failed, "worktree remove", worktree, "worktree", "remove", worktree)
    _step(failed, "local branch delete", clone, "branch", "-D", branch)
    if _release(pid, scripts, clone):
        failed.append("release")
    shutil.rmtree(spare)
    current = _git(clone, "branch", "--show-current").stdout.strip()
    if current not in ("", "main"):
        _say("fast-forward of main to origin/main not done: the main clone is on %s" % current)
        failed.append("fast-forward")
    else:
        _step(failed, "fast-forward of main to origin/main", clone, "pull", "--ff-only", ".", "origin/main",
              label="fast-forward")
    if failed:
        _say("merged, but cleanup failed: %s" % ", ".join(failed))
        return 2
    return 0


def main(argv):
    if len(argv) != 4:
        print(USAGE, file=sys.stderr)
        return 2
    pr, worktree, branch, message = argv
    if not re.fullmatch(r"https://github\.com/[^/]+/[^/]+/pull/\d+", pr):
        print(USAGE, file=sys.stderr)
        return 2
    driver = tunables.read("VERI_GH_DRIVER", None)
    if driver is not None and driver not in ("auto", "rest", "graphql"):
        print("VERI_GH_DRIVER is '%s': expected auto, rest or graphql" % driver, file=sys.stderr)
        return 2
    repo = _repo(pr)
    pid = str(os.getpid())
    code = _script("merge-lock.sh", "take", "--pid", pid)
    if code:
        _say("taking the merge lock failed (exit %d)" % code)
        return code
    code = _gate(pid, "git", "-C", worktree, "fetch", "origin")
    if code:
        return code
    lease = _rev(worktree, "refs/remotes/origin/%s" % branch)
    if not lease:
        _say("origin/%s does not resolve; no lease to pin" % branch)
        _release(pid)
        return 2
    if _git(worktree, "merge-base", "--is-ancestor", lease, "HEAD").returncode:
        _say("origin/%s has commits the worktree lacks; nothing pushed" % branch)
        _release(pid)
        return 2
    for git_args in (("rebase", "origin/main"),
                     ("push", "--force-with-lease=%s:%s" % (branch, lease), "origin", branch)):
        code = _gate(pid, "git", "-C", worktree, *git_args, keep=True)
        if code:
            return code
    head = _rev(worktree, "HEAD")
    if not head:
        _say("the pushed head does not resolve")
        _release(pid)
        return 2
    code = 3
    while code == 3:
        code = _gate(pid, os.path.join(SCRIPTS, "wait-ci.sh"), pr, "540", "", head)
    if code:
        return code
    gh_merge = ("gh", "pr", "merge", pr, "--rebase", "--match-head-commit", head)
    rest_merge = ("gh", "api", "-X", "PUT", "repos/%s/pulls/%s/merge" % (repo, _number(pr)),
                  "-f", "merge_method=rebase", "-f", "sha=%s" % head)
    driver = tunables.read("VERI_GH_DRIVER", None)
    if driver == "graphql":
        code = _gate(pid, *gh_merge)
    elif driver == "auto":
        code = _gate(pid, *gh_merge)
        if code:
            code = _gate(pid, *rest_merge)
    else:
        code = _gate(pid, *rest_merge)
    if code:
        return code
    pull = _merged(repo, pr)
    if pull is None:
        _say("%s is not reported merged; no tag, branch delete or worktree removal" % pr)
        _release(pid)
        return 1
    return _cleanup(pid, pr, pull, worktree, branch, message)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
