"""watch-runs.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import subprocess
import sys
import time

import paths
import pid_file
import status


def _runs():
    _, document = status.json_document(read_states=False)
    return json.loads(document)["runs"]


def _starting():
    return pid_file.starting_runs(status.main_working_tree())


def live_conductors():
    live = [str(run["issue"]) for run in _runs() if run.get("state") == "running"]
    return live + [issue for issue in dict.fromkeys(_starting()) if issue not in live]


def run_state(issue):
    for run in _runs():
        if str(run["issue"]) == issue:
            return run.get("state", "")
    return ""


class QueueUnreadable(Exception):
    pass


def solvable_issues():
    script = os.path.join(paths.scripts_of(__file__), "veri", "..", "solvable-issues.sh")
    done = subprocess.run([script, "--not-running"], capture_output=True, text=True)
    if done.returncode != 0:
        raise QueueUnreadable(done.stderr)
    return [line.split()[0] for line in done.stdout.splitlines() if line.strip()]


_pause = 2


def wait():
    time.sleep(_pause)


def clock():
    return time.monotonic()


def _whole_number(text):
    return text.isascii() and text.isdigit() and int(text) >= 1


def main(argv):
    given = {}
    for i in range(0, len(argv), 2):
        flag, value = argv[i], argv[i + 1:i + 2]
        if flag not in ("--target", "--max-wait") or flag in given or not (value and _whole_number(value[0])):
            print("usage: watch-runs.sh [--target <N>] [--max-wait <seconds>]  (N, seconds: whole numbers >= 1)",
                  file=sys.stderr)
            return 2
        given[flag] = int(value[0])
    target = given.get("--target")
    max_wait = given.get("--max-wait")
    started = live_conductors()
    if not given and not started:
        print("nothing to watch")
        return 3
    global _pause
    _pause = 2 if max_wait is None else min(2, max_wait)
    deadline = clock() + max_wait if max_wait is not None else None
    missed = set()
    while True:
        wait()
        live = live_conductors()
        if target is not None and len(live) < target:
            try:
                solvable = solvable_issues()
            except QueueUnreadable as failure:
                sys.stderr.write(str(failure))
                return 2
            if solvable:
                print("slot-free %d/%d next %s" % (len(live), target, solvable[0]))
                return 0
        missed &= set(started) - set(live)
        for issue in started:
            if issue not in live:
                state = run_state(issue).split(" ")[0]
                if not state:
                    if pid_file.recorded_started(os.path.join(status.main_working_tree(), ".tdd", "wt", issue)):
                        continue
                    if issue in pid_file.conductor_processes():
                        continue
                    if issue not in missed:
                        missed.add(issue)
                        continue
                    print("vanished %s" % issue)
                    return 2
                print("exited %s %s" % (issue, state))
                return 0
        if deadline is not None and clock() >= deadline:
            print("timeout")
            return 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
