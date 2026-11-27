"""holds-step.sh's gate, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry
import git
import tick_ledger

USAGE = "usage: holds-step.sh <n> <step-start-sha> <id>…"


def main(argv):
    if len(argv) < 3:
        return entry.refuse(usage=USAGE)
    start = argv[1]
    if not git.ok("diff", "--quiet", start, "--"):
        return entry.refuse(f"holds-step.sh: the worktree differs from {start}: a tracked file changed; no case run")
    if git.out("status", "--porcelain", "--untracked-files=all"):
        return entry.refuse(f"holds-step.sh: the worktree differs from {start}: an untracked file is present; no case run")
    answers = [tick_ledger.run_case(case)[0] for case in argv[2:]]
    if 2 in answers:
        return entry.refuse("holds-step.sh: a named id ran no case: its test command collected nothing or could not run")
    return 1 if any(answers) else 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
