"""stack-pr.sh's logic, run in-process: the one open pull request from the stack branch to the default branch, whose
every push makes CI run on the stack's tip (PRD 034.2a)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry
import github
import stack_branch

USAGE = "usage: stack-pr.sh"
TITLE = "Stack %s: tracks it for CI against %s (never merged)"


def main(argv):
    if argv:
        return entry.refuse(usage=USAGE)
    stack, default, commits = stack_branch.ahead(".")
    pulls = github.stack_pulls(stack, default)
    if pulls:
        url = pulls[0].html_url
    else:
        url = github.pr_open(stack, default, TITLE % (stack, default), "")
    sys.stdout.write(url + "\n")
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
