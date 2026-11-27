"""stack-fix.sh's logic, run in-process: pushes a fix worktree's reviewed hand fix on top of a red stack, once per
culprit, after checking its bounds and running the cases stack-culprit.sh named (PRD 034.3c)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import subprocess
import sys

import ci_flake
import detect_test_command
import entry
import git
import github
import paths
import stack_branch
import stack_culprit
import stack_green

USAGE = "usage: stack-fix.sh <n> <red-sha> <culprit-file>"
SCRIPTS = paths.resolved_scripts_of(__file__)
NETWORK = "VERI_GIT_NETWORK_TIMEOUT"


class NoAnswer(Exception):
    """No answer from git, GitHub or a script (exit 2); str() says why."""


class Refused(Exception):
    """A bound the fix does not hold (exit 1); str() says which."""


class NotRed(Exception):
    """stack-red.sh exits 3: nothing to fix (exit 3)."""


def script(name, *args, limit=None):
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


def log(rev_range):
    """The commits of <rev_range>, oldest first, as [(sha, subject, [each Stack-fix trailer value])]. NoAnswer when git
    refuses the log."""
    found = git.git("log", "--reverse",
                    "--format=%H%x1f%s%x1f%(trailers:key=" + TRAILER + ",valueonly,separator=%x1f)%x1e",
                    rev_range, capture_output=True, text=True)
    if found.returncode:
        raise NoAnswer("git log %s failed (exit %d): %s"
                       % (rev_range, found.returncode, " ".join(found.stderr.split())[:200]))
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


def _run(command, target=None, cwd=None):
    """<command> run in <cwd> (default: the current directory) under VERI_TIMEOUT, <target> passed as "$1" (the alone
    run of a case) when given: (exit code, output), the code None when the run gave no answer (no exit within
    VERI_TIMEOUT, its process group killed, or killed by a signal)."""
    if target is not None and '"$1"' not in command:
        command += ' "$1"'
    ran = github.bounded_group(["sh", "-c", command, "sh", *([target] if target is not None else [])],
                               limit_name="VERI_TIMEOUT", cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
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


def _origin_now(stack):
    """After a push that did not answer 0: origin's <stack> as a fresh fetch reads it ("" when origin has none).
    NoAnswer when the fetch gets no answer."""
    if git.network("fetch", "--prune", "origin").returncode:
        raise NoAnswer("the push did not answer 0 and a fetch of origin got no answer, so whether it landed is not"
                       " known")
    return _rev("refs/remotes/origin/" + stack)


def _push(head, stack, onto):
    """Push <head> to <stack> on origin as a compare-and-swap leased to <onto>, the stack as fetched: its exit code
    (a TimedOut answers 124)."""
    return git.network("push", "--force-with-lease=refs/heads/%s:%s" % (stack, onto), "origin",
                       "%s:refs/heads/%s" % (head, stack)).returncode


def _say(message):
    print("stack-fix: " + message, file=sys.stderr)


def _checked(n, red):
    """The checks of the stack and the fix's commits, with the lock held: (stack, default, onto, head). Refused or
    NoAnswer when one fails; NotRed when stack-red.sh exits 3."""
    code, said = script("stack-red.sh", limit=NETWORK)
    if code == 3:
        raise NotRed("stack-red.sh exits 3: the stack is not red; nothing pushed")
    if code != 0:
        raise NoAnswer("stack-red.sh exited %d, so whether the stack is red is not known; nothing pushed" % code)
    now = (said.split() or [""])[0]
    if now != red:
        raise Refused("%s is not the commit red now: stack-red.sh prints %s; nothing pushed" % (red, now))
    try:
        found = stack_branch.ahead(".")
    except stack_branch.Refused as refused:
        raise NoAnswer(str(refused)) from None
    if found is None:
        raise NoAnswer("the repository's CLAUDE.md names no stack branch (stack-branch.sh exits 3)")
    stack, default, _ = found
    onto, head = _rev("refs/remotes/origin/" + stack), _rev("HEAD")
    if not onto or not head:
        raise NoAnswer("%s does not resolve after the fetch; nothing pushed" % (
            "origin/" + stack if not onto else "the fix worktree's HEAD"))
    for commit, subject, trailers in log("refs/remotes/origin/%s..refs/remotes/origin/%s" % (default, stack)):
        if trailers and n in stack_green.named(subject):
            raise Refused("%s (%s) on origin/%s already carries a %s: trailer for issue %s: one fix per culprit;"
                          " nothing pushed" % (commit, subject, stack, TRAILER, n))
    _bounds(n, red, stack, onto, head)
    return stack, default, onto, head


def _bounds(n, red, stack, onto, head):
    """The fix's commits: origin/<stack> as fetched (<onto>) is an ancestor of <head>, and each commit of
    <onto>..<head> ends its subject `(#<n>)` and carries `Stack-fix: <red>`. Refused, or NoAnswer from git."""
    descends = _ancestor(onto, head)
    if descends is None:
        raise NoAnswer("git merge-base --is-ancestor gave no answer; nothing pushed")
    if not descends:
        raise Refused("origin/%s at %s is not an ancestor of HEAD %s: the fix must sit on the stack's tip, and the push"
                      " is a fast-forward only; nothing pushed" % (stack, onto, head))
    commits = log("%s..%s" % (onto, head))
    if not commits:
        raise Refused("HEAD adds no commit to origin/%s: there is no fix to push" % stack)
    for commit, subject, trailers in commits:
        if not subject.endswith("(#%s)" % n) or red not in trailers:
            raise Refused("the fix commit %s (%s) %s; every fix commit ends its subject (#%s) and carries %s: %s;"
                          " nothing pushed" % (commit, subject, "lacks the trailer %s: %s" % (TRAILER, red)
                                               if subject.endswith("(#%s)" % n)
                                               else "does not end its subject (#%s)" % n,
                                               n, TRAILER, red))


TEST_DIRS = ("test", "tests", "spec", "__tests__")
TEST_NAME_PARTS = ("_test.", ".test.", ".spec.")


def test_file(path, case_files):
    """Whether <path> is a test file: one of <case_files> (the files of the cases the culprit file names), or a path
    with a directory named test, tests, spec or __tests__, or a file name that starts `test_` or holds `_test.`,
    `.test.` or `.spec.`."""
    *dirs, name = path.split("/")
    return (path in case_files or any(part in TEST_DIRS for part in dirs) or name.startswith("test_")
            or any(part in name for part in TEST_NAME_PARTS))


def _no_test_moved(onto, head, cases):
    """Refused naming the first test file `git diff --name-status <onto>..<head>` lists, added, changed, deleted or
    renamed (either side of a rename); NoAnswer from git."""
    case_files = {case.split("::", 1)[0] for case in cases}
    for status, *names in _changed("%s..%s" % (onto, head)):
        for path in names:
            if test_file(path, case_files):
                raise Refused("the fix touches the test file %s (%s): it may edit no test file; nothing pushed" % (
                    path, status))


def _alone(code, output, case):
    """What an alone run of <case> that exited <code> with <output> says: "green" (exit 0, its output not saying the
    case was not found or not collected), "absent" (the output says so, whatever the exit), "red" (a failure line naming
    it, read as stack-culprit.sh reads one, or an exit 1, 4 or 5), None no answer (no exit, or any other exit)."""
    if code is None:
        return None
    if code == 0:
        return "absent" if stack_culprit.ABSENT_OUTPUT.search(ci_flake.ANSI.sub("", output)) else "green"
    said = stack_culprit.verdict(code, output, case)
    if said == stack_culprit.ABSENT:
        return "absent"
    return "red" if said is True or code in (1, 4, 5) else None


def _cases_pass(top, cases):
    """Each of <cases> run alone at HEAD in <top> through the repository's `veri: one test file:` command. Refused
    naming the first that is red or absent (its file missing at HEAD, or not found or not collected); NoAnswer naming
    one whose run gave no answer, or when no such command is declared. The exit code alone never passes a case."""
    command = _one_file_command(top)
    if not command:
        raise NoAnswer("the repository declares no `veri: one test file:` command (detect-test-command.sh --tier"
                       " \"one test file\"), so the named cases cannot be run; nothing pushed")
    for case in cases:
        if not _has(case.split("::", 1)[0]):
            raise Refused("%s: its file is absent at HEAD, and a case gone is not a pass; nothing pushed" % case)
        code, output = _run(command, case, cwd=top)
        said = _alone(code, output, case)
        if said in ("red", "absent"):
            raise Refused("%s is still %s at HEAD run alone (exit %d); nothing pushed" % (
                case, "red" if said == "red" else "absent or not collected", code))
        if said is None:
            raise NoAnswer("%s run alone at HEAD gave no answer (%s); nothing pushed" % (
                case, "no exit within VERI_TIMEOUT" if code is None else "exit %d, its output naming no failure of it"
                % code))


def tier_and_prose(top, say):
    """The fast tier and prose-owed.sh, run at HEAD in <top>: Refused on a red fast tier (any non-zero exit) or
    prose-owed.sh exit 1 (a unit owes a grade); NoAnswer when no fast tier command is found, the fast tier gives no
    exit within VERI_TIMEOUT, or prose-owed.sh exits otherwise. <say> ends each message."""
    fast = _fast_command(top)
    if not fast:
        raise NoAnswer("no fast tier command is found (detect-test-command.sh --tier fast); %s" % say)
    code, _ = _run(fast, cwd=top)
    if code is None:
        raise NoAnswer("the fast tier (%s) gave no exit within VERI_TIMEOUT; %s" % (fast, say))
    if code:
        raise Refused("the fast tier (%s) is red at HEAD, exit %d; %s" % (fast, code, say))
    owed, _ = script("prose-owed.sh", top)
    if owed == 1:
        raise Refused("prose-owed.sh exits 1 at HEAD: a unit owes a grade; %s" % say)
    if owed:
        raise NoAnswer("prose-owed.sh exited %d at HEAD; %s" % (owed, say))


def pushed(head, stack, onto):
    """Push <head> to <stack>, leased to <onto> and a fast-forward of it (its descent checked before): returns when
    origin's stack is <head>, read back after a push that did not answer 0 (one that timed out may have landed).
    Refused when origin's stack moved to another commit; NoAnswer when it still reads <onto> or cannot be read."""
    if _push(head, stack, onto) == 0:
        return
    now = _origin_now(stack)
    if now == head:
        return
    if now == onto:
        raise NoAnswer("the push of %s to %s was refused or gave no answer, and origin's %s did not move; nothing"
                       " pushed" % (head, stack, stack))
    raise Refused("origin's %s moved since the fetch (now %s, fetched at %s); nothing pushed, nothing forced" % (
        stack, now or "deleted", onto))


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
    code, _ = script("merge-lock.sh", "take", "--pid", pid)
    if code:
        return entry.refuse("taking the merge lock failed (exit %d); nothing pushed" % code, prefix="stack-fix: ")
    try:
        stack, default, onto, head = _checked(n, red)
        _no_test_moved(onto, head, cases)
        if _dirty().strip():
            raise Refused("the fix worktree has uncommitted changes, so a run there would not test HEAD; nothing"
                          " pushed")
        top = _top()
        _cases_pass(top, cases)
        tier_and_prose(top, "nothing pushed")
        if _rev("HEAD") != head or _dirty().strip():
            raise NoAnswer("the alone runs, the fast tier or prose-owed.sh changed the fix worktree (HEAD or its files)"
                           " since %s was checked; nothing pushed" % head)
        pushed(head, stack, onto)
    except (Refused, NoAnswer, NotRed) as stopped:
        _say(str(stopped))
        return {Refused: 1, NoAnswer: 2, NotRed: 3}[type(stopped)]
    finally:
        released, _ = script("merge-lock.sh", "release", "--pid", pid)
        if released:
            _say("releasing the merge lock failed (exit %d)" % released)
    sys.stdout.write(head + "\n")
    body = ("stack-fix: the hand fix for issue %s is pushed on %s at %s, on top of the red commit %s."
            "\n\nCases fixed:\n%s") % (
        n, stack, head, red, "".join("- %s\n" % case for case in cases))
    comment(stack, default, n, body, "stack-fix")
    return 0


def comment(stack, default, issue, body, name):
    """Add <body> once to the stack's one open tracking pull request and once to issue <issue>, after a push: a
    tracking pull request it cannot tell (none open, or several) or a comment that fails is said on stderr, prefixed
    <name>, and never changes the exit, since the push already landed."""
    try:
        pulls = github.stack_pulls(stack, default)
    except github.NoAnswer as no:
        pulls = None
        print("%s: the tracking pull request could not be read (%s); no comment posted there" % (
            name, " ".join(str(no.detail or no.answer).split())[:200]), file=sys.stderr)
    targets = []
    if pulls is not None and len(pulls) != 1:
        print("%s: %d open pull requests track %s; no comment posted there" % (name, len(pulls), stack),
              file=sys.stderr)
    elif pulls:
        targets.append(pulls[0].number)
    for number in targets + [int(issue)]:
        try:
            github.gh_comment_post(number, github.published(body))
        except github.NoAnswer as no:
            print("%s: the comment on #%s failed (%s); the push stands" % (
                name, number, " ".join(str(no.detail or no.answer).split())[:200]), file=sys.stderr)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
