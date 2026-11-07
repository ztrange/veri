"""restart-conductor.sh's watch, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import subprocess
import sys
import time

import full_tier_time
import growth
import pid_file
import status
import stop_run as stop_run_module

USAGE = "usage: restart-conductor.sh <n>"


def _positive_int(text):
    return text.isascii() and text.isdigit() and int(text) >= 1


def _tdd_dir():
    return os.path.join(full_tier_time.main_tree(os.getcwd()), ".tdd")


def _run_dir(run):
    return os.path.join(_tdd_dir(), "wt", run)


def conductor_alive(run):
    return pid_file.live_conductor(_run_dir(run)) is not None


def stop_run(mode, run):
    stop_run_module.stop_run(_run_dir(run), mode)


def run_state(run):
    return json.loads(status.run_activity(_run_dir(run), as_json=True))["state"]


def detach_leaf(run):
    scripts = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(_tdd_dir(), f"conductor-{run}.log"), "a") as log:
        subprocess.Popen(
            [os.path.join(scripts, "detach-leaf.sh"), os.path.join(scripts, "run-conductor.sh"), run],
            stdout=log)


def _growth(run):
    try:
        with open(os.path.join(_tdd_dir(), f"conductor-{run}.log")) as f:
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
            pending = os.path.join(_run_dir(run), ".tdd", "restart-pending")
            os.makedirs(os.path.dirname(pending), exist_ok=True)
            with open(pending, "w") as f:
                f.write(f"{os.getpid()}\n")
            stop_run("at-ledger", run)
        sleep(5)
    if run_state(run) == "stopped":
        detach_leaf(run)
        with open(os.path.join(_run_dir(run), ".tdd", "events.jsonl"), "a") as f:
            f.write(json.dumps({"event": "conductor-restart", "growth": str(g), "knob": knob}) + "\n")
        os.remove(os.path.join(_run_dir(run), ".tdd", "restart-pending"))
    print(f"restarts {run} 0")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
