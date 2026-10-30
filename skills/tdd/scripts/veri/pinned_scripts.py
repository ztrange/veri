"""pinned-scripts.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import subprocess
import sys

USAGE = "usage: pinned-scripts.sh <issue-number>\n"


def main_working_tree():
    listed = subprocess.run(["git", "worktree", "list", "--porcelain"], capture_output=True, text=True).stdout
    return listed.split("\n", 1)[0].removeprefix("worktree ")


def recorded_pin(main_tree, issue):
    try:
        with open(os.path.join(main_tree, ".tdd", "issue-%s-skill-commit" % issue)) as record:
            return record.read().strip()
    except OSError:
        return ""


def main(argv):
    if len(argv) != 1 or not re.fullmatch(r"[0-9]+", argv[0]):
        sys.stderr.write(USAGE)
        return 2
    issue = argv[0]
    main_tree = main_working_tree()
    kept = os.path.join(main_tree, ".tdd", "wt", issue, ".tdd", "pinned-scripts")
    if os.path.isdir(kept):
        sys.stdout.write(kept + "\n")
        return 0
    pin = recorded_pin(main_tree, issue)
    if pin:
        sys.stderr.write("pinned-scripts.sh: run %s's pinned scripts are gone; its pin is %s. Recover them, never the "
                         "installed copy: git archive %s skills/tdd/scripts\n" % (issue, pin, pin))
    else:
        sys.stderr.write("pinned-scripts.sh: run %s has no pinned scripts, and no pin is recorded\n" % issue)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
