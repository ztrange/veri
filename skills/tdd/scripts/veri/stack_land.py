"""stack-land.sh's logic, run in-process: lands the stack's tested cut on the default branch (PRD 034.4a)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import re
import subprocess
import sys
import tempfile

import entry
import event
import git
import github
import merge_common
import pid_file
import run_dir
import stack_branch
import stack_fix
import tunables

USAGE = "usage: stack-land.sh [--now]"
# A merge refusal naming the repository's rules: gh's own, for a pull request its base branch's rules block, and
# GitHub's, for a merge a ruleset refuses.
RULES = r"base branch policy|Repository rule violations"


def _pulls_onto(stack):
    """The urls of the open pull requests whose base is <stack>, kept only when the answer itself names <stack> as the
    base ref and the pull request's head is in this repository (Pull.cross_repository): a fork's, which anyone can open,
    keeps nothing live."""
    run = github.gh_api("repos/{owner}/{repo}/pulls?state=open&base=%s&per_page=100" % stack, stderr=subprocess.PIPE)
    raws = json.loads(run.stdout)
    return [pr.html_url for raw, pr in zip(raws, github.pulls_in(run.stdout))
            if (raw.get("base") or {}).get("ref") == stack and not pr.cross_repository]


def _living_conductors():
    """The runs (`#<n>`) whose journal's last conductor-start names a living conductor, as status.sh's Running section
    reads them."""
    lives = []
    for path, events in event.journals("stack-land.sh"):
        starts = [e for e in events if e.get("event") == "conductor-start"]
        if starts and pid_file.conductor_alive(starts[-1]):
            lives.append(event.run_name(path))
    return lives


def _live(stack):
    """What keeps <stack> live, said in a few words: the open pull requests onto it, else the living conductors; None
    when it is idle."""
    pulls = _pulls_onto(stack)
    if pulls:
        return "open pull requests onto %s: %s" % (stack, " ".join(pulls))
    conductors = _living_conductors()
    return "living conductors: %s" % " ".join(conductors) if conductors else None


def _closes(stack, default, cut):
    """The slice body's `Closes #<n>` lines: one per issue a subject in origin/<default>..<cut> ends with `(#<n>)` for,
    in the range's order, kept only when a pull request merged into <stack> carries `Closes #<n>`; an issue named only by
    subjects is said on stderr."""
    joined = _read("reading the pull requests merged into %s" % stack, github.joined_issues, stack)
    span = "origin/%s..%s" % (default, cut)
    named = re.findall(r"\(#(\d+)\)$", _read("git log of " + span, git.out, "log", "--format=%s", span), re.M)
    issues = list(dict.fromkeys(named))
    only = [n for n in issues if int(n) not in joined]
    if only:
        print("stack-land: issues named only by commit subjects in origin/%s..%s, given no Closes line: %s"
              % (default, cut, " ".join("#" + n for n in only)), file=sys.stderr)
    return "".join("Closes #%s\n" % n for n in issues if int(n) in joined)


def _unproven(default, cut):
    """The slice body's lines naming what no suite proved: one per commit of origin/<default>..<cut> whose Veri-Suite
    trailer reads skipped, in the range's order, then one naming .tdd/stack-local-red in the main working tree when it
    exists, with its first line. A range with neither gives none."""
    span = "origin/%s..%s" % (default, cut)
    said = _read("git log of " + span, git.out, "log", "--reverse",
                 "--format=%h%x1f%s%x1f%(trailers:key=Veri-Suite,valueonly,unfold,separator=%x20)", span)
    lines = []
    for record in said.splitlines():
        short, subject, suite = (record.split("\x1f") + ["", ""])[:3]
        if suite.startswith("skipped"):
            lines.append("Suite skipped on %s %s: %s\n" % (short, subject, suite.strip()))
    red = os.path.join(run_dir.main_tree_from_files(), ".tdd", "stack-local-red")
    if os.path.exists(red):
        with open(red, encoding="utf-8", errors="replace") as f:
            first = f.readline().strip()
        lines.append(".tdd/stack-local-red exists: a local full run was red: %s\n" % first)
    return "".join(lines)


def _pull(repo, number):
    """GitHub's record of pull request <number> of <repo>, read as queued-merge.sh reads it; None when GitHub gave no
    answer or the answer is not a JSON object, so the settle window reads again."""
    try:
        pull = json.loads(github.gh_api("repos/%s/pulls/%s" % (repo, number), stderr=subprocess.PIPE).stdout)
    except (github.NoAnswer, ValueError):
        return None
    return pull if isinstance(pull, dict) else None


def _issue_state(repo, number):
    """The state GitHub's record of issue <number> of <repo> reads, as parked_issues.py reads a blocker's."""
    return json.loads(github.gh_api("repos/%s/issues/%s" % (repo, number), stderr=subprocess.PIPE).stdout).get("state")


class _Conflict(Exception):
    """The rebase of the cut onto origin/<default> failed; the message is git's stderr."""


def _rebased(cut, default):
    """<cut> rebased onto origin/<default> in a detached worktree of its own, removed after: the rebased head. A rebase
    that fails is aborted and its worktree removed, then raised as _Conflict."""
    with tempfile.TemporaryDirectory() as parent:
        tree = os.path.join(parent, "slice")
        git.out("worktree", "add", "--detach", tree, cut, cwd=".")
        try:
            git.out("-C", tree, "rebase", "origin/" + default)
        except git.GitFailed as failed:
            git.ok("-C", tree, "rebase", "--abort")
            raise _Conflict(failed.stderr) from None
        else:
            head = git.out("-C", tree, "rev-parse", "HEAD")
        finally:
            git.out("worktree", "remove", "--force", tree, cwd=".")
    return head


class _Unanswered(Exception):
    """A read after the merge lock was taken got no answer; the message names the read."""


def _read(what, call, *args):
    """<call>(*<args>)'s answer; _Unanswered naming <what> when GitHub gave none (NoAnswer, or an answer that is not
    JSON) or git failed."""
    try:
        return call(*args)
    except (github.NoAnswer, ValueError, git.GitFailed) as failed:
        detail = failed.detail if isinstance(failed, github.NoAnswer) else str(failed)
        raise _Unanswered("%s got no answer: %s" % (what, " ".join(detail.split()))) from None


def _freed(line):
    """Free the merge lock this process holds, then refuse with <line> (exit 2)."""
    stack_fix.script("merge-lock.sh", "release", "--pid", str(os.getpid()))
    return entry.refuse(line, prefix="stack-land: ")


def _kept(line, pr):
    """<line>, adding that nothing merged and the slice branch and its pull request <pr> are kept."""
    return "%s; nothing merged, the merge lock freed, the slice branch and %s kept" % (line, pr)


def _refused(line):
    """Free the merge lock this process holds, then say <line> on stderr: a clean negative (exit 1)."""
    stack_fix.script("merge-lock.sh", "release", "--pid", str(os.getpid()))
    print("stack-land: " + line, file=sys.stderr)
    return 1


def _declined(line, pr):
    """_refused(_kept(<line>, <pr>))."""
    return _refused(_kept(line, pr))


def _after(pr, cut, repo, closed):
    """After the landing of <pr> at <cut>, the merge lock freed: carry the stack, then cut the slice's tags (KL40), then
    read the Closes issues <closed> of <repo>, last, and report those still open. Each runs whatever the one before
    answered; every one that failed, or a Closes read that got no answer, is named on stderr with the command or check
    owed, and any is exit 2. stack-carry.sh and stack-tag.sh take the merge lock themselves and
    run under no bound of ours: their own network calls are bounded, and a bound that killed them would kill them
    holding the lock, which merge-lock.sh never takes over."""
    owed = []
    carried, _ = stack_fix.script("stack-carry.sh", cut)
    if carried not in (0, 3):
        owed.append("stack-carry.sh %s exits %d: the stack is left as it was; owed: stack-carry.sh %s"
                    % (cut, carried, cut))
    tagged, said = stack_fix.script("stack-tag.sh", pr)
    sys.stdout.write(said)
    if tagged not in (0, 3):
        owed.append("stack-tag.sh exits %d: the slice's tags are owed; run stack-tag.sh %s" % (tagged, pr))
    try:
        still = [n for n in closed if _issue_state(repo, n) == "open"]
    except (github.NoAnswer, ValueError, AttributeError) as failed:
        detail = failed.detail if isinstance(failed, github.NoAnswer) else str(failed)
        still = []
        owed.append("reading its Closes issues' state got no answer: %s; owed: check that %s is closed"
                    % (" ".join(detail.split()), " ".join("#" + n for n in closed)))
    if still:
        owed.append("its Closes issues still open after the settle window: %s; the landing left as done"
                    % " ".join("#" + n for n in still))
    for line in owed:
        print("stack-land: %s landed, but %s" % (pr, line), file=sys.stderr)
    return 2 if owed else 0


def main(argv):
    if argv not in ([], ["--now"]):
        return entry.refuse(usage=USAGE)
    try:
        outage = os.path.exists(os.path.join(run_dir.main_tree_from_files(), ".tdd", "github-outage"))
    except OSError as error:
        return entry.refuse("the main working tree cannot be read (%s), so whether GitHub is out is not known"
                            % error, prefix="stack-land: ")
    if outage:
        print("stack-land: .tdd/github-outage exists, so a landing waits for the GitHub outage to end; nothing read,"
              " locked or landed", file=sys.stderr)
        return 3
    size = tunables.get("VERI_SLICE_COMMITS")
    if not (size.isascii() and size.isdigit() and int(size) >= 1):
        return entry.refuse("VERI_SLICE_COMMITS must be a whole number of 1 or more: %r" % size, prefix="stack-land: ")
    window, refusal = merge_common.settle_window()
    if refusal:
        return entry.refuse(refusal, prefix="stack-land: ")
    try:
        stack = stack_branch.named(".")
    except stack_branch.Refused as refused:
        return entry.refuse("stack-branch.sh exits 2: %s" % refused, prefix="stack-land: ")
    if stack is None:
        return entry.refuse("stack-branch.sh exits 3: the repository's CLAUDE.md names no stack branch",
                            prefix="stack-land: ")
    code, said = stack_fix.script("stack-red.sh", limit=stack_fix.NETWORK)
    if code == 0:
        red, url = (said.split() + ["", ""])[:2]
        print("stack-land: the stack is red: CI failed on %s (%s); nothing cut or merged" % (red, url), file=sys.stderr)
        return 1
    if code == 2:
        return entry.refuse("stack-red.sh exits 2: no answer on the stack's CI; nothing cut or merged",
                            prefix="stack-land: ")
    code, said = stack_fix.script("stack-green.sh", limit=stack_fix.NETWORK)
    if code == 3:
        print("stack-land: stack-green.sh exits 3: no tested issue end to cut at; nothing to land", file=sys.stderr)
        return 3
    if code == 2:
        return entry.refuse("stack-green.sh exits 2: no answer on the stack's tested cut; nothing cut or merged",
                            prefix="stack-land: ")
    cut = said.split()[0]
    default = git.default_branch(cwd=".")
    ahead = int(git.out("rev-list", "--count", "origin/%s..%s" % (default, cut)))
    if argv != ["--now"] and ahead < int(size):
        live = _live(stack)
        if live:
            print("stack-land: the cut %s is %d commits ahead of origin/%s, fewer than VERI_SLICE_COMMITS (%s), and the"
                  " stack is live: %s; nothing landed" % (cut, ahead, default, size, live), file=sys.stderr)
            return 3
    code, _ = stack_fix.script("merge-lock.sh", "take", "--pid", str(os.getpid()))
    if code != 0:
        return entry.refuse("merge-lock.sh take exits %d: the merge lock not taken; nothing fetched, pushed or opened"
                            % code, prefix="stack-land: ")
    try:
        fetch = git.network("fetch", "--prune", "origin", cwd=".")
        if fetch.returncode:
            return _freed("git fetch origin failed (exit %d): %s; the merge lock freed, nothing pushed or opened"
                          % (fetch.returncode, fetch.stderr.strip()))
        slice_branch = "%s-slice-%s" % (stack, cut[:10])
        read = git.network("ls-remote", "--heads", "origin", "refs/heads/%s" % slice_branch, cwd=".")
        if read.returncode:
            return _freed("git ls-remote of the slice branch %s failed (exit %d): %s; the merge lock freed, nothing"
                          " pushed" % (slice_branch, read.returncode, read.stderr.strip()))
        listed = read.stdout.split()
        if listed and listed[0] != cut:
            return _freed("the slice branch %s is already on origin at another commit, %s; the merge lock freed,"
                          " nothing pushed" % (slice_branch, listed[0]))
        push = git.network("push", "origin", "%s:refs/heads/%s" % (cut, slice_branch), cwd=".")
        if push.returncode:
            return _freed("git push of the slice branch %s failed (exit %d): %s; the merge lock freed, nothing opened"
                          " or merged" % (slice_branch, push.returncode, push.stderr.strip()))
        reused = _read("listing the open pull requests from " + slice_branch, github.stack_pulls, slice_branch, default)
        if reused:
            pr = reused[0].html_url
        else:
            pr = _read("opening the pull request from %s to %s" % (slice_branch, default), github.pr_open, slice_branch,
                       default, "Land %s at %s" % (stack, cut[:10]),
                       _closes(stack, default, cut) + _unproven(default, cut))
        repo, number = pr.removeprefix("https://github.com/").rsplit("/pull/", 1)
        said = []

        def gate(gh, *args):
            run = github.run_gh(*args, stderr=subprocess.PIPE)
            said.append(run.stderr or "")
            return run.returncode

        head = cut
        if not git.ok("merge-base", "--is-ancestor", "origin/" + default, cut, cwd="."):
            try:
                head = _rebased(cut, default)
            except _Conflict as conflict:
                return _declined("the rebase of the slice branch %s onto origin/%s conflicts: %s"
                                 % (slice_branch, default, " ".join(str(conflict).split())), pr)
            leased = git.network("push", "--force-with-lease=%s:%s" % (slice_branch, cut), "origin",
                                 "%s:refs/heads/%s" % (head, slice_branch), cwd=".")
            if leased.returncode:
                return _freed(_kept("the leased push of the rebased head %s to the slice branch %s failed (exit %d): %s"
                                    % (head, slice_branch, leased.returncode, " ".join(leased.stderr.split())), pr))
            ci = merge_common.ci_wait(lambda: stack_fix.script("wait-ci.sh", pr, "540", "", head)[0])
            if ci == 1:
                return _declined("CI is red on the rebased head %s of the slice branch %s" % (head, slice_branch), pr)
            if ci != 0:
                return _freed(_kept("wait-ci.sh exits %d: no answer on CI at the rebased head %s of the slice branch %s"
                                    % (ci, head, slice_branch), pr))
        code = merge_common.merge(gate, pr, repo, number, head, driver="rest")
        if re.search(RULES, said[-1]):
            return _refused("the merge of %s was refused under the repository's rules (exit %d): %s; the merge lock"
                            " freed, nothing retried" % (pr, code, " ".join(said[-1].split())))
        answers = merge_common.settle(lambda: _pull(repo, number), window, wait_first=bool(code))
        if merge_common.merged(answers[-1]):
            closed = re.findall(r"^Closes #(\d+)$", answers[-1].get("body") or "", re.M)
            print("pull request: %s\nmerge commit: %s\nissues closed: %s"
                  % (pr, answers[-1].get("merge_commit_sha"), " ".join("#" + n for n in closed)))
            stack_fix.script("merge-lock.sh", "release", "--pid", str(os.getpid()))
            return _after(pr, cut, repo, closed)
        last = answers[-1] or {}
        return _freed("%s did not read merged by the end of the settle window after the merge call exited %d (last read:"
                      " state %s, merged %s); the merge lock freed, nothing retried"
                      % (pr, code, repr(last.get("state"))[:40], repr(last.get("merged"))[:40]))
    except _Unanswered as unanswered:
        return _freed("%s; the merge lock freed, nothing merged" % unanswered)
    except BaseException:
        # Any other error after the take (a git failure in the rebase worktree, a KeyboardInterrupt) ends through
        # entry.run's exit 2 or the interrupt; the lock is freed first, since merge-lock.sh never takes over a dead
        # holder's lock and a held one would block every later merge.
        stack_fix.script("merge-lock.sh", "release", "--pid", str(os.getpid()))
        raise


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
