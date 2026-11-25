"""restart-conductor.sh's watch, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import signal
import subprocess
import sys
import time

import entry
import event
import growth
import paths
import pid_file
import restart_marker
import run_dir
import run_pins
import run_activity
import stop_run as stop_run_module
import tunables

USAGE = "usage: restart-conductor.sh <n>"
LAUNCH_WAIT = 60


def _positive_int(text):
    return entry.whole_number(text) is not None


def _main_tree():
    return run_dir.main_tree_from_files(os.getcwd())


def _run_dir(run):
    return run_dir.worktree(_main_tree(), run)


def _run_file(run, name):
    return run_dir.run_file(_run_dir(run), name)


def _log_path(run):
    return run_dir.main_file(_main_tree(), f"conductor-{run}.log")


def conductor_alive(run):
    return pid_file.live_conductor(_run_dir(run)) is not None


def _process_live(run):
    root = _main_tree()
    return any(issue == run and pid_file.is_inside(pid_file.cwd_of(pid), root) for pid, issue in pid_file.conductors())


def stop_run(mode, run):
    stop_run_module.stop_run(_run_dir(run), mode)


def run_state(run):
    return run_activity.state(_run_dir(run))


def _launch_env(run):
    env = {k: v for k, v in tunables.environment().items() if not k.startswith("VERI_")}
    env.update(run_pins.launch_env(run, _main_tree()) or {})
    return env


def detach_leaf(run):
    scripts = paths.resolved_scripts_of(__file__)
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


def _clean_up_unstopped_exit(run, mark):
    restart_marker.clear(_run_dir(run))
    try:
        if _stop_mark(run) == mark:
            os.remove(_run_file(run, "stop"))
    except FileNotFoundError:
        pass


def main(argv):
    if not argv or not _positive_int(argv[0]):
        print(USAGE, file=sys.stderr)
        return 2
    knob = tunables.get("VERI_RESET_GROWTH_CONDUCTOR")
    if not _positive_int(knob):
        print(f"restart-conductor.sh: VERI_RESET_GROWTH_CONDUCTOR must be a whole number >= 1, got {knob!r}", file=sys.stderr)
        return 2
    run = argv[0]

    def on_signal(signum, frame):
        print(f"restart-conductor.sh: run {run} restarter exiting on {signal.Signals(signum).name}")
        sys.exit(2)

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, on_signal)
    if not conductor_alive(run) and not _new_conductor_appears(run):
        return 3
    restarts = 0
    offset = 0
    while True:
        asked = False
        foreign = False
        misses = 0
        reasons = []
        while misses < 3:
            if asked and _stop_mark(run) not in (None, mark):  # noqa: F821 -- set on an earlier pass, when asked
                foreign = True
            if not conductor_alive(run):
                misses += 1
                reasons.append(pid_file.not_live_reason(_run_dir(run)))
                if misses >= 3 and (reasons[-1] in ("parent command", "own command", "lstart unreadable")
                                    or (set(reasons) == {"pid file unreadable"} and _process_live(run))):
                    misses = 0
                sleep(1)
                continue
            misses = 0
            reasons = []
            try:
                g = _growth(run, offset)
            except OSError as e:
                print(f"restart-conductor.sh: cannot read conductor-{run}.log: {e}", file=sys.stderr)
                return 2
            if not asked and not foreign and g is not None and g >= 0.85 * int(knob):
                foreign = _stop_mark(run) is not None
                if not foreign:
                    restart_marker.claim(_run_dir(run), os.getpid())
                    stop_run("at-ledger", run)
                    asked = True
                    mark = _stop_mark(run)
            sleep(5)
        for reason in reasons:
            print(f"restart-conductor.sh: conductor read not-live: {reason}")
        unstopped = not asked or foreign or run_state(run) != "stopped"
        if asked and unstopped:
            _clean_up_unstopped_exit(run, mark)
        if unstopped:
            break
        offset = _log_size(run)
        detach_leaf(run)
        restarts += 1
        event.mark(_run_dir(run), event.context(tunables.environment()), "conductor-restart",
                   [f"growth={g}", f"knob={knob}"])
        appeared = _new_conductor_appears(run)
        restart_marker.clear(_run_dir(run))
        if not appeared:
            print(f"restart-conductor.sh: no conductor was recorded for run {run} within {LAUNCH_WAIT}s of its relaunch",
                  file=sys.stderr)
            return 2
    print(f"restarts {run} {restarts}")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
