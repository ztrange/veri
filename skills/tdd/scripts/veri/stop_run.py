"""stop-run.sh's stop request, run in-process."""
import os
import re
import signal
import subprocess
import sys

import pid_file
import stop_modes


def usage():
    return f"usage: stop-run.sh [--mode {'|'.join(stop_modes.STOP_MODES)}] <issue> | --all\n".encode()


def complain(message):
    sys.stderr.buffer.write(os.fsencode("stop-run: " + message) + b"\n")


def refuse(message):
    complain(message)
    sys.stderr.buffer.write(usage())
    return 2


def nothing_to_do(message):
    complain(message)
    return 3


def main_working_tree():
    try:
        git = subprocess.run(["git", "worktree", "list", "--porcelain"],
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return b""
    first = git.stdout.split(b"\n", 1)[0]
    return first.removeprefix(b"worktree ")


def stop_run(run, mode):
    with open(run + "/.tdd/stop", "w") as stop:
        stop.write(mode + "\n")
    sys.stdout.buffer.write(os.fsencode(run) + b"\n")
    if mode == "now":
        stop_leaves(run)


def stop_leaves(run):
    tdd = run + "/.tdd/"
    for entry in sorted(os.listdir(tdd)):
        if entry.startswith(".") or not entry.endswith(".pid"):
            continue
        name = entry.removesuffix(".pid")
        if name == "conductor":
            continue
        pid = pid_file.number_in(tdd + entry)
        if pid is None or not pid_file.supervising(pid, name):
            continue
        try:
            os.kill(int(pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError, OverflowError):
            pass


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
    main_tree = main_working_tree()
    if not main_tree:
        return refuse("no main working tree here — type this inside the repository")
    runs = os.fsdecode(main_tree) + "/.tdd/wt/"
    if every:
        stopped = 0
        try:
            names = os.listdir(runs)
        except FileNotFoundError:
            names = []
        for name in sorted(names):
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
    os.chdir(os.environ.get("VERI_CALLER_DIR") or ".")
    sys.exit(main(sys.argv[1:]))
