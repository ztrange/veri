"""stop-run.sh's stop request, run in-process."""
import os
import re
import subprocess
import sys

import pid_file
import stop_modes


def usage():
    return f"usage: stop-run.sh [--mode {'|'.join(stop_modes.STOP_MODES)}] <issue> | --all\n".encode()


def refuse(message):
    sys.stderr.buffer.write(os.fsencode("stop-run: " + message) + b"\n" + usage())
    return 2


def nothing_to_do(message):
    sys.stderr.buffer.write(os.fsencode("stop-run: " + message) + b"\n")
    return 3


def main_working_tree():
    git = subprocess.run(["git", "worktree", "list", "--porcelain"],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    first = git.stdout.split(b"\n", 1)[0]
    return first.removeprefix(b"worktree ")


def main(argv):
    mode = "at-ledger"
    issue = ""
    args = iter(argv)
    for arg in args:
        if arg == "--mode":
            mode = next(args)
        else:
            issue = arg
    if not issue:
        return refuse("name an issue, or --all")
    if not re.fullmatch(r"[1-9][0-9]*", issue):
        return refuse(f"<issue> must be a positive integer: '{issue}'")
    target = os.fsdecode(main_working_tree()) + "/.tdd/wt/" + issue
    if pid_file.live_conductor(target) is None:
        return nothing_to_do(f"no live run for issue {issue}")
    with open(target + "/.tdd/stop", "w") as stop:
        stop.write(mode + "\n")
    sys.stdout.buffer.write(os.fsencode(target) + b"\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
