"""stack-pr.sh's logic, run in-process: the one open pull request from the stack branch to the default branch, whose
every push makes CI run on the stack's tip (PRD 034.2a)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry
import github
import stack_branch

USAGE = "usage: stack-pr.sh"
TITLE = "Stack %s: tracks it for CI against %s (never merged)"
BODY = ("This pull request tracks the stack branch `%s`, so CI runs on each push to it. It is never merged itself:"
        " slices are cut from it, each a pull request of its own ending at a tested commit that ends an issue, and"
        " those land on `%s`. Opened by veri's `stack-pr.sh`; a join reopens it when it is closed.")


def main(argv):
    if argv:
        return entry.refuse(usage=USAGE)
    stack, default, commits = stack_branch.ahead(".")
    if not commits:
        print("stack-pr: origin/%s is not ahead of origin/%s, or origin has no %s; nothing opened" % (
            stack, default, stack), file=sys.stderr)
        return 3
    pulls = github.stack_pulls(stack, default)
    if pulls:
        url = pulls[0].html_url
    else:
        url = github.pr_open(stack, default, TITLE % (stack, default), BODY % (stack, default))
    sys.stdout.write(url + "\n")
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
