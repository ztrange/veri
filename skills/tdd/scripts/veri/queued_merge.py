"""queued-merge.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

try:
    import event
    import tunables
    from github import gh_api, gh_probe
    from ledger import ledger_path
except ImportError:
    from . import event
    from . import tunables
    from .github import gh_api, gh_probe
    from .ledger import ledger_path

USAGE = "usage: queued-merge.sh <pr-url> <worktree> <branch> <tag-message|->"
FETCH_ATTEMPTS = 5
REFRESH_RETRIES = 10
SCRIPTS = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

RELEASE_FILES = ("merge-lock.sh", "lib/shim-python.sh", "lib/venv-python.sh", "veri/merge_lock.py",
                 "veri/tunables.py", "veri/entry.py", "veri/pycache_prefix.py")


def _start(name, *args, scripts=SCRIPTS, cwd=None, capture=False):
    try:
        return subprocess.run([os.path.join(scripts, name), *args], cwd=cwd, capture_output=capture, text=True)
    except OSError:
        return subprocess.CompletedProcess(name, 2, "", "")


def _script(name, *args, scripts=SCRIPTS, cwd=None):
    return _start(name, *args, scripts=scripts, cwd=cwd).returncode


def _gate(pid, *cmd, keep=False):
    return _script("merge-lock.sh", "gate", *(["--keep"] if keep else []), "--pid", pid, "--", *cmd)


def _gate_output(pid, *cmd):
    run = _start("merge-lock.sh", "gate", "--keep", "--pid", pid, "--", *cmd, capture=True)
    sys.stdout.write(run.stdout or "")
    sys.stderr.write(run.stderr or "")
    return run.returncode, (run.stdout or "") + (run.stderr or "")


def _rebase(pid, worktree, git_args):
    code, output = _gate_output(pid, "git", "-C", worktree, *git_args)
    for _ in range(REFRESH_RETRIES):
        if not code or "would be overwritten by merge" not in output or _git(worktree, "status", "--porcelain").stdout.strip():
            break
        _gate(pid, "git", "-C", worktree, "update-index", "--really-refresh", keep=True)
        event.mark(worktree, {}, "rebase-refresh-retry")
        code, output = _gate_output(pid, "git", "-C", worktree, "rebase", "--continue")
    return code


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


def _synced(worktree, lease):
    if not _git(worktree, "merge-base", "--is-ancestor", lease, "HEAD").returncode:
        return True
    return (not _git(worktree, "merge-base", "--is-ancestor", "HEAD", lease).returncode
            and not _git(worktree, "status", "--porcelain").stdout.strip()
            and not _git(worktree, "merge", "--ff-only", lease).returncode)


def _pull(repo, pr):
    """GitHub's pull record for <pr> as a dict; None when it cannot be read."""
    run = gh_api("repos/%s/pulls/%s" % (repo, _number(pr)))
    try:
        pull = json.loads(run.stdout) if run.returncode == 0 else None
    except ValueError:
        return None
    return pull if isinstance(pull, dict) else None


def _merged(repo, pr):
    """GitHub's pull record when it answers merged: true; None when it answers anything else."""
    pull = _pull(repo, pr)
    return pull if pull and pull.get("merged") is True else None


def _closed(repo, pr):
    pull = _pull(repo, pr)
    return bool(pull) and pull.get("state") == "closed" and pull.get("merged") is False


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
    return name


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
    name = ""
    if message != "-":
        name = _tag(worktree, message, pull, pr)
        if not name:
            failed.append("tag")
    if message == "-" or name:
        issue = re.match(r"tdd/(\d+)-", branch)
        if issue:
            event.mark(worktree, {"issue": issue.group(1)}, "merged",
                       ["pr=" + pr, "tag=" + name, "message=" + (message if name else "")])
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
    if _merged(repo, pr) is not None:
        _say("%s is already merged; nothing rebased or pushed" % pr)
        _release(pid)
        return 2
    if _closed(repo, pr):
        _say("%s is closed and unmerged; nothing rebased or pushed" % pr)
        _release(pid)
        return 2
    pull = _pull(repo, pr)
    head_sha = ((pull or {}).get("head") or {}).get("sha")
    if not isinstance(head_sha, str) or not head_sha:
        _say("could not read the head of %s from GitHub; nothing rebased or pushed" % pr)
        _release(pid)
        return 2
    if not _git(worktree, "merge-base", "--is-ancestor", head_sha, "origin/main").returncode:
        _say("the head %s of %s is already on origin/main; nothing rebased or pushed" % (head_sha, pr))
        _release(pid)
        return 2
    lease = _rev(worktree, "refs/remotes/origin/%s" % branch)
    if not lease:
        _say("origin/%s does not resolve; no lease to pin" % branch)
        _release(pid)
        return 2
    if not _synced(worktree, lease):
        _say("origin/%s has commits the worktree lacks; nothing pushed" % branch)
        _release(pid)
        return 2
    before = _rev(worktree, "HEAD")
    code = _rebase(pid, worktree, ("rebase", "origin/main"))
    if code:
        return code
    code = _gate(pid, "git", "-C", worktree, "push", "--force-with-lease=%s:%s" % (branch, lease),
                 "origin", "HEAD:refs/heads/%s" % branch, keep=True)
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
    if tunables.read("VERI_CI_ON_PR") == "0" and before != head:
        found = subprocess.run([os.path.join(SCRIPTS, "detect-test-command.sh"), "--tier", "all"],
                               cwd=worktree, capture_output=True, text=True)
        full = found.stdout.strip()
        if found.returncode or not full:
            _say("no full test command for the rebased tree (%s); not merged" % (
                "detect-test-command.sh exited %d" % found.returncode if found.returncode
                else "detect-test-command.sh printed nothing"))
            _release(pid)
            return 2
        if _gate(pid, "sh", "-c", full, keep=True):
            _say("the full test command (%s) is red on the rebased tree; not merged" % full)
            _release(pid)
            return 1
    own = re.match(r"tdd/(\d+)-", branch)
    if own:
        paths = glob.glob(ledger_path(worktree, own.group(1)))
    else:
        changed = _git(worktree, "diff", "--name-only", "origin/main...HEAD", "--", ".tdd/issue-*.md")
        if changed.returncode:
            _say("git diff --name-only origin/main...HEAD failed (exit %d): %s; not merged" % (
                changed.returncode, changed.stderr.strip()))
            _release(pid)
            return 2
        paths = changed.stdout.split()
    for path in paths:
        number = re.match(r"issue-(\d+)\.md", os.path.basename(path))
        if not number:
            continue
        shown = gh_probe("pr", "view", pr, "--json", "body")
        if shown.returncode:
            _say("could not read the PR body of %s; not merged" % pr)
            _release(pid)
            return 2
        body = json.loads(shown.stdout)["body"]
        if not re.search(r"Closes #%s\b" % number.group(1), body):
            _say("the PR body of %s lacks the line 'Closes #%s'; not merged" % (pr, number.group(1)))
            _release(pid)
            return 2
    gh_merge = ("gh", "pr", "merge", pr, "--rebase", "--match-head-commit", head)
    rest_merge = ("gh", "api", "-X", "PUT", "repos/%s/pulls/%s/merge" % (repo, _number(pr)),
                  "-f", "merge_method=rebase", "-f", "sha=%s" % head)
    driver = tunables.read("VERI_GH_DRIVER", None)
    # The merge call keeps the lock even when it errors: an errored call may have landed, and the
    # settle window below re-reads the PR while still holding it, so a landed merge reaches _cleanup
    # with the lock its release expects, and no other merge takes the lock mid-window.
    if driver == "graphql":
        code = _gate(pid, *gh_merge, keep=True)
    elif driver == "auto":
        code = _gate(pid, *gh_merge, keep=True)
        if code:
            code = _gate(pid, *rest_merge, keep=True)
    else:
        code = _gate(pid, *rest_merge, keep=True)
    pull = None
    if code:
        for _ in range(int(tunables.read("VERI_MERGE_SETTLE_READS") or "10")):
            time.sleep(float(tunables.read("VERI_MERGE_SETTLE_SLEEP") or "3"))
            pull = _merged(repo, pr)
            if pull is not None:
                break
        if pull is None:
            _say("%s did not read merged after the merge call exited %d; nothing tagged or cleaned up" % (pr, code))
            _release(pid)
            return code
    else:
        pull = _merged(repo, pr)
    if pull is None:
        _say("%s is not reported merged; no tag, branch delete or worktree removal" % pr)
        _release(pid)
        return 1
    return _cleanup(pid, pr, pull, worktree, branch, message)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
