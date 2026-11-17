"""stack-fix.sh's logic, run in-process: pushes a fix worktree's reviewed hand fix on top of a red stack, once per
culprit, after checking its bounds and running the cases stack-culprit.sh named (PRD 034.3c)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import subprocess
import sys

import detect_test_command
import entry
import git
import github
import paths
import stack_branch
import stack_green

USAGE = "usage: stack-fix.sh <n> <red-sha> <culprit-file>"
SCRIPTS = paths.resolved_scripts_of(__file__)
NETWORK = "VERI_GIT_NETWORK_TIMEOUT"


class NoAnswer(Exception):
    """No answer from git, GitHub or a script (exit 2); str() says why."""


class Refused(Exception):
    """A bound the fix does not hold (exit 1); str() says which."""


def _script(name, *args, limit=None):
    """Run the sibling script <name> with <args>: (exit code, stdout), its stderr passed through. With <limit> (a
    tunable's name) its whole process group is killed at that bound and the call answers 2."""
    argv = [os.path.join(SCRIPTS, name), *args]
    try:
        if limit:
            ran = github.bounded_group(argv, limit_name=limit, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                       text=True)
            return (2 if isinstance(ran, github.TimedOut) else ran.returncode), ran.stdout or ""
        ran = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, text=True)
    except OSError as error:
        print("stack-fix: %s could not start: %s" % (name, error), file=sys.stderr)
        return 2, ""
    return ran.returncode, ran.stdout or ""


def _top():
    """The fix worktree the script was run in."""
    return git.out("rev-parse", "--show-toplevel")


def _rev(ref):
    """The sha <ref> names in the fix worktree, "" when it names none."""
    found = git.git("rev-parse", "--verify", "--quiet", ref + "^{commit}", capture_output=True, text=True)
    return found.stdout.strip() if found.returncode == 0 else ""


def _ancestor(older, newer):
    """Whether <older> is an ancestor of <newer>: True or False, None when git gives no answer."""
    found = git.git("merge-base", "--is-ancestor", older, newer, capture_output=True, text=True)
    return {0: True, 1: False}.get(found.returncode)


TRAILER = "Stack-fix"


def _log(rev_range):
    """The commits of <rev_range>, oldest first, as [(sha, subject, [each Stack-fix trailer value])]. NoAnswer when git
    refuses the log."""
    found = git.git("log", "--reverse", "--format=%H%x1f%s%x1f%(trailers:key=" + TRAILER + ",valueonly,separator=%x1f)%x1e",
                    rev_range, capture_output=True, text=True)
    if found.returncode:
        raise NoAnswer("git log %s failed (exit %d): %s" % (rev_range, found.returncode, " ".join(found.stderr.split())[:200]))
    commits = []
    for record in found.stdout.split("\x1e"):
        fields = record.strip("\n").split("\x1f")
        if len(fields) >= 2:
            commits.append((fields[0], fields[1], [value.strip() for value in fields[2:] if value.strip()]))
    return commits


def _changed(rev_range):
    """The files `git diff --name-status <rev_range>` lists, as [(status, path, ...)] (a rename or copy names both
    paths). NoAnswer when git refuses the diff."""
    found = git.git("diff", "--name-status", "-M", rev_range, capture_output=True, text=True)
    if found.returncode:
        raise NoAnswer("git diff --name-status %s failed (exit %d)" % (rev_range, found.returncode))
    return [tuple(line.split("\t")) for line in found.stdout.splitlines() if line.strip()]


def _dirty():
    """`git status --porcelain` in the fix worktree. NoAnswer when git refuses it."""
    found = git.git("status", "--porcelain", capture_output=True, text=True)
    if found.returncode:
        raise NoAnswer("git status failed (exit %d)" % found.returncode)
    return found.stdout


def _has(path):
    """Whether HEAD holds the file <path>."""
    return git.git("cat-file", "-e", "HEAD:" + path, capture_output=True).returncode == 0


def _run(command, target=None):
    """<command> run in the fix worktree under VERI_TIMEOUT, <target> passed as "$1" (the alone run of a case) when
    given: (exit code, output), the code None when the run gave no answer (no exit within VERI_TIMEOUT, its process
    group killed, or killed by a signal)."""
    if target is not None and '"$1"' not in command:
        command += ' "$1"'
    ran = github.bounded_group(["sh", "-c", command, "sh", *([target] if target is not None else [])],
                               limit_name="VERI_TIMEOUT", stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True)
    if isinstance(ran, github.TimedOut) or not 0 <= ran.returncode < 128:
        return None, ran.stdout or ""
    return ran.returncode, ran.stdout or ""


def _one_file_command(top):
    """The repository's `veri: one test file:` command in <top>; None when it declares none."""
    found = detect_test_command.resolved("one test file", None, top)
    return os.fsdecode(found) if found else None


def _fast_command(top):
    """The repository's fast tier command in <top>; None when none is found."""
    found = detect_test_command.resolved("fast", None, top)
    return os.fsdecode(found) if found else None


def _fetch():
    """Whether `git fetch --prune origin` answered."""
    return git.network("fetch", "--prune", "origin").returncode == 0


def _moved(stack, onto):
    """After a refused push: True when a fetch shows origin's <stack> is no longer <onto>, False when it still is.
    NoAnswer when the fetch gets no answer."""
    if not _fetch():
        raise NoAnswer("the push was refused and a fetch of origin got no answer; nothing pushed")
    return _rev("refs/remotes/origin/" + stack) != onto


def _push(head, stack, onto):
    """Push <head> to <stack> on origin as a compare-and-swap leased to <onto>, the stack as fetched: its exit code
    (a TimedOut answers 124)."""
    return git.network("push", "--force-with-lease=refs/heads/%s:%s" % (stack, onto), "origin",
                       "%s:refs/heads/%s" % (head, stack)).returncode


def _say(message):
    print("stack-fix: " + message, file=sys.stderr)


def _checked(n, red):
    """Every check before the push, with the lock held: (stack, onto, head). Refused or NoAnswer when one fails;
    _NotRed when stack-red.sh exits 3."""
    code, said = _script("stack-red.sh", limit=NETWORK)
    if code != 0:
        raise NoAnswer("stack-red.sh exited %d, so whether the stack is red is not known; nothing pushed" % code)
    now = (said.split() or [""])[0]
    if now != red:
        raise Refused("%s is not the commit red now: stack-red.sh prints %s; nothing pushed" % (red, now))
    try:
        found = stack_branch.ahead(".")
    except stack_branch.Refused as refused:
        raise NoAnswer(str(refused)) from None
    stack, default, _ = found
    onto = _rev("refs/remotes/origin/" + stack)
    for commit, subject, trailers in _log("refs/remotes/origin/%s..refs/remotes/origin/%s" % (default, stack)):
        if trailers and n in stack_green.named(subject):
            raise Refused("%s (%s) on origin/%s already carries a %s: trailer for issue %s: one fix per culprit;"
                          " nothing pushed" % (commit, subject, stack, TRAILER, n))
    head = _rev("HEAD")
    return stack, onto, head


def culprit_answer(text):
    """(red, issues, cases) a stack-culprit.sh answer records: the sha of its `red:` line, the issue numbers of its
    `issue:` line (none for `none`), and the case of each `case:` line, in order. None when it lacks any of them."""
    red = re.search(r"^red: ([0-9a-f]{40})$", text, re.M)
    issues = re.search(r"^issue: (.+)$", text, re.M)
    cases = re.findall(r"^case: ([^\t\n]+)", text, re.M)
    if not (red and issues and cases):
        return None
    return red.group(1), set(issues.group(1).split()) - {"none"}, cases


def main(argv):
    if len(argv) != 3:
        return entry.refuse(usage=USAGE)
    n, red, culprit = argv
    if not re.fullmatch(r"[1-9][0-9]*", n) or not re.fullmatch(r"[0-9a-f]{40}", red):
        return entry.refuse("<n> must be an issue number and <red-sha> a full 40-hex sha", usage=USAGE)
    try:
        with open(culprit, encoding="utf-8", errors="replace") as f:
            answer = culprit_answer(f.read())
    except OSError as error:
        return entry.refuse("the culprit file cannot be read: %s" % error.strerror, prefix="stack-fix: ")
    if answer is None:
        return entry.refuse("the culprit file is not stack-culprit.sh's answer: it lacks its red:, issue: or case:"
                            " lines; nothing pushed", prefix="stack-fix: ")
    recorded, issues, cases = answer
    if recorded != red or n not in issues:
        _say("the culprit file names issue %s for %s, not issue %s for %s; nothing pushed" % (
            " ".join(sorted(issues, key=int)) or "none", recorded, n, red))
        return 1
    pid = str(os.getpid())
    code, _ = _script("merge-lock.sh", "take", "--pid", pid)
    if code:
        return entry.refuse("taking the merge lock failed (exit %d); nothing pushed" % code, prefix="stack-fix: ")
    try:
        try:
            stack, onto, head = _checked(n, red)
        except Refused as refused:
            _say(str(refused))
            return 1
        except NoAnswer as no:
            _say(str(no))
            return 2
        _push(head, stack, onto)
    finally:
        released, _ = _script("merge-lock.sh", "release", "--pid", pid)
        if released:
            _say("releasing the merge lock failed (exit %d)" % released)
    sys.stdout.write(head + "\n")
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
