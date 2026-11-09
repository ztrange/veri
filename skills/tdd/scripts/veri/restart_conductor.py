"""restart-conductor.sh's watch, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import subprocess
import sys
import time

import event
import full_tier_time
import growth
import pid_file
import status
import stop_run as stop_run_module
import tunables

USAGE = "usage: restart-conductor.sh <n>"
LAUNCH_WAIT = 60


def _positive_int(text):
    return text.isascii() and text.isdigit() and int(text) >= 1


def _tdd_dir():
    return os.path.join(full_tier_time.main_tree(os.getcwd()), ".tdd")


def _run_dir(run):
    return os.path.join(_tdd_dir(), "wt", run)


def _run_file(run, name):
    return os.path.join(_run_dir(run), ".tdd", name)


def _log_path(run):
    return os.path.join(_tdd_dir(), f"conductor-{run}.log")


def conductor_alive(run):
    return pid_file.live_conductor(_run_dir(run)) is not None


def stop_run(mode, run):
    stop_run_module.stop_run(_run_dir(run), mode)


def run_state(run):
    return json.loads(status.run_activity(_run_dir(run), as_json=True))["state"]


def _launch_env(run):
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    try:
        with open(os.path.join(_tdd_dir(), f"issue-{run}-launch-env")) as record:
            for line in record:
                key, sep, value = line.rstrip("\n").partition("=")
                if sep:
                    env[key] = value
    except FileNotFoundError:
        pass
    return env


def detach_leaf(run):
    scripts = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = _launch_env(run)
    with open(_log_path(run), "a") as log:
        subprocess.Popen(
            [os.path.join(scripts, "detach-leaf.sh"), os.path.join(scripts, "run-conductor.sh"), run],
            stdout=log, env=env)


def _log_size(run):
    return os.path.getsize(_log_path(run))


def _growth(run, offset=0):
    try:
        with open(_log_path(run)) as f:
            f.seek(offset)
            records = []
            for line in f:
                try:
                    records.append(json.loads(line))
                except ValueError:
                    continue
    except FileNotFoundError:
        return None
    return growth.growth(records)


def _stop_mark(run):
    try:
        return os.stat(_run_file(run, "stop")).st_mtime_ns
    except FileNotFoundError:
        return None


def sleep(seconds):
    time.sleep(seconds)


def _new_conductor_appears(run):
    """The old conductor is dead, so any live one is the new launch; its pid file may lag the launch."""
    for _ in range(LAUNCH_WAIT):
        if conductor_alive(run):
            return True
        sleep(1)
    return conductor_alive(run)


def main(argv):
    if not argv or not _positive_int(argv[0]):
        print(USAGE, file=sys.stderr)
        return 2
    knob = tunables.read("VERI_RESET_GROWTH_CONDUCTOR", "70000")
    if not _positive_int(knob):
        print(f"restart-conductor.sh: VERI_RESET_GROWTH_CONDUCTOR must be a whole number >= 1, got {knob!r}", file=sys.stderr)
        return 2
    run = argv[0]
    if not conductor_alive(run) and not _new_conductor_appears(run):
        return 3
    restarts = 0
    offset = 0
    while True:
        asked = False
        misses = 0
        while misses < 3:
            if not conductor_alive(run):
                misses += 1
                sleep(1)
                continue
            misses = 0
            try:
                g = _growth(run, offset)
            except OSError as e:
                print(f"restart-conductor.sh: cannot read conductor-{run}.log: {e}", file=sys.stderr)
                return 2
            if not asked and g is not None and g >= 0.85 * int(knob):
                pending = _run_file(run, "restart-pending")
                os.makedirs(os.path.dirname(pending), exist_ok=True)
                with open(pending, "w") as f:
                    f.write(f"{os.getpid()}\n")
                stop_run("at-ledger", run)
                asked = True
                mark = _stop_mark(run)
            sleep(5)
        if not asked or run_state(run) != "stopped":
            if asked:
                os.remove(_run_file(run, "restart-pending"))
                try:
                    if _stop_mark(run) == mark:
                        os.remove(_run_file(run, "stop"))
                except FileNotFoundError:
                    pass
            break
        offset = _log_size(run)
        detach_leaf(run)
        restarts += 1
        event.mark(_run_dir(run), event.context(tunables.environment()), "conductor-restart",
                   [f"growth={g}", f"knob={knob}"])
        appeared = _new_conductor_appears(run)
        os.remove(_run_file(run, "restart-pending"))
        if not appeared:
            print(f"restart-conductor.sh: no conductor was recorded for run {run} within {LAUNCH_WAIT}s of its relaunch",
                  file=sys.stderr)
            return 2
    print(f"restarts {run} {restarts}")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
