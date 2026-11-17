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
    if argv:
        return entry.refuse(usage=USAGE)
    stack, _, _ = stack_branch.ahead(".")
    runs = github.workflow_runs(stack)
    answered = [found for found in runs if found[2] == "completed" and found[3] != "cancelled"]
    head, url, _, conclusion, _ = max(answered, key=lambda found: found[4])
    if conclusion in GREEN:
        return 3
    sys.stdout.write("%s %s %s\n" % (head, url, conclusion))
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
