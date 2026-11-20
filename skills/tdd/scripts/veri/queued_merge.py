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

import ci_on_pr
import entry
import event
import git
import merge_common
import paths
import run_dir
import run_records
import stack_branch
import tunables
from github import TimedOut, bounded_group, gh_api, gh_probe

USAGE = ("usage: queued-merge.sh [--skip-suite <model-id> <reason>] <pr-url> <worktree> <branch> <tag-message|->\n"
         "       queued-merge.sh --local-green")
SKIPPER = re.compile(r"opus|fable", re.IGNORECASE)
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


def _gate(pid, *cmd, keep=False, cwd=None):
    return _script("merge-lock.sh", "gate", *(["--keep"] if keep else []), "--pid", pid, "--", *cmd, cwd=cwd)


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
    if ci_on_pr.declared(worktree) == "0" and before != head:
        found = subprocess.run([os.path.join(SCRIPTS, "detect-test-command.sh"), "--tier", "all"],
                               cwd=worktree, capture_output=True, text=True)
        full = found.stdout.strip()
        if found.returncode or not full:
            return ("no full test command for the rebased tree (%s); not merged" % (
                "detect-test-command.sh exited %d" % found.returncode if found.returncode
                else "detect-test-command.sh printed nothing"), 2)
        if _gate(pid, "sh", "-c", full, keep=True, cwd=worktree):
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
    code = merge_common.ci_wait(lambda: _gate(pid, os.path.join(SCRIPTS, "wait-ci.sh"), pr, "540", "", head,
                                                       cwd=worktree))
    if code:
        return "", (code, LEAVE)
    refusal = _before_merge(pid, pr, worktree, branch, before, head)
    if refusal:
        return "", _refused(*refusal)
    return head, None


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
    # The merge call keeps the lock even when it errors: an errored call may have landed, and the
    # settle window below re-reads the PR while still holding it, so a landed merge reaches _cleanup
    # with the lock its release expects, and no other merge takes the lock mid-window. A call killed at VERI_GH_TIMEOUT
    # is one that exited non-zero: it may have landed too.
    def merge(*cmd):
        return _network_gate(pid, *cmd, keep=True, limit="VERI_GH_TIMEOUT").returncode

    code = merge_common.merge(merge, pr, repo, _number(pr), head)
    answers = merge_common.settle(lambda: _pull(repo, pr), window, wait_first=bool(code))
    pull = answers[-1] if merge_common.merged(answers[-1]) else None
    answered = any(read is not None for read in answers)
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


def _content_differs(worktree, before, onto, base=None):
    """None when the rebased HEAD's tree equals the tree of merging <before> (the run's pre-rebase tip) with <onto> (the
    stack as fetched), from <base> (the run's recorded base sha) when given: complete by construction, since it compares
    content, not commits. Otherwise the refusal: a merge-tree that fails or reports conflicts is named as that, a
    differing tree names the first paths that differ."""
    merged = _git(worktree, "merge-tree", "--write-tree", *(["--merge-base=" + base] if base else []), before, onto)
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


def _base_sha(worktree, branch):
    """The sha the run's cut recorded in `.tdd/issue-<n>-base-sha` (or its last join rewrote there), None when the file is
    absent: a run cut before it existed rebases as before."""
    path = run_dir.issue_file(worktree, run_dir.branch_issue(branch), "-base-sha")
    try:
        with open(path) as f:
            text = f.read()
    except FileNotFoundError:
        return None
    if not re.fullmatch(r"[0-9a-f]{7,40}\n?", text):
        raise _Garbled("%s holds %r, not one commit sha; nothing rebased or pushed" % (path, text[:80]))
    return text.strip()


class _Garbled(Exception):
    """The run's recorded base sha is not one commit sha; the message names the file."""


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
        frozen, said = _stack_red(worktree)
        if frozen == 0:
            red = (said.split() + ["", ""])[:2]
            _say("the stack is frozen: CI's latest answer on origin/%s is red at %s (%s); nothing rebased or pushed, the"
                 " run kept to join once the stack is green. Next: stack-culprit.sh %s" % (stack, red[0], red[1], red[0]))
            return 1
        if frozen != 3:
            _say("stack-red.sh exited %d, so whether the stack is red is not known; nothing rebased or pushed" % frozen)
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
        # A run whose cut recorded the stack's sha replays only its own commits (D27): a landing rewrites the stack, and
        # a plain rebase would replay the landed commits, conflicting where the default branch moved near one.
        try:
            base = _base_sha(worktree, branch)
        except _Garbled as garbled:
            _say(str(garbled))
            return 2
        rebase = _git(worktree, "rebase", *(["--onto", "origin/" + stack, base] if base else ["origin/" + stack]))
        if rebase.returncode and not _rebasing(worktree):
            _say("git rebase onto origin/%s was refused without a conflict (exit %d); nothing pushed" % (
                stack, rebase.returncode))
            return 2
        if rebase.returncode:
            _git(worktree, "rebase", "--abort")
            _say("rebasing %s onto origin/%s conflicted (%s); aborted, nothing pushed" % (
                branch, stack, " ".join((rebase.stdout + rebase.stderr).split())[:400]))
            return 1
        differs = _content_differs(worktree, before, onto, base)
        if differs:
            return _put_back(worktree, before, differs)
        # The checked tip, saved now: it alone is pushed, to the run branch and to the stack.
        checked = _rev(worktree, "HEAD")
        pushed = git.network("-C", worktree, "push", "--force-with-lease=%s:%s" % (branch, lease),
                             "origin", "%s:refs/heads/%s" % (checked, branch))
        if not pushed.returncode:
            lease = checked
            if base:
                # The run's commits now sit on <onto>, on origin too: the next join replays them from there.
                with open(run_dir.issue_file(worktree, run_dir.branch_issue(branch), "-base-sha"), "w") as f:
                    f.write(onto + "\n")
        if pushed.returncode:
            _say("the leased push of %s failed (exit %d): %s; nothing pushed to %s" % (
                branch, pushed.returncode, pushed.stderr.strip(), stack))
            return 2
        code = _tip_checks(worktree, stack)
        if code:
            return code
        changed = _changed(worktree, checked)
        if changed:
            _say("the fast tier or prose-owed.sh changed the worktree: %s; nothing pushed to %s" % (changed, stack))
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
    answers = merge_common.settle(lambda: _pull(repo, pr), window)
    if merge_common.merged(answers[-1]):
        return 0
    _say("%s did not read merged after the push to %s (last read: %s); the stack is left as pushed" % (
        pr, stack, _state(answers[-1])))
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
    tracked, said = _track(worktree)
    said = " ".join(said.split())[:200] or "it said nothing"
    # The join has already succeeded: a tracking pull request not (re)opened is said, never the join's failure.
    if tracked == 3:
        _say("joined, but stack-pr.sh exit 3 says the stack is not ahead of the default branch right after the push"
             " (%s); no tracking pull request opened" % said)
    elif tracked:
        _say("joined, but stack-pr.sh failed, exit %d (%s); the stack's tracking pull request may be missing" % (
            tracked, said))
    return _join_cleanup(worktree, branch, released)


def _track(worktree):
    """stack-pr.sh run in <worktree>, so the first join after a landing reopens the tracking pull request:
    (exit code, its stderr). Bounded like the join's git network calls: after VERI_GIT_NETWORK_TIMEOUT seconds its
    whole process group is killed and the call answers 2, its stderr naming the limit."""
    run = _bounded([os.path.join(SCRIPTS, "stack-pr.sh")], NETWORK, cwd=worktree, stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE, text=True)
    return run.returncode, run.stderr or ""


def _stack_red(worktree):
    """stack-red.sh run in <worktree>: (exit code, its stdout), its stderr passed through. Bounded like _track."""
    run = _bounded([os.path.join(SCRIPTS, "stack-red.sh")], NETWORK, cwd=worktree, stdout=subprocess.PIPE, text=True)
    return run.returncode, run.stdout or ""


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


def _outage(worktree):
    """True when `.tdd/github-outage` exists in the main working tree <worktree> belongs to, read with no process."""
    clone = _main_clone(worktree)
    return bool(clone) and os.path.exists(os.path.join(clone, ".tdd", "github-outage"))


def _offline_stack(worktree):
    """The stack to join offline while the outage file exists: the stack the worktree's CLAUDE.md names, read with no
    call to origin, when the run's cut recorded it in `.tdd/issue-<n>-base`; None to go on as online."""
    record = stack_branch.recorded_base(worktree)
    if not record:
        return None
    stack = stack_branch.named(worktree, remote=False)
    return stack if stack and record[1].strip() == stack else None


def _join_offline(pid, pr, worktree, branch, stack, skip=None):
    """The offline join (PRD 033.2a): onto the local <stack> under the merge lock, released on every exit path, with no
    call to GitHub. Returns an exit code."""
    code = _script("merge-lock.sh", "take", "--pid", pid)
    if code:
        _say("taking the merge lock failed (exit %d)" % code)
        return code
    try:
        code = _joined_offline(pr, worktree, branch, stack, skip)
    finally:
        released = _release(pid)
    if code:
        return code
    return _offline_cleanup(worktree, branch, released)


def _offline_cleanup(worktree, branch, released):
    """After an offline join, the lock already released: remove the run's worktree and its local branch, and leave its
    remote branch and run records for the recovery, which needs GitHub. 0, or 2 naming each step that failed."""
    failed = ["release"] if released else []
    clone = _main_clone(worktree)
    _step(failed, "worktree remove", worktree, "worktree", "remove", worktree)
    _step(failed, "local branch delete", clone, "branch", "-D", branch)
    if failed:
        _say("joined offline, but cleanup failed: %s" % ", ".join(failed))
        return 2
    return 0


def _holder(worktree, stack):
    """The worktree <stack> is checked out in, "" when none is; None when `git worktree list` fails."""
    listed = _git(worktree, "worktree", "list", "--porcelain")
    if listed.returncode:
        return None
    for block in listed.stdout.split("\n\n"):
        lines = block.splitlines()
        if lines and "branch refs/heads/" + stack in lines:
            return lines[0].removeprefix("worktree ")
    return ""


def _local_stack(worktree, stack):
    """The local <stack>'s sha, created at origin/<stack> as last fetched when absent: (sha, None), or ("", refusal)."""
    holder = _holder(worktree, stack)
    if holder is None:
        return "", "git worktree list failed, so whether %s is checked out is not known" % stack
    if holder:
        return "", "the local %s is checked out in %s, a second writer" % (stack, holder)
    fetched = _rev(worktree, "refs/remotes/origin/" + stack)
    if not fetched:
        return "", "origin/%s does not resolve as last fetched" % stack
    onto = _rev(worktree, "refs/heads/" + stack)
    if not onto:
        made = _git(worktree, "branch", stack, fetched)
        if made.returncode:
            return "", "creating the local %s at origin/%s %s failed (exit %d): %s" % (
                stack, stack, fetched, made.returncode, " ".join(made.stderr.split())[:200])
        return fetched, None
    if _git(worktree, "merge-base", "--is-ancestor", fetched, onto).returncode:
        return "", "the local %s at %s does not descend from origin/%s at %s" % (stack, onto, stack, fetched)
    return onto, None


def _joined_offline(pr, worktree, branch, stack, skip=None):
    """The offline join with the lock held: the online join's guards that need no network (an unticked ledger step, the
    freeze stack-red.sh reads from `.tdd/stack-local-red` (exit 1 while it exits 0, 2 on any exit but 0 and 3), an
    unresolvable HEAD, a merge commit in the run's history, a rebased tip whose content is not the merge), then the
    rebase onto the local <stack>, the fast tier, prose-owed.sh and the full suite, the Veri-Joined amend and a
    fast-forward of the local <stack>. <skip> ("<model-id> <reason>") skips the full suite, recorded as Veri-Suite:
    skipped. A rebased tip that is the stack's own tip is exit 3 when that tip carries this
    run's trailer (joined before), else exit 2: amending it would rewrite the stack. Returns an exit code."""
    code = _unchecked_steps(worktree, branch)
    if code:
        return code
    frozen, said = _stack_red(worktree)
    if frozen == 0:
        _say("the local %s is frozen: stack-red.sh says %s; nothing joined, the run kept to join once a green full run on"
             " the stack's tip lifts it. Next: queued-merge.sh --local-green" % (stack, " ".join(said.split())[:300]))
        return 1
    if frozen != 3:
        _say("stack-red.sh exited %d, so whether the local %s is frozen is not known; nothing joined" % (frozen, stack))
        return 2
    before = _rev(worktree, "HEAD")
    if not before:
        _say("the worktree's HEAD does not resolve; nothing joined")
        return 2
    onto, refusal = _local_stack(worktree, stack)
    if refusal:
        _say(refusal + "; nothing joined")
        return 2
    merges = _git(worktree, "rev-list", "--merges", "%s..%s" % (onto, before))
    if merges.returncode:
        _say("git rev-list --merges %s..%s failed (exit %d); nothing joined" % (onto, before, merges.returncode))
        return 2
    if merges.stdout.strip():
        _say("the run's history holds a merge commit (%s) and must be linear: a rebase would flatten it; nothing"
             " joined. Rebase the run's branch onto the local %s so its history is linear, and join again"
             % (merges.stdout.split()[0], stack))
        return 2
    try:
        base = _base_sha(worktree, branch)
    except _Garbled as garbled:
        _say(str(garbled))
        return 2
    rebase = _git(worktree, "rebase", *(["--onto", stack, base] if base else [stack]))
    if rebase.returncode and not _rebasing(worktree):
        _say("git rebase onto the local %s was refused without a conflict (exit %d); nothing joined" % (
            stack, rebase.returncode))
        return 2
    if rebase.returncode:
        _git(worktree, "rebase", "--abort")
        _say("rebasing %s onto the local %s conflicted (%s); aborted, nothing joined" % (
            branch, stack, " ".join((rebase.stdout + rebase.stderr).split())[:400]))
        return 1
    checked = _rev(worktree, "HEAD")
    if not checked:
        return _put_back(worktree, before, "git rev-parse HEAD failed on the rebased tip")
    if checked == onto:
        return _rejoined(pr, worktree, branch, stack, before, onto)
    differs = _content_differs(worktree, before, onto, base)
    if differs:
        return _put_back(worktree, before, differs)
    code = _tip_checks(worktree, stack)
    if code:
        return code
    if skip:
        _say("the full suite skipped on the rebased tip by --skip-suite %s" % skip)
        code, suite = 0, "skipped " + skip
    else:
        code, suite = _full_gate(worktree, stack)
    if code == 1:
        return _freeze(worktree, stack, checked, suite)
    if code:
        return code
    changed = _changed(worktree, checked)
    if changed:
        _say("the fast tier, prose-owed.sh or the full suite changed the worktree: %s; the local %s not moved" % (
            changed, stack))
        return 2
    amend = _git(worktree, "commit", "--amend", "--no-edit", "--no-verify", "--allow-empty",
                 "--trailer", "Veri-Joined: %s %s" % (pr, branch), "--trailer", "Veri-Suite: " + suite)
    joined = _rev(worktree, "HEAD")
    if amend.returncode or not joined:
        _say("amending the rebased tip with its Veri-Joined trailer failed (exit %d): %s; the local %s not moved" % (
            amend.returncode, " ".join(amend.stderr.split())[:200], stack))
        return 2
    # Only a fast-forward moves the local stack: the amended tip must descend from the stack it was rebased onto.
    if _git(worktree, "merge-base", "--is-ancestor", onto, joined).returncode:
        _say("the joined tip %s does not descend from the local %s at %s; the local %s not moved" % (
            joined, stack, onto, stack))
        return 2
    moved = _git(worktree, "update-ref", "refs/heads/" + stack, joined, onto)
    if moved.returncode:
        _say("moving the local %s from %s to %s failed (exit %d): %s" % (
            stack, onto, joined, moved.returncode, " ".join(moved.stderr.split())[:200]))
        return 2
    print("joined offline, no tag %s" % joined)
    return 0


def _rejoined(pr, worktree, branch, stack, before, onto):
    """The rebased tip is the local <stack>'s own tip <onto>: the run adds no commit to it. Exit 3 when <onto> carries this
    run's `Veri-Joined: <pr> <branch>` trailer (a retry after an offline join whose cleanup failed), the branch put back
    to <before>; exit 2 otherwise. Either way nothing is amended and the stack does not move."""
    shown = _git(worktree, "show", "-s", "--format=%(trailers:key=Veri-Joined,valueonly,unfold)", onto)
    if shown.returncode:
        return _put_back(worktree, before, "git show %s failed (exit %d), so whether the run joined it is not known" % (
            onto, shown.returncode))
    if "%s %s" % (pr, branch) not in [line.strip() for line in shown.stdout.splitlines()]:
        return _put_back(worktree, before, "the rebased tip is the local %s's own tip %s, which carries no Veri-Joined"
                         " trailer of %s %s: the run adds no commit, and amending it would rewrite the stack" % (
                             stack, onto, pr, branch))
    if before != onto and git.git("-C", worktree, "reset", "--hard", before, capture_output=True, text=True).returncode:
        _say("the local %s at %s already carries this run's Veri-Joined trailer, but putting the branch back failed: run"
             " git -C %s reset --hard %s; nothing joined again" % (stack, onto, worktree, before))
        return 2
    _say("the local %s at %s already carries this run's Veri-Joined trailer: joined before; nothing joined again" % (
        stack, onto))
    return 3


def _full_gate(worktree, stack):
    """The all-tier command `detect-test-command.sh --tier all` prints, run on the rebased tip in <worktree>: (code, the
    Veri-Suite trailer's value, or on red the failed cases): 0 "passed" green, 0 "not gated" with no command (said in one
    stderr line), 1 red, 2 when the command cannot be read. The run's output is captured, then written out as it came."""
    found = _start("detect-test-command.sh", "--tier", "all", cwd=worktree, capture=True)
    full = found.stdout.strip()
    if found.returncode not in (0, 3):
        _say("detect-test-command.sh --tier all exited %d; the local %s not moved" % (found.returncode, stack))
        return 2, None
    if not full:
        _say("no all-tier command (detect-test-command.sh --tier all printed nothing); the join onto the local %s is not"
             " gated" % stack)
        return 0, "not gated"
    run = subprocess.run(["sh", "-c", full], cwd=worktree, capture_output=True, text=True)
    sys.stdout.write(run.stdout or "")
    sys.stderr.write(run.stderr or "")
    if run.returncode:
        _say("the full suite (%s) is red on the rebased tip; the local %s not moved" % (full, stack))
        return 1, _failed_cases(run)
    return 0, "passed"


def _failed_cases(run):
    """The cases a red full run names, one per pytest `FAILED <case>` or `ERROR <case>` line of its output; when it names
    none, one line saying so with its exit code."""
    cases = [line.split()[1] for line in ((run.stdout or "") + (run.stderr or "")).splitlines()
             if line.startswith(("FAILED ", "ERROR ")) and len(line.split()) > 1]
    return cases or ["(no FAILED or ERROR line in the full suite's output; exit %d)" % run.returncode]


def _freeze(worktree, stack, checked, cases):
    """After a red gate on <checked>: when a commit of origin/<stack>..<stack> carries `Veri-Suite: skipped`, write
    `.tdd/stack-local-red` in the main working tree (<checked>, then one line per failed case), since the red may then be
    a skipped join's and not the candidate's own (PRD 033.2b, OL9). 1 (the gate's red) once written or with no skipped
    commit, 2 when the range cannot be read or the file cannot be written."""
    span = "refs/remotes/origin/%s..refs/heads/%s" % (stack, stack)
    logged = _git(worktree, "log", "--format=%(trailers:key=Veri-Suite,valueonly,unfold)", span)
    if logged.returncode:
        _say("the full suite is red, but git log of %s failed (exit %d), so whether a Veri-Suite: skipped join sits on the"
             " local %s is not known; nothing frozen" % (span, logged.returncode, stack))
        return 2
    if not any(line.strip().startswith("skipped") for line in logged.stdout.splitlines()):
        return 1
    path = os.path.join(_main_clone(worktree), ".tdd", "stack-local-red")  # resolved already: _outage needed it
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("".join(line + "\n" for line in [checked] + cases))
    except OSError as error:
        _say("the full suite is red over a Veri-Suite: skipped join, but writing %s failed (%s); nothing frozen" % (
            path, error))
        return 2
    _say("a Veri-Suite: skipped join sits on the local %s, so the red may not be this run's: wrote %s, which freezes"
         " joins until queued-merge.sh --local-green runs green" % (stack, path))
    return 1


def _changed(worktree, checked):
    """None when <worktree>'s HEAD is still the <checked> tip and nothing is uncommitted; else what changed, said."""
    head, status = _rev(worktree, "HEAD"), _git(worktree, "status", "--porcelain")
    if head == checked and not status.returncode and not status.stdout.strip():
        return None
    return "HEAD is %s, the checked tip %s%s" % (head or "unresolvable", checked, "; uncommitted: " + " ".join(
        status.stdout.split()[1::2][:5]) if status.stdout.strip() else "")


def _tip_checks(worktree, stack):
    """The fast tier and prose-owed.sh on the rebased tip in <worktree>: 0 green, 1 red or a unit owing a grade, 2 no
    answer."""
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


def _skip_suite(argv):
    """(skip, rest, None) from argv: skip is "<model-id> <reason>" when argv starts with --skip-suite, else None;
    (None, None, code) refusing an id naming neither opus nor fable, or a blank reason (PRD 033.2b, OL6)."""
    if argv[:1] != ["--skip-suite"]:
        return None, argv, None
    if len(argv) != 7:
        print(USAGE, file=sys.stderr)
        return None, None, 2
    model, reason = argv[1], " ".join(argv[2].split())
    if not SKIPPER.search(model):
        _say("--skip-suite takes a model id naming opus or fable, not %r: a model below Opus never skips the gate;"
             " nothing done" % model[:80])
        return None, None, 2
    if not reason:
        _say("--skip-suite needs a reason after the model id; nothing done")
        return None, None, 2
    return "%s %s" % (model, reason), argv[3:], None


def _local_green(argv):
    """--local-green (PRD 033.2b, OL20), run in the target repository's clone during an outage: under the merge lock, the
    all-tier command on the local stack's tip in a worktree added there and removed after; green removes
    `.tdd/stack-local-red` (0), red keeps it (1). 2 outside an outage, with no stack named or on no answer; 3 when no
    `.tdd/stack-local-red` exists, nothing locked or run."""
    if argv:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        clone = run_dir.main_tree_from_files()
    except OSError as error:
        _say("the main working tree cannot be read (%s); nothing run" % error)
        return 2
    if not os.path.exists(os.path.join(clone, ".tdd", "github-outage")):
        _say("--local-green runs only during a GitHub outage (.tdd/github-outage exists); online, CI's answer on the stack"
             " lifts a freeze; nothing run")
        return 2
    try:
        stack = stack_branch.named(clone, remote=False)
    except stack_branch.Refused as refused:
        _say("%s; nothing run" % refused)
        return 2
    if not stack:
        _say("the repository's CLAUDE.md names no stack branch, so there is no local stack to run; nothing run")
        return 2
    red = os.path.join(clone, ".tdd", "stack-local-red")
    if not os.path.exists(red):
        _say("%s does not exist, so the local %s is not frozen; nothing run" % (red, stack))
        return 3
    pid = str(os.getpid())
    code = _script("merge-lock.sh", "take", "--pid", pid)
    if code:
        _say("taking the merge lock failed (exit %d)" % code)
        return code
    try:
        code = _green_tip(clone, stack, red, pid)
    finally:
        released = _release(pid)
    return 2 if released else code


def _green_tip(clone, stack, red, pid):
    """The all-tier command on the local <stack>'s tip, in a worktree added at it and removed after, with the lock held:
    0 green and <red> removed, 1 red and <red> kept, 2 on no answer (a failed worktree removal included)."""
    tip = _rev(clone, "refs/heads/" + stack)
    if not tip:
        _say("the local %s does not resolve; %s kept" % (stack, red))
        return 2
    worktree = os.path.join(clone, ".tdd", "local-green-" + pid)
    added = _git(clone, "worktree", "add", "--detach", worktree, tip)
    if added.returncode:
        _say("git worktree add --detach %s %s failed (exit %d): %s; %s kept" % (
            worktree, tip, added.returncode, " ".join(added.stderr.split())[:200], red))
        return 2
    try:
        code = _green_run(worktree, stack, tip, red)
    finally:
        # An error or Ctrl-C mid-suite still removes the worktree this run added, and only it.
        removed = _git(clone, "worktree", "remove", "--force", worktree)
    if removed.returncode:
        _say("git worktree remove --force %s failed (exit %d): %s" % (
            worktree, removed.returncode, " ".join(removed.stderr.split())[:200]))
        return 2
    return code


def _green_run(worktree, stack, tip, red):
    found = _start("detect-test-command.sh", "--tier", "all", cwd=worktree, capture=True)
    full = found.stdout.strip()
    if found.returncode not in (0, 3) or not full:
        _say("no all-tier command for the local %s's tip (detect-test-command.sh --tier all exited %d%s), so no green run"
             " can lift the freeze; %s kept" % (stack, found.returncode, "" if full else ", printing nothing", red))
        return 2
    if subprocess.run(["sh", "-c", full], cwd=worktree).returncode:
        _say("the full suite (%s) is red on the local %s's tip %s; %s kept" % (full, stack, tip, red))
        return 1
    try:
        os.remove(red)
    except OSError as error:
        _say("the full suite is green on the local %s's tip %s, but removing %s failed (%s)" % (stack, tip, red, error))
        return 2
    _say("the full suite is green on the local %s's tip %s; removed %s, so joins go on" % (stack, tip, red))
    return 0


def main(argv):
    if argv[:1] == ["--local-green"]:
        return _local_green(argv[1:])
    skip, argv, refused = _skip_suite(argv)
    if refused is not None:
        return refused
    if len(argv) != 4:
        print(USAGE, file=sys.stderr)
        return 2
    pr, worktree, branch, message = argv
    if not re.fullmatch(r"https://github\.com/[^/]+/[^/]+/pull/\d+", pr):
        print(USAGE, file=sys.stderr)
        return 2
    clone, issue = _main_clone(worktree), run_dir.branch_issue(branch)
    if clone is None:
        return _merge(pr, worktree, branch, message, skip)
    return event.stage("merge", lambda: _merge(pr, worktree, branch, message, skip), clone,
                       event.context(tunables.with_values(VERI_ISSUE=issue)) if issue else None)


def _main_clone(worktree):
    """The main working tree <worktree> belongs to, read from its `.git` as git reads it, with no process: the merge's
    stage lines go there, never to the worktree the merge removes. None when it cannot be read."""
    try:
        return os.path.dirname(os.path.normpath(os.path.abspath(event.common_dir(worktree))))
    except (OSError, UnicodeDecodeError):
        return None


def _merge(pr, worktree, branch, message, skip=None):
    driver = tunables.get("VERI_GH_DRIVER")
    if driver not in ("auto", "rest", "graphql"):
        print("VERI_GH_DRIVER is '%s': expected auto, rest or graphql" % driver, file=sys.stderr)
        return 2
    window, refusal = merge_common.settle_window()
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
    if _outage(worktree):
        try:
            stack = _offline_stack(worktree)
        except stack_branch.Refused as refused:
            _say("%s; nothing joined" % refused)
            return 2
        if stack:
            return _join_offline(pid, pr, worktree, branch, stack, skip)
    if skip:
        _say("--skip-suite skips only the offline join's gate, and this join is not offline (no .tdd/github-outage, or"
             " the run's recorded base names no stack); nothing done")
        return 2
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
