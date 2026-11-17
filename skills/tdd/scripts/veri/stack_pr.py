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


def tracking(stack, default):
    """The url of the one open pull request from <stack> to <default>, opened (ready) when none is. NoAnswer when
    GitHub gives none; two or more open is NoAnswer naming them all, since none of them is the one; an open one that
    is a draft, on which CI runs nothing, is NoAnswer naming it and saying it must be marked ready."""
    pulls = github.stack_pulls(stack, default)
    if len(pulls) > 1:
        raise github.NoAnswer("", "%d open pull requests track %s, so none is the one: %s" % (
            len(pulls), stack, " and ".join(str(p.html_url) for p in pulls)))
    if pulls:
        if pulls[0].draft is not False:
            raise github.NoAnswer("", "%s, the stack's tracking pull request, is a draft%s, and CI runs on no push to a"
                                  " draft: it must be marked ready (this script never changes it)" % (
                                      pulls[0].html_url, "" if pulls[0].draft else " (or does not say)"))
        return pulls[0].html_url
    return github.pr_open(stack, default, TITLE % (stack, default), BODY % (stack, default))


def main(argv):
    if argv:
        return entry.refuse(usage=USAGE)
    try:
        span = stack_branch.ahead(".")
    except stack_branch.Refused as refused:
        return entry.refuse(str(refused), prefix="stack-pr: ")
    if span is None:
        return 3
    stack, default, commits = span
    if not commits:
        print("stack-pr: origin/%s is not ahead of origin/%s, or origin has no %s; nothing opened" % (
            stack, default, stack), file=sys.stderr)
        return 3
    try:
        url = tracking(stack, default)
    except github.NoAnswer as no:
        return entry.refuse(" ".join(str(no.detail or no.answer).split()) + "; nothing opened", prefix="stack-pr: ")
    sys.stdout.write(url + "\n")
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
