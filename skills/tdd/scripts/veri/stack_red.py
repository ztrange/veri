"""stack-red.sh's logic, run in-process: whether CI's latest answer on the stack branch is red, which freezes joins
(PRD 034.3a); during a GitHub outage, whether `.tdd/stack-local-red` freezes the local stack, read with no GitHub call
(PRD 033.2b)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import entry
import github
import run_dir
import stack_branch

USAGE = "usage: stack-red.sh"
LOCAL_RED = os.path.join(".tdd", "stack-local-red")
GREEN = ("success", "neutral", "skipped")


def run_id(run):
    """The id of a listed workflow run, the last part of its url."""
    return run[1].rsplit("/", 1)[1]


def _answer(run):
    """(conclusion, attempt): what a listed workflow run answers with, and the attempt that gave it. A run completed
    with a conclusion other than cancelled answers itself. One whose run_attempt is above 1 and that is not completed,
    or completed cancelled, answers from its earlier attempts, walked from n-1 down to 1: the first completed and not
    cancelled answers. None when it has no answer (attempt 1 not completed or cancelled, or every earlier attempt
    cancelled). github.NoAnswer when an earlier attempt cannot be read or reads not completed."""
    status, conclusion, attempt = run[2], run[3], run[5]
    if status == "completed" and conclusion != "cancelled":
        return conclusion, attempt
    for earlier in range(attempt - 1, 0, -1):
        status, conclusion = github.run_attempt(run_id(run), earlier)
        if status != "completed":
            raise github.NoAnswer("", "run %s attempt %d reads %r, not completed" % (run_id(run), earlier, status))
        if conclusion != "cancelled":
            return conclusion, earlier
    return None


def workflow_answer(runs):
    """(run, conclusion, attempt) answering for one workflow's <runs>, or None when none has answered yet: the newest
    run with an answer, except that while the newest run without one is still going, the newest answer on that run's
    own head wins over a newer one on another head. github.NoAnswer passes up."""
    pending, other = None, None
    for run in sorted(runs, key=lambda found: found[4], reverse=True):
        found = _answer(run)
        if found:
            if pending is None or run[0] == pending:
                return (run,) + found
            other = other or (run,) + found
        elif pending is None and other is None and run[2] != "completed":
            pending = run[0]
    return other


def by_workflow(runs):
    """{workflow id: its answer}, workflow_answer per workflow (listed run[6]); a github.NoAnswer it raised stands as
    that workflow's answer."""
    answers = {}
    for workflow in dict.fromkeys(run[6] for run in runs):
        try:
            answers[workflow] = workflow_answer([run for run in runs if run[6] == workflow])
        except github.NoAnswer as no:
            answers[workflow] = no
    return answers


def _local(clone):
    """During an outage, with no GitHub call: 0 printing `<sha> <path> local` when `.tdd/stack-local-red` exists in the
    main working tree <clone>, 3 when it does not, 2 when no stack is named or the file's first line is not a sha."""
    try:
        stack = stack_branch.named(".", remote=False)
    except stack_branch.Refused as refused:
        return entry.refuse(str(refused), prefix="stack-red: ")
    if not stack:
        return entry.refuse("the repository's CLAUDE.md names no stack branch (stack-branch.sh exits 3)",
                            prefix="stack-red: ")
    path = os.path.join(clone, LOCAL_RED)
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            first = f.readline().strip()
    except FileNotFoundError:
        print("stack-red: .tdd/github-outage exists and %s does not, so the local %s is not frozen; GitHub not read" % (
            LOCAL_RED, stack), file=sys.stderr)
        return 3
    except OSError as error:
        return entry.refuse("%s cannot be read (%s)" % (path, error), prefix="stack-red: ")
    if not re.fullmatch(r"[0-9a-f]{7,40}", first):
        return entry.refuse("%s's first line %r is not a commit sha" % (path, first[:80]), prefix="stack-red: ")
    sys.stdout.write("%s %s local\n" % (first, path))
    return 0


def main(argv):
    refused = entry.no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    try:
        clone = run_dir.main_tree_from_files()
    except OSError as error:
        return entry.refuse("the main working tree cannot be read (%s), so whether GitHub is out is not known" % error,
                            prefix="stack-red: ")
    if os.path.exists(os.path.join(clone, ".tdd", "github-outage")):
        return _local(clone)
    try:
        span = stack_branch.ahead(".")
    except stack_branch.Refused as refused:
        return entry.refuse(str(refused), prefix="stack-red: ")
    if span is None:
        return entry.refuse("the repository's CLAUDE.md names no stack branch (stack-branch.sh exits 3)",
                            prefix="stack-red: ")
    stack = span[0]
    try:
        runs = github.workflow_runs(stack)
    except github.NoAnswer as no:
        return entry.refuse(" ".join(str(no.detail or no.answer).split()), prefix="stack-red: ")
    answers = by_workflow(runs)
    red = [found for found in answers.values() if isinstance(found, tuple) and found[1] not in GREEN]
    if red:
        run, conclusion, _ = max(red, key=lambda found: found[0][4])
        sys.stdout.write("%s %s %s\n" % (run[0], run[1], conclusion))
        return 0
    lost = [found for found in answers.values() if isinstance(found, github.NoAnswer)]
    if lost:
        return entry.refuse("%s; no answer from %d of %d workflows" % (
            " ".join(str(lost[0].detail or lost[0].answer).split()), len(lost), len(answers)), prefix="stack-red: ")
    green = [found for found in answers.values() if found]
    if not green:
        print("stack-red: CI has not answered on origin/%s yet: none of the %d workflow runs read completed with a"
              " conclusion other than cancelled" % (stack, len(runs)), file=sys.stderr)
        return 3
    print("stack-red: CI's latest answer on origin/%s is %s in each of its %d workflows, not red" % (
        stack, "/".join(sorted({found[1] for found in green})), len(green)), file=sys.stderr)
    return 3


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
