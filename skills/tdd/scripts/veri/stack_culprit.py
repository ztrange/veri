"""stack-culprit.sh's logic, run in-process: the issue whose end turned the stack red, found by running the cases CI
named red alone at each issue end, oldest first, in a detached worktree of its own (PRD 034.3b)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import ci_flake
import detect_test_command
import entry
import git
import github
import rerun_alone
import stack_branch
import stack_green

USAGE = "usage: stack-culprit.sh <red-sha>"
MAX_CASES = 5  # the cases run alone at each issue end; ci-flake.sh bounds its alone runs the same way


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
    return git.git("-C", path, "checkout", "--detach", "--force", commit, capture_output=True, text=True).returncode == 0


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
                               stdin=__import__("subprocess").DEVNULL, stdout=__import__("subprocess").PIPE,
                               stderr=__import__("subprocess").STDOUT, text=True)
    if isinstance(ran, github.TimedOut) or not 0 <= ran.returncode < 128:
        return None, ran.stdout or ""
    return ran.returncode, ran.stdout or ""


def _first_fail(output, path):
    """The first line of an alone run's <output> holding FAIL, stripped, with <path> written `<worktree>` and the home
    directory `~`, since it is published; `(no FAIL line)` when none holds it."""
    line = next((line.strip() for line in output.splitlines() if "FAIL" in line), "(no FAIL line)")
    return line.replace(path, "<worktree>").replace(os.path.expanduser("~"), "~")


def _owners(subjects):
    """Per subject, oldest first, the issues its commit belongs to by KT5's subject rule: those it names, else those of
    the nearest earlier subject naming any (none when no earlier one does)."""
    owners, owner = [], frozenset()
    for subject in subjects:
        owner = frozenset(stack_green.named(subject)) or owner
        owners.append(owner)
    return owners


def _tested_base(span):
    """The index in <span> of the newest commit stack-green.sh's rule calls tested (a KT5 issue end whose check runs
    all passed), its newest ENDS_READ such ends read, one read each; -1 (origin/<default>) when none of them is.
    Older ends past that bound are not read."""
    ends = [at for at, end in enumerate(stack_green.issue_ends([subject for _, subject in span])) if end][::-1]
    for at in ends[:stack_green.ENDS_READ]:
        if stack_green.tested(github.check_runs(span[at][0])):
            return at
    return -1


def main(argv):
    if len(argv) != 1:
        return entry.refuse(usage=USAGE)
    red = argv[0]
    stack, default, commits = stack_branch.ahead(".")
    span = commits[:[commit for commit, _ in commits].index(red) + 1]
    base, owners = _tested_base(span), _owners([subject for _, subject in span])
    ends = [at for at in range(base + 1, len(span)) if at == len(span) - 1 or owners[at + 1] != owners[at]]
    runs = [found for found in github.workflow_runs(stack)
            if found[0] == red and found[2] == "completed" and found[3] != "cancelled"]
    url = max(runs, key=lambda found: found[4])[1]
    cases = rerun_alone.named_targets(ci_flake.runner_text(github.run_failed_log(url.rsplit("/", 1)[1])))
    if len(cases) > MAX_CASES:
        print("stack-culprit: the log names %d cases; the first %d are run, %d not run" % (
            len(cases), MAX_CASES, len(cases) - MAX_CASES), file=sys.stderr)
    cases = cases[:MAX_CASES]
    top = _top()
    path = os.path.join(top, ".tdd", "stack-culprit-%d" % os.getpid())
    command = _one_file_command(top)
    if not _add_worktree(path, red):
        return entry.refuse("git worktree add --detach %s failed; nothing run, and never in this checkout" % path,
                            prefix="stack-culprit: ")
    try:
        before = span[base][0] if base >= 0 else "origin/" + default
        for at in ends:
            commit = span[at][0]
            _checkout(path, commit)
            red_here = []
            for case in cases:
                if not _has(path, commit, case.split("::", 1)[0]):
                    continue
                code, output = _run_alone(path, command, case)
                if code is None or code not in (0, 1, 4, 5):
                    return entry.refuse("%s run alone at %s gave no answer (%s)" % (
                        case, commit, "no exit within VERI_TIMEOUT" if code is None else "exit %d" % code),
                        prefix="stack-culprit: ")
                if code == 1:
                    red_here.append((case, _first_fail(output, path)))
            if red_here:
                issues = " ".join(sorted(owners[at], key=int)) or "none"
                sys.stdout.write("red: %s\nissue: %s\ncommit: %s\nbefore: %s\n%s" % (
                    red, issues, commit, before, "".join("case: %s\t%s\n" % found for found in red_here)))
                return 0
            before = commit
    finally:
        _remove_worktree(path)
    return 3


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
