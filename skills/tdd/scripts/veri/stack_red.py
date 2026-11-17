"""stack-red.sh's logic, run in-process: whether CI's latest answer on the stack branch is red, which freezes joins
(PRD 034.3a)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry
import github
import stack_branch

USAGE = "usage: stack-red.sh"
GREEN = ("success", "neutral", "skipped")


def main(argv):
    refused = entry.no_arguments(argv, USAGE)
    if refused is not None:
        return refused
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
    answered = [found for found in runs if found[2] == "completed" and found[3] != "cancelled"]
    if not answered:
        print("stack-red: CI has not answered on origin/%s yet: none of the %d workflow runs read completed with a"
              " conclusion other than cancelled" % (stack, len(runs)), file=sys.stderr)
        return 3
    head, url, _, conclusion, _ = max(answered, key=lambda found: found[4])
    if conclusion in GREEN:
        print("stack-red: CI's latest answer on origin/%s is %s (%s), not red" % (stack, conclusion, head),
              file=sys.stderr)
        return 3
    sys.stdout.write("%s %s %s\n" % (head, url, conclusion))
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
