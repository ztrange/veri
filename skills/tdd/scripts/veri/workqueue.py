"""workqueue.sh's subcommands, run in-process."""
import subprocess
import sys

USAGE = """workqueue.sh: usage: workqueue.sh assign <worker> <issue>...
                     workqueue.sh next <worker>
                     workqueue.sh start <worker> <issue>
                     workqueue.sh done <worker> <issue> <merge-sha>
                     workqueue.sh park <worker> <issue> <reason>
                     workqueue.sh show [<worker>]
"""


def refuse(message=None):
    if message is not None:
        sys.stderr.write(message + "\n")
    sys.stderr.write(USAGE)
    return 2


def main_working_tree():
    listing = subprocess.run(["git", "worktree", "list", "--porcelain"],
                             capture_output=True, text=True).stdout
    first = listing.split("\n", 1)[0]
    return first.removeprefix("worktree ")


def main(argv):
    command = argv[0] if argv else ""
    if command == "next":
        return 3
    if command == "done" and not "".join(argv[3:4]):
        return refuse()
    if command == "start":
        queue = main_working_tree() + "/.tdd/workqueue"
        with open(queue) as lines:
            for line in lines:
                if line.split("\t")[:3] == [argv[1], argv[2], "queued"]:
                    break
            else:
                sys.stderr.write("workqueue.sh: %s holds no queued item for issue %s\n" % (argv[1], argv[2]))
                return 1
    if command != "assign":
        return refuse("workqueue.sh: unknown subcommand: " + command)
    named = set()
    for issue in argv[2:]:
        if issue in named:
            return refuse("workqueue.sh: issue %s is named twice" % issue)
        named.add(issue)
