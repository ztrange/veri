"""stack-land.sh's logic, run in-process: lands the stack's tested cut on the default branch (PRD 034.4a)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import subprocess
import sys

import entry
import git
import github
import stack_branch
import stack_fix

USAGE = "usage: stack-land.sh [--now]"


def _pulls_onto(stack):
    """The urls of the open pull requests whose base is <stack>, kept only when the answer itself names <stack> as the
    base ref."""
    run = github.gh_api("repos/{owner}/{repo}/pulls?state=open&base=%s&per_page=100" % stack, stderr=subprocess.PIPE)
    return [raw.get("html_url") for raw in json.loads(run.stdout) if (raw.get("base") or {}).get("ref") == stack]


def main(argv):
    if argv not in ([], ["--now"]):
        return entry.refuse(usage=USAGE)
    size = os.environ.get("VERI_SLICE_COMMITS", "100")
    if not (size.isascii() and size.isdigit() and int(size) >= 1):
        return entry.refuse("VERI_SLICE_COMMITS must be a whole number of 1 or more: %r" % size, prefix="stack-land: ")
    try:
        stack = stack_branch.named(".")
    except stack_branch.Refused as refused:
        return entry.refuse("stack-branch.sh exits 2: %s" % refused, prefix="stack-land: ")
    if stack is None:
        return entry.refuse("stack-branch.sh exits 3: the repository's CLAUDE.md names no stack branch",
                            prefix="stack-land: ")
    code, said = stack_fix.script("stack-red.sh", limit=stack_fix.NETWORK)
    if code == 0:
        red, url = (said.split() + ["", ""])[:2]
        print("stack-land: the stack is red: CI failed on %s (%s); nothing cut or merged" % (red, url), file=sys.stderr)
        return 1
    if code == 2:
        return entry.refuse("stack-red.sh exits 2: no answer on the stack's CI; nothing cut or merged",
                            prefix="stack-land: ")
    code, said = stack_fix.script("stack-green.sh", limit=stack_fix.NETWORK)
    if code == 3:
        print("stack-land: stack-green.sh exits 3: no tested issue end to cut at; nothing to land", file=sys.stderr)
        return 3
    if code == 2:
        return entry.refuse("stack-green.sh exits 2: no answer on the stack's tested cut; nothing cut or merged",
                            prefix="stack-land: ")
    cut = said.split()[0]
    default = git.default_branch(cwd=".")
    ahead = int(git.out("rev-list", "--count", "origin/%s..%s" % (default, cut)))
    if argv != ["--now"] and ahead < int(size):
        live = _pulls_onto(stack)
        if live:
            print("stack-land: the cut %s is %d commits ahead of origin/%s, fewer than VERI_SLICE_COMMITS (%s), and the"
                  " stack is live: open pull requests onto %s: %s; nothing landed"
                  % (cut, ahead, default, size, stack, " ".join(live)), file=sys.stderr)
            return 3


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
