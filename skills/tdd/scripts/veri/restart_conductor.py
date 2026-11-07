"""restart-conductor.sh's watch, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import sys
import time

import full_tier_time
import growth
import stop_run as stop_run_module

USAGE = "usage: restart-conductor.sh <n>"


def _positive_int(text):
    return text.isascii() and text.isdigit() and int(text) >= 1


def conductor_alive(run):
    return False


def stop_run(mode, run):
    stop_run_module.stop_run(os.path.join(full_tier_time.main_tree(os.getcwd()), ".tdd", "wt", run), mode)


def run_state(run):
    return ""


def detach_leaf(run):
    pass


def _growth(run):
    try:
        with open(os.path.join(full_tier_time.main_tree(os.getcwd()), ".tdd", f"conductor-{run}.log")) as f:
            records = [json.loads(line) for line in f]
    except OSError:
        return None
    return growth.growth(records)


def sleep(seconds):
    time.sleep(seconds)


def main(argv):
    if not argv or not _positive_int(argv[0]):
        print(USAGE, file=sys.stderr)
        return 2
    knob = os.environ.get("VERI_RESET_GROWTH_CONDUCTOR", "70000")
    if not _positive_int(knob):
        print(f"restart-conductor.sh: VERI_RESET_GROWTH_CONDUCTOR must be a whole number >= 1, got {knob!r}", file=sys.stderr)
        return 2
    run = argv[0]
    if not conductor_alive(run):
        return 3
    while conductor_alive(run):
        g = _growth(run)
        if g is not None and g >= 0.85 * int(knob):
            pending = os.path.join(full_tier_time.main_tree(os.getcwd()), ".tdd", "wt", run, ".tdd", "restart-pending")
            os.makedirs(os.path.dirname(pending), exist_ok=True)
            with open(pending, "w") as f:
                f.write(f"{os.getpid()}\n")
            stop_run("at-ledger", run)
        sleep(5)
    if run_state(run) == "stopped":
        detach_leaf(run)
    print(f"restarts {run} 0")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
