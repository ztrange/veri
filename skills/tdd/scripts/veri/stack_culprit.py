"""stack-culprit.sh's logic, run in-process: the issue whose end turned the stack red, found by running the cases CI
named red alone at each issue end, oldest first, in a detached worktree of its own (PRD 034.3b)."""
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
import rerun_alone
import stack_branch
import stack_green
import stack_red

USAGE = "usage: stack-culprit.sh <red-sha>"
MAX_CASES = 5  # the cases run alone at each issue end; ci-flake.sh bounds its alone runs the same way
MAX_ENDS = 20  # the issue ends one search tests; with more it runs nothing, since each end costs MAX_CASES alone runs


def _top():
    """The working tree the script was run in: its worktree is made under that tree's `.tdd/`."""
    return git.out("rev-parse", "--show-toplevel")


def _one_file_command(root):
    """The repository's `veri: one test file:` command, as detect-test-command.sh --tier "one test file" reads it in
    <root>; None when it declares none."""
    found = detect_test_command.resolved("one test file", None, root)
    return os.fsdecode(found) if found else None


def _add_worktree(path, commit):
    """Whether `git worktree add --detach <path> <commit>` made the worktree."""
    return git.git("worktree", "add", "--detach", path, commit, capture_output=True, text=True).returncode == 0


def _checkout(path, commit):
    """Whether <path>, this script's own worktree, now has <commit> checked out, detached."""
    return git.git("-C", path, "checkout", "--detach", "--force", commit,
                   capture_output=True, text=True).returncode == 0


def _remove_worktree(path):
    """Whether `git worktree remove --force <path>` removed this script's own worktree."""
    return git.git("worktree", "remove", "--force", path, capture_output=True, text=True).returncode == 0


def _has(path, commit, name):
    """Whether <commit> holds the file <name>."""
    return git.git("-C", path, "cat-file", "-e", "%s:%s" % (commit, name), capture_output=True).returncode == 0


def _run_alone(path, command, target):
    """<target> run alone through <command> in <path>: (exit code, output), the code None when the run gave no answer
    (not done within VERI_TIMEOUT, its process group killed, or killed by a signal)."""
    cmd = command if '"$1"' in command else command + ' "$1"'
    ran = github.bounded_group(["sh", "-c", cmd, "sh", target], limit_name="VERI_TIMEOUT", cwd=path,
                               stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True)
    if isinstance(ran, github.TimedOut) or not 0 <= ran.returncode < 128:
        return None, ran.stdout or ""
    return ran.returncode, ran.stdout or ""


ABSENT = "absent"
ABSENT_OUTPUT = re.compile(r"^ERROR: not found: |\bno tests ran\b|^collected 0 items", re.M)


def verdict(code, output, case):
    """What an alone run of <case> says: True red (it exited non-zero and its output carries a failure line naming
    <case>, read as ci-flake.sh reads one), False not red (it exited 0), ABSENT not red because the output says the
    case was not found or not collected, None no answer (any other ending, a kill or a timeout). The exit code alone
    never decides: a make wrapper exits 2 for a failing case and a missing one alike."""
    if code is None:
        return None
    if code == 0:
        return False
    text = ci_flake.ANSI.sub("", output)
    if case in rerun_alone.named_targets(text):
        return True
    return ABSENT if ABSENT_OUTPUT.search(text) else None


def _first_fail(output, path, case):
    """The first failure line of an alone run's <output> naming <case> (else the first holding FAIL), stripped, with
    <path> written `<worktree>` and the home directory `~`, since it is published; `(no FAIL line)` when none is."""
    lines = [line.strip() for line in ci_flake.ANSI.sub("", output).splitlines()]
    line = next((line for line in lines if line.startswith(("FAILED " + case, "ERROR " + case))),
                next((line for line in lines if "FAIL" in line), "(no FAIL line)"))
    return line.replace(path, "<worktree>").replace(os.path.expanduser("~"), "~")


def owners(subjects):
    """Per subject, oldest first, the issues its commit belongs to by KT5's subject rule: those it names, else those of
    the nearest earlier subject naming any (none when no earlier one does)."""
    found, owner = [], frozenset()
    for subject in subjects:
        owner = frozenset(stack_green.named(subject)) or owner
        found.append(owner)
    return found


def _tested_base(span):
    """The index in <span> of the newest commit stack-green.sh's rule calls tested (a KT5 issue end whose check runs
    all passed), its newest ENDS_READ such ends read, one read each; -1 (origin/<default>) when none of them is.
    Older ends past that bound are not read."""
    ends = [at for at, end in enumerate(stack_green.issue_ends([subject for _, subject in span])) if end][::-1]
    for at in ends[:stack_green.ENDS_READ]:
        if stack_green.tested(github.check_runs(span[at][0])):
            return at
    return -1


class _NoAnswer(Exception):
    """No answer to start the search from (exit 2); str() says why."""


def _search_inputs(red):
    """(stack, default, span, run url, cases): the stack and default branch, origin/<default>..<red> as [(sha,
    subject)] oldest first, the url of the red run on <red> (each workflow's answer on <red> read as stack-red.sh reads
    one, the newest red one taken) and the cases the failed log of its answering attempt names. _NoAnswer,
    stack_branch.Refused or github.NoAnswer when any of them cannot be had."""
    found = stack_branch.ahead(".")
    if found is None:
        raise _NoAnswer("the repository's CLAUDE.md names no stack branch (stack-branch.sh exits 3)")
    stack, default, commits = found
    shas = [commit for commit, _ in commits]
    if red not in shas:
        raise _NoAnswer("%s is not a commit of origin/%s..origin/%s" % (red, default, stack))
    answers = stack_red.by_workflow([run for run in github.workflow_runs(stack) if run[0] == red])
    red_runs = [found for found in answers.values() if isinstance(found, tuple) and found[1] not in stack_red.GREEN]
    if not red_runs:
        lost = [found for found in answers.values() if isinstance(found, github.NoAnswer)]
        if lost:
            raise lost[0]
        raise _NoAnswer("no workflow's answer on %s is red among the runs GitHub lists for %s (%d workflows read):"
                        " there is no red log to read" % (red, stack, len(answers)))
    run, _, attempt = max(red_runs, key=lambda found: found[0][4])
    url = run[1]
    try:
        cases = rerun_alone.named_targets(ci_flake.runner_text(github.run_failed_log(stack_red.run_id(run), attempt)))
    except ValueError as unread:
        raise _NoAnswer("the failed log of %s cannot be read: %s" % (url, unread)) from None
    if not cases:
        raise _NoAnswer("the failed log of %s names no case" % url)
    return stack, default, commits[:shas.index(red) + 1], url, cases


def _search(path, command, ends, before, red, cases):
    """Run <cases> alone at each of <ends> [(sha, owners)], oldest first, in the worktree <path>: the answer to print at
    the first end where a case is red, None when none is. _NoAnswer for a checkout that fails, an alone run with no
    answer, or a case absent at <red> itself. <before> is the commit the first end follows."""
    for commit, issues in ends:
        if not _checkout(path, commit):
            raise _NoAnswer("checking out %s in the search's own worktree failed; nothing more run" % commit)
        red_here = []
        for case in cases:
            if not _has(path, commit, case.split("::", 1)[0]):
                said, code, output = ABSENT, None, ""
            else:
                code, output = _run_alone(path, command, case)
                said = verdict(code, output, case)
            if said == ABSENT and commit == red:
                raise _NoAnswer("%s is absent at %s itself, where CI named it red: the CI id and the local"
                                " one-test-file command disagree" % (case, red))
            if said is None:
                raise _NoAnswer("%s run alone at %s gave no answer (%s, and its output names no failure of it and"
                                " does not say it was not found)" % (
                                    case, commit, "no exit within VERI_TIMEOUT" if code is None else "exit %d" % code))
            if said is True:
                red_here.append((case, _first_fail(output, path, case)))
        if red_here:
            return "red: %s\nissue: %s\ncommit: %s\nbefore: %s\n%s" % (
                red, " ".join(sorted(issues, key=int)) or "none", commit, before,
                "".join("case: %s\t%s\n" % found for found in red_here))
        before = commit
    return None


def _comment(stack, default, body):
    """Add <body> as a comment on the stack's one open tracking pull request, unless a trusted comment there
    (github.trusted_comment) already holds exactly <body> as github.published posts it: a stranger's copy never stops
    it. With none open, or several, nothing is posted and stderr says so. NoAnswer from GitHub passes up."""
    pulls = github.stack_pulls(stack, default)
    if len(pulls) != 1:
        print("stack-culprit: %d open pull requests track %s; no comment posted" % (len(pulls), stack), file=sys.stderr)
        return
    number = pulls[0].number
    if any(comment.get("body") == github.published(body) and github.trusted_comment(comment)
           for comment in github.issue_comments(number)):
        return
    github.gh_comment_post(number, github.published(body))


def main(argv):
    if len(argv) != 1:
        return entry.refuse(usage=USAGE)
    red = argv[0]
    if not re.fullmatch(r"[0-9a-f]{40}", red):
        return entry.refuse("<red-sha> must be a full 40-hex commit sha, got %r" % red[:80], usage=USAGE)
    try:
        stack, default, span, url, cases = _search_inputs(red)
        base = _tested_base(span)
    except (stack_branch.Refused, github.NoAnswer, _NoAnswer) as no:
        said = no.detail or no.answer if isinstance(no, github.NoAnswer) else str(no)
        return entry.refuse(" ".join(str(said).split()), prefix="stack-culprit: ")
    owned = owners([subject for _, subject in span])
    ends = [at for at in range(base + 1, len(span)) if at == len(span) - 1 or owned[at + 1] != owned[at]]
    if len(ends) > MAX_ENDS:
        return entry.refuse("%d issue ends from %s to %s are untested, more than %d the search runs; nothing run" % (
            len(ends), span[base][0] if base >= 0 else "origin/" + default, red, MAX_ENDS), prefix="stack-culprit: ")
    if len(cases) > MAX_CASES:
        print("stack-culprit: the log names %d cases; the first %d are run, %d not run" % (
            len(cases), MAX_CASES, len(cases) - MAX_CASES), file=sys.stderr)
    cases = cases[:MAX_CASES]
    top = _top()
    path = os.path.join(top, ".tdd", "stack-culprit-%d" % os.getpid())
    command = _one_file_command(top)
    if not command:
        return entry.refuse("the repository declares no `veri: one test file:` command (detect-test-command.sh --tier"
                            " \"one test file\"); nothing run", prefix="stack-culprit: ")
    if not _add_worktree(path, red):
        return entry.refuse("git worktree add --detach %s failed; nothing run, and never in this checkout" % path,
                            prefix="stack-culprit: ")
    since = span[base][0] if base >= 0 else "origin/" + default
    try:
        printed = _search(path, command, [(span[at][0], owned[at]) for at in ends], since, red, cases)
    except _NoAnswer as no:
        return entry.refuse(str(no), prefix="stack-culprit: ")
    finally:
        if not _remove_worktree(path):
            print("stack-culprit: git worktree remove --force %s failed; the search's own worktree is left there"
                  % path, file=sys.stderr)
    if printed:
        sys.stdout.write(printed)
        answer = printed
    else:
        answer = "no issue end from %s to %s turns a case red; cases run: %s\n" % (since, red, ", ".join(cases))
        print("stack-culprit: " + answer.rstrip("\n"), file=sys.stderr)
    try:
        _comment(stack, default, "stack-culprit: %s\n\n%s\nRed run: %s\n" % (red, answer, url))
    except github.NoAnswer as no:
        return entry.refuse("the answer was not commented on the tracking pull request: %s" % " ".join(
            str(no.detail or no.answer).split()), prefix="stack-culprit: ")
    return 0 if printed else 3


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
