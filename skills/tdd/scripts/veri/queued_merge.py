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

import entry
import event
import git
import paths
import run_dir
import run_records
import stack_branch
import tunables
from github import TimedOut, bounded_group, gh_api, gh_probe

USAGE = "usage: queued-merge.sh <pr-url> <worktree> <branch> <tag-message|->"
FETCH_ATTEMPTS = 5
JOIN_ATTEMPTS = 5
REFRESH_RETRIES = 10
SCRIPTS = paths.resolved_scripts_of(__file__)
VERSION_TAG = re.compile(r"v[0-9]+\.[0-9]+")
NETWORK = "VERI_GIT_NETWORK_TIMEOUT"

RELEASE, LEAVE = "release", "leave"

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


def _bounded(argv, limit, **kwargs):
    """<argv> under github.bounded_group, killed with its whole process group after <limit>'s seconds: a call that
    timed out answers 2, its line naming the call and the limit on the stream the caller captures, else on ours."""
    try:
        run = bounded_group(argv, limit_name=limit, **kwargs)
    except OSError as error:
        return subprocess.CompletedProcess(argv, 2, "", str(error))
    if isinstance(run, TimedOut):
        run.returncode = 2
    return run


def _network_gate(pid, *cmd, keep=False, limit=NETWORK):
    """_gate for a network call, bounded by <limit> (VERI_GIT_NETWORK_TIMEOUT unless named): the CompletedProcess, a
    TimedOut when killed."""
    return _bounded([os.path.join(SCRIPTS, "merge-lock.sh"), "gate", *(["--keep"] if keep else []), "--pid", pid, "--", *cmd],
                    limit)


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


def _network_git(worktree, *args):
    """_git for a network call, bounded by VERI_GIT_NETWORK_TIMEOUT: a call killed at the bound answers 2."""
    return _bounded(["git", "-C", worktree, *args], NETWORK, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


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
            time.sleep(float(tunables.get("VERI_FETCH_RETRY_SLEEP", unless_empty=True)))
        fetch = _network_git(worktree, "fetch", "origin")
        if isinstance(fetch, TimedOut):
            break  # the retries wait for a merge commit not yet visible, not out a hung network
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
    tags = [t for t in _git(worktree, "tag", "--sort=-v:refname").stdout.split() if VERSION_TAG.fullmatch(t)]
    if not tags:
        _say("no vN.M tag to bump from; no tag cut")
        return False
    major, minor = tags[0].removeprefix("v").split(".")
    name = "v%s.%d" % (major, int(minor) + 1)
    if _git(worktree, "tag", "-a", name, "-m", message, target).returncode:
        _say("git tag failed; tag %s not published" % name)
        return False
    try:
        oid = git.out("-C", worktree, "rev-parse", "--verify", "refs/tags/" + name)
    except git.GitFailed:
        oid = ""  # publishing goes on; only a later delete needs it, and refuses without it
    try:
        pushed = _network_git(worktree, "push", "origin", name)
    except Exception as error:
        # Raised after the cut: the tag this run cut must not outlive it unnamed.
        _say("publishing tag %s raised %s: %s; tag %s cut, may have been published, and %s" % (
            name, type(error).__name__, error, name, _untag(worktree, name, oid)))
        return False
    if pushed.returncode:
        failed = "git push failed (exit %d): %s;" % (pushed.returncode, (pushed.stderr or "").strip())
        published = "may have been published" if isinstance(pushed, TimedOut) else "not published"
        _say("%s tag %s cut, %s, and %s" % (failed, name, published, _untag(worktree, name, oid)))
        return False
    return name


def _untag(worktree, name, oid):
    """Delete refs/tags/<name> only while it still points at <oid>, the object this run cut: what became of it, said.
    Never raises; with no <oid> read, nothing is deleted."""
    if not oid:
        return "tag %s left in the clone: its object could not be read" % name
    try:
        deleted = git.git("-C", worktree, "update-ref", "-d", "refs/tags/" + name, oid, capture_output=True, text=True)
    except Exception as error:
        return "tag %s left in the clone: git update-ref -d raised %s: %s" % (name, type(error).__name__, error)
    if deleted.returncode:
        return "tag %s left in the clone: git update-ref -d failed (exit %d): %s" % (
            name, deleted.returncode, deleted.stderr.strip())
    return "removed"


def _step(failed, what, cwd, *args, label=None, runner=_git):
    run = runner(cwd, *args)
    if run.returncode:
        _say("%s failed (exit %d): %s" % (what, run.returncode, run.stderr.strip()))
        failed.append(label or what)


def _delete_branch(failed, worktree, branch, runner):
    """Delete origin's <branch> under a lease pinned to the head this run pushed, so a commit pushed to it since is never
    deleted unseen. A refused or unanswered delete is read again: origin listing no such branch (GitHub may have
    deleted a merged PR's branch already) counts as deleted; listing it, or no answer, appends 'branch delete'."""
    run = runner(worktree, "push", "origin", "--delete", branch, "--force-with-lease=%s:%s" % (branch, _rev(worktree, "HEAD")))
    if not run.returncode:
        return
    listed = runner(worktree, "ls-remote", "--heads", "origin", "refs/heads/" + branch)
    if not listed.returncode and not (listed.stdout or "").strip():
        return
    _say("branch delete failed (exit %d): %s" % (run.returncode, (run.stderr or "").strip()))
    failed.append("branch delete")


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
        try:
            name = _tag(worktree, message, pull, pr)
        except Exception as error:
            _say("cutting the tag raised %s: %s" % (type(error).__name__, error))
            name = ""
        if not name:
            failed.append("tag")
    if message == "-" or name:
        issue = re.match(r"tdd/(\d+)-", branch)
        if issue:
            event.mark(worktree, {"issue": issue.group(1)}, "merged",
                       ["pr=" + pr, "tag=" + name, "message=" + (message if name else "")])
    _delete_branch(failed, worktree, branch, _network_git)
    run_issue = run_dir.branch_issue(branch)
    if run_issue:
        records = _network_git(worktree, "push", "origin", "--delete", run_records.ref(run_issue))
        if records.returncode and "remote ref does not exist" not in (records.stderr or ""):
            _say("run records delete failed (exit %d): %s" % (records.returncode, (records.stderr or "").strip()))
            failed.append("run records delete")
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


def _refused(message, code=2):
    """A refusal that frees the lock: main releases it once, after the message."""
    _say(message)
    return code, RELEASE


def _before_rebase(repo, pr, worktree, branch):
    """The checks made before the rebase: (lease, None) to go, ("", (message, code)) to refuse. No lock logic."""
    if _merged(repo, pr) is not None:
        return "", ("%s is already merged; nothing rebased or pushed" % pr, 2)
    if _closed(repo, pr):
        return "", ("%s is closed and unmerged; nothing rebased or pushed" % pr, 2)
    pull = _pull(repo, pr)
    head_sha = ((pull or {}).get("head") or {}).get("sha")
    if not isinstance(head_sha, str) or not head_sha:
        return "", ("could not read the head of %s from GitHub; nothing rebased or pushed" % pr, 2)
    if not _git(worktree, "merge-base", "--is-ancestor", head_sha, "origin/main").returncode:
        return "", ("the head %s of %s is already on origin/main; nothing rebased or pushed" % (head_sha, pr), 2)
    lease = _rev(worktree, "refs/remotes/origin/%s" % branch)
    if not lease:
        return "", ("origin/%s does not resolve; no lease to pin" % branch, 2)
    if not _synced(worktree, lease):
        return "", ("origin/%s has commits the worktree lacks; nothing pushed" % branch, 2)
    return lease, None


def _before_merge(pid, pr, worktree, branch, before, head):
    """The checks between the pushed head's CI and the merge call: None to go, (message, code) to refuse."""
    if tunables.read("VERI_CI_ON_PR") == "0" and before != head:
        found = subprocess.run([os.path.join(SCRIPTS, "detect-test-command.sh"), "--tier", "all"],
                               cwd=worktree, capture_output=True, text=True)
        full = found.stdout.strip()
        if found.returncode or not full:
            return ("no full test command for the rebased tree (%s); not merged" % (
                "detect-test-command.sh exited %d" % found.returncode if found.returncode
                else "detect-test-command.sh printed nothing"), 2)
        if _gate(pid, "sh", "-c", full, keep=True):
            return "the full test command (%s) is red on the rebased tree; not merged" % full, 1
    own = re.match(r"tdd/(\d+)-", branch)
    if own:
        paths = glob.glob(run_dir.ledger(worktree, own.group(1)))
    else:
        changed = _git(worktree, "diff", "--name-only", "origin/main...HEAD", "--", ".tdd/issue-*.md")
        if changed.returncode:
            return ("git diff --name-only origin/main...HEAD failed (exit %d): %s; not merged" % (
                changed.returncode, changed.stderr.strip()), 2)
        paths = changed.stdout.split()
    for path in paths:
        number = re.match(r"issue-(\d+)\.md", os.path.basename(path))
        if not number:
            continue
        shown = gh_probe("pr", "view", pr, "--json", "body")
        if shown.returncode:
            return "could not read the PR body of %s; not merged" % pr, 2
        body = json.loads(shown.stdout)["body"]
        if not re.search(r"Closes #%s\b" % number.group(1), body):
            return "the PR body of %s lacks the line 'Closes #%s'; not merged" % (pr, number.group(1)), 2
    return None


def _rebasing(worktree):
    """True when <worktree> holds a rebase stopped mid-way (git's rebase-merge or rebase-apply directory exists)."""
    for name in ("rebase-merge", "rebase-apply"):
        found = _git(worktree, "rev-parse", "--git-path", name)
        where = found.stdout.strip()
        if not found.returncode and where and os.path.isdir(os.path.join(worktree, where)):
            return True
    return False


def _to_merge(pid, repo, pr, worktree, branch):
    """Fetch, rebase, push, wait for CI and check before the merge: (head, None) to merge, ("", (code, outcome)) to stop."""
    fetch = _network_gate(pid, "git", "-C", worktree, "fetch", "origin")
    if fetch.returncode:
        # A gate killed at the bound never released the lock its failure releases: main does.
        return "", (fetch.returncode, RELEASE if isinstance(fetch, TimedOut) else LEAVE)
    lease, refusal = _before_rebase(repo, pr, worktree, branch)
    if refusal:
        return "", _refused(*refusal)
    before = _rev(worktree, "HEAD")
    code = _rebase(pid, worktree, ("rebase", "origin/main"))
    if code:
        return "", (code, LEAVE)
    push = _network_gate(pid, "git", "-C", worktree, "push", "--force-with-lease=%s:%s" % (branch, lease),
                         "origin", "HEAD:refs/heads/%s" % branch, keep=True)
    if isinstance(push, TimedOut):
        _say("the leased push was killed at the bound; lock kept, clear it with merge-lock.sh release --force")
    if push.returncode:
        return "", (push.returncode, LEAVE)
    head = _rev(worktree, "HEAD")
    if not head:
        return "", _refused("the pushed head does not resolve")
    code = 3
    while code == 3:
        code = _gate(pid, os.path.join(SCRIPTS, "wait-ci.sh"), pr, "540", "", head)
    if code:
        return "", (code, LEAVE)
    refusal = _before_merge(pid, pr, worktree, branch, before, head)
    if refusal:
        return "", _refused(*refusal)
    return head, None


def _settle_window():
    """(reads, sleep) for the settle window from VERI_MERGE_SETTLE_READS (a whole number >= 1) and
    VERI_MERGE_SETTLE_SLEEP (a non-negative number of seconds); a refusal message instead when either is unusable."""
    reads = tunables.get("VERI_MERGE_SETTLE_READS", unless_empty=True)
    sleep = tunables.get("VERI_MERGE_SETTLE_SLEEP", unless_empty=True)
    if entry.whole_number(reads) is None:
        return None, "VERI_MERGE_SETTLE_READS is '%s': expected a whole number of at least 1" % reads
    try:
        seconds = float(sleep)
    except ValueError:
        seconds = -1.0
    if not seconds >= 0 or seconds == float("inf"):
        return None, "VERI_MERGE_SETTLE_SLEEP is '%s': expected a non-negative number of seconds" % sleep
    return (entry.whole_number(reads), seconds), None


def _locked(pid, repo, pr, worktree, branch, message, window):
    """Everything after the lock is taken: returns (exit code, RELEASE | LEAVE), never releasing itself.

    main releases the lock exactly once when the outcome is RELEASE. LEAVE means the lock needs
    nothing more from main, for one of two reasons:

    Kept on purpose, held for the next merge or the operator to recover:
      - the rebase stops (a conflict, a dirty "would be overwritten" stop, a phantom stop past the
        retry bound): exits git's code, nothing pushed;
      - the push under the pinned lease is refused: exits git's code.

    Already settled by the callee:
      - the first fetch, the wait-ci gate: a gate without --keep releases the lock itself on failure;
      - _cleanup: releases the lock after the tag, branch delete and worktree removal.

    An exception escaping before the merge call is exit 2, named in entry.refusal's form: RELEASE, or LEAVE when
    a rebase is stopped mid-way in the worktree, kept as a rebase stop keeps it;
    after the call, _cleanup releases from a copy of the scripts, so no blanket release is safe there.
    """
    try:
        head, stop = _to_merge(pid, repo, pr, worktree, branch)
    except Exception as error:
        sys.stderr.write(entry.refusal(main, error))
        if _rebasing(worktree):
            _say("a rebase is stopped in %s; lock kept, clear it with merge-lock.sh release --force" % worktree)
            return 2, LEAVE
        return 2, RELEASE
    if stop:
        return stop
    gh_merge = ("gh", "pr", "merge", pr, "--rebase", "--match-head-commit", head)
    rest_merge = ("gh", "api", "-X", "PUT", "repos/%s/pulls/%s/merge" % (repo, _number(pr)),
                  "-f", "merge_method=rebase", "-f", "sha=%s" % head)
    driver = tunables.get("VERI_GH_DRIVER")
    # The merge call keeps the lock even when it errors: an errored call may have landed, and the
    # settle window below re-reads the PR while still holding it, so a landed merge reaches _cleanup
    # with the lock its release expects, and no other merge takes the lock mid-window. A call killed at VERI_GH_TIMEOUT
    # is one that exited non-zero: it may have landed too.
    def merge(*cmd):
        return _network_gate(pid, *cmd, keep=True, limit="VERI_GH_TIMEOUT").returncode

    if driver == "graphql":
        code = merge(*gh_merge)
    elif driver == "auto":
        code = merge(*gh_merge)
        if code:
            code = merge(*rest_merge)
    else:
        code = merge(*rest_merge)
    pull, answered = None, False
    reads, sleep = window
    for attempt in range(reads):
        if code or attempt:
            time.sleep(sleep)
        read = _pull(repo, pr)
        answered = answered or read is not None
        if read and read.get("merged") is True:
            pull = read
            break
    if pull is None and not answered:
        call = "exited %d" % code if code else "succeeded"
        return _refused("the merge call %s and the state of %s could not be read; nothing tagged or cleaned up" % (call, pr))
    if pull is None and code:
        return _refused("%s did not read merged after the merge call exited %d; nothing tagged or cleaned up" % (pr, code), code)
    if pull is None:
        return _refused("%s is not reported merged; no tag, branch delete or worktree removal" % pr, 1)
    return _cleanup(pid, pr, pull, worktree, branch, message), LEAVE


def _unchecked_steps(worktree, branch):
    """0 when the run's committed ledger has no unticked line but its `⟦full-suite⟧` ones, which a stacked run never
    ticks (CI on the stack's tip is that run); 1 naming the first other one; 2 when the ledger cannot be read."""
    issue = run_dir.branch_issue(branch)
    if issue is None:
        return 0
    path = run_dir.ledger(worktree, issue)
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError) as error:
        _say("the ledger %s cannot be read (%s); nothing pushed" % (path, error))
        return 2
    for line in lines:
        if line.startswith("- [ ] ") and "⟦full-suite⟧" not in line:
            _say("the ledger %s has an unchecked step: %s; nothing pushed" % (path, line[6:]))
            return 1
    return 0


def _content_differs(worktree, before, onto):
    """None when the rebased HEAD's tree equals the tree of merging <before> (the run's pre-rebase tip) with <onto> (the
    stack as fetched): complete by construction, since it compares content, not commits. Otherwise the refusal: a
    merge-tree that fails or reports conflicts is named as that, a differing tree names the first paths that differ."""
    merged = _git(worktree, "merge-tree", "--write-tree", before, onto)
    if merged.returncode == 1:
        return "git merge-tree --write-tree %s %s reports a conflict, so the rebased tip cannot be checked" % (before, onto)
    expected = merged.stdout.split("\n", 1)[0].strip() if not merged.returncode else ""
    if not expected:
        return "git merge-tree --write-tree %s %s failed (exit %d): %s" % (
            before, onto, merged.returncode, " ".join(merged.stderr.split())[:200])
    actual = _rev(worktree, "HEAD^{tree}")
    if not actual:
        return "git rev-parse HEAD^{tree} failed on the rebased tip"
    if actual == expected:
        return None
    names = _git(worktree, "diff", "--name-only", expected, actual).stdout.split()
    return "the rebased tip's content is not the merge of the run's tip %s and origin's stack %s; differing: %s" % (
        before, onto, " ".join(names[:5]) or "(git diff named no path)")


def _put_back(worktree, before, message):
    """Refuse with <message>, the local branch put back to the run's pre-rebase tip <before>, so the worktree agrees
    with origin's run branch again; exit 2. A reset that fails is said, with the exact command to run."""
    reset = git.git("-C", worktree, "reset", "--hard", before, capture_output=True, text=True)
    if reset.returncode:
        message += "; putting the branch back failed (%s): run git -C %s reset --hard %s" % (
            " ".join(reset.stderr.split())[:200], worktree, before)
    _say(message + "; nothing pushed")
    return 2


def _joined(pid, repo, pr, worktree, branch, stack):
    """The join with the lock held, never releasing it: rebase onto origin/<stack>, push the run's branch under a lease,
    check the rebased tip, push it to <stack> as a compare-and-swap that can only fast-forward what was fetched (leased to
    the fetched stack, the tip descending from it): a push refused because origin's stack moved, or was rewound, starts
    again from the fetch, at most JOIN_ATTEMPTS times; a stack origin no longer has is exit 2. Returns an exit code."""
    code = _unchecked_steps(worktree, branch)
    if code:
        return code
    lease = _rev(worktree, "HEAD")
    if not lease:
        _say("the worktree's HEAD does not resolve; nothing pushed")
        return 2
    for _ in range(JOIN_ATTEMPTS):
        fetch = git.network("-C", worktree, "fetch", "--prune", "origin")
        if fetch.returncode:
            _say("git fetch origin got no answer (%s); nothing pushed" % fetch.stderr.strip())
            return 2
        onto = _rev(worktree, "refs/remotes/origin/" + stack)
        if not onto:
            _say("origin has no %s branch (deleted?); a join never recreates a stack, only a launch does — nothing pushed"
                 % stack)
            return 2
        if _rev(worktree, "refs/remotes/origin/" + branch) != lease:
            _say("origin/%s is not the run's tip %s (a commit the worktree lacks, or none pushed); nothing pushed"
                 % (branch, lease))
            return 2
        # A plain rebase: a join may never lose work. A commit rewound off the stack that the run still carries comes
        # back; the stack is only rewritten by a slice landing, which keeps every patch (git skips identical ones).
        before = _rev(worktree, "HEAD")
        merges = _git(worktree, "rev-list", "--merges", "%s..%s" % (onto, before))
        if merges.returncode:
            _say("git rev-list --merges %s..%s failed (exit %d); nothing pushed" % (onto, before, merges.returncode))
            return 2
        if merges.stdout.strip():
            _say("the run's history holds a merge commit (%s) and must be linear: a rebase would flatten it; nothing"
                 " pushed. Rebase the run's branch onto origin/%s so its history is linear, push it, and join again"
                 % (merges.stdout.split()[0], stack))
            return 2
        rebase = _git(worktree, "rebase", "origin/" + stack)
        if rebase.returncode and not _rebasing(worktree):
            _say("git rebase onto origin/%s was refused without a conflict (exit %d); nothing pushed" % (
                stack, rebase.returncode))
            return 2
        if rebase.returncode:
            _git(worktree, "rebase", "--abort")
            _say("rebasing %s onto origin/%s conflicted (%s); aborted, nothing pushed" % (
                branch, stack, " ".join((rebase.stdout + rebase.stderr).split())[:400]))
            return 1
        differs = _content_differs(worktree, before, onto)
        if differs:
            return _put_back(worktree, before, differs)
        # The checked tip, saved now: it alone is pushed, to the run branch and to the stack.
        checked = _rev(worktree, "HEAD")
        pushed = git.network("-C", worktree, "push", "--force-with-lease=%s:%s" % (branch, lease),
                             "origin", "%s:refs/heads/%s" % (checked, branch))
        if not pushed.returncode:
            lease = checked
        if pushed.returncode:
            _say("the leased push of %s failed (exit %d): %s; nothing pushed to %s" % (
                branch, pushed.returncode, pushed.stderr.strip(), stack))
            return 2
        found = _start("detect-test-command.sh", "--tier", "fast", cwd=worktree, capture=True)
        fast = found.stdout.strip()
        if found.returncode or not fast:
            _say("no fast-tier command for the rebased tip (detect-test-command.sh exited %d); nothing pushed to %s" % (
                found.returncode, stack))
            return 2
        if subprocess.run(["sh", "-c", fast], cwd=worktree).returncode:
            _say("the fast tier (%s) is red on the rebased tip; nothing pushed to %s" % (fast, stack))
            return 1
        owed = _start("prose-owed.sh", worktree, cwd=worktree).returncode
        if owed:
            _say("prose-owed.sh exited %d on the rebased tip; nothing pushed to %s" % (owed, stack))
            return 1 if owed == 1 else 2
        head, status = _rev(worktree, "HEAD"), _git(worktree, "status", "--porcelain")
        if head != checked or status.returncode or status.stdout.strip():
            _say("the fast tier or prose-owed.sh changed the worktree: HEAD is %s, the checked tip %s%s; nothing pushed to"
                 " %s" % (head or "unresolvable", checked, "; uncommitted: " + " ".join(status.stdout.split()[1::2][:5])
                          if status.stdout.strip() else "", stack))
            return 2
        head = checked
        if not head or _git(worktree, "merge-base", "--is-ancestor", onto, head).returncode:
            _say("the rebased tip %s does not descend from origin/%s at %s; nothing pushed to it" % (head, stack, onto))
            return 2
        # A compare-and-swap that can only fast-forward: the lease is the stack as fetched, and the tip descends from it.
        if not git.network("-C", worktree, "push", "--force-with-lease=%s:%s" % (stack, onto), "origin",
                           "%s:refs/heads/%s" % (head, stack)).returncode:
            return 0
        if (git.network("-C", worktree, "fetch", "--prune", "origin").returncode
                or _rev(worktree, "refs/remotes/origin/" + stack) == onto):
            _say("the push of %s to %s was refused and origin's %s did not move; nothing more pushed" % (head, stack, stack))
            return 2
        _say("origin's %s moved during the join; starting again from the fetch" % stack)
    _say("origin's %s moved on each of %d attempts; nothing more pushed" % (stack, JOIN_ATTEMPTS))
    return 2


def _state(pull):
    """What a read of the pull request answered, for a message: GitHub's text is untrusted, so repr'd and cut short."""
    if pull is None:
        return "no answer"
    return "state %s, merged %s" % (repr(pull.get("state"))[:40], repr(pull.get("merged"))[:40])


def _confirmed(repo, pr, stack, window):
    """0 when a read of <pr> over the settle window answers merged: true; 2 naming the last state read otherwise."""
    reads, sleep = window
    last = None
    for attempt in range(reads):
        if attempt:
            time.sleep(sleep)
        last = _pull(repo, pr)
        if last and last.get("merged") is True:
            return 0
    _say("%s did not read merged after the push to %s (last read: %s); the stack is left as pushed" % (
        pr, stack, _state(last)))
    return 2


def _join(pid, repo, pr, worktree, branch, stack, window):
    """Join the run on <branch> to <stack> under the merge lock, released on every exit path."""
    code = _script("merge-lock.sh", "take", "--pid", pid)
    if code:
        _say("taking the merge lock failed (exit %d)" % code)
        return code
    try:
        code = _joined(pid, repo, pr, worktree, branch, stack)
        code = code or _confirmed(repo, pr, stack, window)
    finally:
        released = _release(pid)
    if code:
        return code
    _track(worktree)
    return _join_cleanup(worktree, branch, released)


def _track(worktree):
    """stack-pr.sh run in <worktree>, so the first join after a landing reopens the tracking pull request:
    (exit code, its stderr)."""
    run = _start("stack-pr.sh", cwd=worktree, capture=True)
    return run.returncode, run.stderr or ""


def _join_cleanup(worktree, branch, released):
    """After a confirmed join, the lock already released: delete the run's remote branch, remove its worktree and
    its local branch; the main clone is not moved, since a join does not move the default branch. 0, or 2 naming
    each step that failed (a failed release among them)."""
    failed = ["release"] if released else []
    clone = os.path.dirname(_git(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    _delete_branch(failed, worktree, branch, lambda cwd, *args: git.network("-C", cwd, *args))
    run_issue = run_dir.branch_issue(branch)
    if run_issue:
        records = git.network("-C", worktree, "push", "origin", "--delete", run_records.ref(run_issue))
        if records.returncode and "remote ref does not exist" not in (records.stderr or ""):
            _say("run records delete failed (exit %d): %s" % (records.returncode, (records.stderr or "").strip()))
            failed.append("run records delete")
    _step(failed, "worktree remove", worktree, "worktree", "remove", worktree)
    _step(failed, "local branch delete", clone, "branch", "-D", branch)
    if failed:
        _say("joined, but cleanup failed: %s" % ", ".join(failed))
        return 2
    return 0


def _stack_base(repo, pr, worktree, branch=None):
    """(stack, None) when the worktree's CLAUDE.md names a stack and <pr> reads as based on it, to join; (None, None) to
    merge as before; (None, (message, code)) to refuse before the lock. Raises stack_branch.Refused for a name that
    cannot be a stack."""
    stack = stack_branch.named(worktree)
    record = stack_branch.recorded_base(worktree)
    recorded = record[1].strip() if record else None
    if record and recorded != stack:
        return None, ("%s records the base %r its run was cut from, but the worktree's CLAUDE.md names %s; neither"
                      " joined nor merged" % (record[0], recorded[:80], repr(stack) if stack else "no stack"), 2)
    if not stack:
        return None, None
    pull = _pull(repo, pr)
    base = pull.get("base") if isinstance(pull, dict) else None
    ref = base.get("ref") if isinstance(base, dict) else None
    if not isinstance(ref, str) or not ref:
        return None, ("could not read the base branch of %s from GitHub; neither joined nor merged" % pr, 2)
    if ref != stack:
        return None, None
    default = (base.get("repo") or {}).get("default_branch") if isinstance(base.get("repo"), dict) else None
    if not isinstance(default, str) or not default:
        return None, ("could not read the default branch of %s's repository from GitHub; nothing joined" % pr, 2)
    if default == stack:
        return None, ("the stack branch %s is the default branch of %s's repository; a join there would be a direct"
                      " push to it — nothing joined" % (stack, pr), 2)
    if pull.get("merged") is True:
        return None, ("%s already reads merged into %s; nothing to join" % (pr, stack), 3)
    if pull.get("state") != "open":
        return None, ("%s reads %s and not merged; nothing joined" % (pr, repr(pull.get("state"))[:40]), 2)
    head = pull.get("head") if isinstance(pull.get("head"), dict) else {}
    tip = _rev(worktree, "HEAD")
    if head.get("ref") != branch or not tip or head.get("sha") != tip:
        return None, ("%s's head reads %s at %s, not the branch %s at %s being joined; nothing joined" % (
            pr, repr(head.get("ref"))[:80], repr(head.get("sha"))[:50], branch, tip or "an unresolvable HEAD"), 2)
    return stack, None


def main(argv):
    if len(argv) != 4:
        print(USAGE, file=sys.stderr)
        return 2
    pr, worktree, branch, message = argv
    if not re.fullmatch(r"https://github\.com/[^/]+/[^/]+/pull/\d+", pr):
        print(USAGE, file=sys.stderr)
        return 2
    driver = tunables.get("VERI_GH_DRIVER")
    if driver not in ("auto", "rest", "graphql"):
        print("VERI_GH_DRIVER is '%s': expected auto, rest or graphql" % driver, file=sys.stderr)
        return 2
    window, refusal = _settle_window()
    if refusal:
        print(refusal, file=sys.stderr)
        return 2
    # Read as github.wait_seconds reads them when the call is bounded: set but empty is refused, not the default.
    for name in (NETWORK, "VERI_GH_TIMEOUT"):
        limit = tunables.get(name)
        if entry.whole_number(limit, 1) is None:
            print("%s is '%s': expected a whole number of seconds of at least 1" % (name, limit), file=sys.stderr)
            return 2
    repo = _repo(pr)
    pid = str(os.getpid())
    stack, refusal = _stack_base(repo, pr, worktree, branch)
    if refusal:
        _say(refusal[0])
        return refusal[1]
    if stack:
        return _join(pid, repo, pr, worktree, branch, stack, window)
    code = _script("merge-lock.sh", "take", "--pid", pid)
    if code:
        _say("taking the merge lock failed (exit %d)" % code)
        return code
    code, outcome = _locked(pid, repo, pr, worktree, branch, message, window)
    if outcome is RELEASE:
        _release(pid)
    return code


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
