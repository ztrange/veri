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


def main(argv):
    if len(argv) != 1:
        return entry.refuse(usage=USAGE)
    red = argv[0]
    stack, _, _ = stack_branch.ahead(".")
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
    _add_worktree(path, red)
    try:
        _checkout(path, red)
        for case in cases:
            _run_alone(path, command, case)
    finally:
        _remove_worktree(path)
    return 3


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
