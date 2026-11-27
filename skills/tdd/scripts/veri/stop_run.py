"""stop-run.sh's stop request, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import signal
import sys
import time

import entry
import paths
import pid_file
import run_dir
import stop_modes
import tunables

PREFIX = "stop-run: "
GONE = (ProcessLookupError, OverflowError)


def usage():
    return f"usage: stop-run.sh [--mode {'|'.join(stop_modes.STOP_MODES)}] <issue> | --all\n".encode()


# for entry's --help; a refusal calls usage() again, since a test swaps stop_modes.STOP_MODES at run time
USAGE = usage()


def complain(message):
    entry.refuse(message, prefix=PREFIX)


def nothing_to_do(message):
    complain(message)
    return 3


def holds(outer, inner):
    return inner == outer or inner.startswith(outer.rstrip(os.sep) + os.sep)


def inside_own_scripts():
    return paths.inside_scripts(__file__)


def on_one_path(main_tree):
    tree = os.path.realpath(os.fsdecode(main_tree))
    here = os.path.realpath(os.getcwd())
    return holds(tree, here) or holds(here, tree) or holds(tree + os.sep + ".git", linked_git_dir(here))


def linked_git_dir(here):
    while True:
        marker = os.path.join(here, ".git")
        if os.path.isfile(marker):
            with open(marker, "rb") as git_file:
                line = git_file.readline().strip()
            if not line.startswith(b"gitdir: "):
                return ""
            return os.path.realpath(os.path.join(here, os.fsdecode(line.removeprefix(b"gitdir: "))))
        if os.path.exists(marker) or os.path.dirname(here) == here:
            return ""
        here = os.path.dirname(here)


def stop_run(run, mode):
    with open(run_dir.run_file(run, "stop"), "w") as stop:
        stop.write(mode + "\n")
    sys.stdout.buffer.write(os.fsencode(run) + b"\n")
    if mode != "now":
        return 0
    killed = []
    refused = stop_leaves(run, killed)
    refused += [group for group in killed if outlives_kill(group)]
    for pid in refused:
        complain(f"cannot signal pid {pid} of run {run}")
    return 2 if refused else 0


def zombie(pid):
    return (pid_file.ps_field("stat", pid) or "").startswith("Z")


def group_alive(group):
    if zombie(group):
        return False
    try:
        os.killpg(group, 0)
    except GONE:
        return False
    except PermissionError:
        return True
    return True


def outlives_kill(group):
    for _ in range(10):
        if not group_alive(group):
            return False
        time.sleep(0.1)
    return True


def stop_leaves(run, killed=None):
    tdd = run_dir.run_file(run, "")
    termed = {}
    refused = []
    for entry in sorted(os.listdir(tdd)):  # noqa: F402 -- the import is unused in this function
        if entry.startswith(".") or not entry.endswith(".pid"):
            continue
        name = entry.removesuffix(".pid")
        if name == "conductor":
            continue
        pid = pid_file.number_in(tdd + entry)
        if pid is None:
            continue
        try:
            own = pid_file.supervising(pid, name)
            if not (own or pid_file.detached(pid)):
                continue
            if not pid_file.start_recorded(tdd + entry):
                complain(f"{tdd + entry} records no start time for pid {pid}; not signalled")
            elif pid_file.start_matches(tdd + entry, pid):
                if own:
                    os.kill(int(pid), signal.SIGTERM)
                else:
                    os.killpg(int(pid), signal.SIGTERM)
                    termed[int(pid)] = name
        except GONE:
            pass
        except PermissionError:
            refused.append(int(pid))
    if termed:
        time.sleep(float(tunables.get("VERI_STOP_KILL_GRACE", unless_empty=True)))
        for group in termed:
            if killed is not None:
                killed.append(group)
            try:
                os.killpg(group, signal.SIGKILL)
            except GONE:
                pass
            except PermissionError:
                if not zombie(group):
                    refused.append(group)
    return refused


def main(argv):
    mode = "at-ledger"
    issue = ""
    every = False
    args = iter(argv)
    for arg in args:
        if arg == "--mode":
            mode = next(args, None)
            if mode is None:
                return entry.refuse(f"--mode needs a value — {stop_modes.modes_named()}", prefix=PREFIX, usage=usage())
        elif arg == "--all":
            every = True
        else:
            issue = arg
    if not stop_modes.stop_mode_known(mode):
        return entry.refuse(f"unknown mode — want {stop_modes.modes_named()}: '{mode}'", prefix=PREFIX, usage=usage())
    if issue and every:
        return entry.refuse("name an issue or --all, not both", prefix=PREFIX, usage=usage())
    if not issue and not every:
        return entry.refuse("name an issue, or --all", prefix=PREFIX, usage=usage())
    if not every and not re.fullmatch(r"[1-9][0-9]*", issue):
        return entry.refuse(f"<issue> must be a positive integer: '{issue}'", prefix=PREFIX, usage=usage())
    if inside_own_scripts():
        return entry.refuse("type this from the repository whose runs you mean, not from the skill's own scripts"
                            " directory", prefix=PREFIX, usage=usage())
    try:
        main_tree = run_dir.main_tree()
    except run_dir.NoMainTree:
        main_tree = ""
    if not main_tree:
        return entry.refuse("no main working tree here — type this inside the repository", prefix=PREFIX, usage=usage())
    if not on_one_path(main_tree):
        return entry.refuse(f"the main working tree '{main_tree}' does not hold the directory this was typed from",
                            prefix=PREFIX, usage=usage())
    runs = run_dir.worktrees(main_tree) + "/"
    alive = pid_file.live_conductor if mode == "now" else pid_file.recorded_alive
    if every:
        stopped = 0
        failed = False
        try:
            names = os.listdir(runs)
        except FileNotFoundError:
            names = []
        for name in sorted(names):
            run = runs + name
            if not name.startswith(".") and alive(run) is not None:
                if stop_run(run, mode) == 2:
                    failed = True
                stopped += 1
        if not stopped:
            return nothing_to_do("no live run to stop")
        return 2 if failed else 0
    target = runs + issue
    if alive(target) is None:
        return nothing_to_do(f"no live run for issue {issue}")
    return stop_run(target, mode)


if __name__ == "__main__":
    os.chdir(tunables.get("VERI_CALLER_DIR", unless_empty=True))
    entry.run(main, sys.argv[1:])
