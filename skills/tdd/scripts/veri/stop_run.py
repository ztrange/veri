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


def stop_run(run, mode):
    with open(run + "/.tdd/stop", "w") as stop:
        stop.write(mode + "\n")
    sys.stdout.buffer.write(os.fsencode(run) + b"\n")


def main(argv):
    mode = "at-ledger"
    issue = ""
    every = False
    args = iter(argv)
    for arg in args:
        if arg == "--mode":
            mode = next(args, None)
            if mode is None:
                return refuse(f"--mode needs a value — {stop_modes.modes_named()}")
        elif arg == "--all":
            every = True
        else:
            issue = arg
    if not stop_modes.stop_mode_known(mode):
        return refuse(f"unknown mode — want {stop_modes.modes_named()}: '{mode}'")
    if issue and every:
        return refuse("name an issue or --all, not both")
    if not issue and not every:
        return refuse("name an issue, or --all")
    if not every and not re.fullmatch(r"[1-9][0-9]*", issue):
        return refuse(f"<issue> must be a positive integer: '{issue}'")
    runs = os.fsdecode(main_working_tree()) + "/.tdd/wt/"
    if every:
        stopped = 0
        for name in sorted(os.listdir(runs)):
            run = runs + name
            if not name.startswith(".") and pid_file.live_conductor(run) is not None:
                stop_run(run, mode)
                stopped += 1
        if not stopped:
            return nothing_to_do("no live run to stop")
        return 0
    target = runs + issue
    if pid_file.live_conductor(target) is None:
        return nothing_to_do(f"no live run for issue {issue}")
    stop_run(target, mode)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
