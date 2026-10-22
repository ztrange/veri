"""watch-runs.sh's computation, run in-process."""
import json
import os
import subprocess
import sys
import time

import paths
import status


def _runs():
    _, document = status.json_document()
    return json.loads(document)["runs"]


def live_conductors():
    return [str(run["issue"]) for run in _runs() if run.get("state") == "running"]


def run_state(issue):
    for run in _runs():
        if str(run["issue"]) == issue:
            return run.get("state", "")
    return ""


class QueueUnreadable(Exception):
    pass


def solvable_issues():
    script = os.path.join(paths.scripts_of(__file__), "solvable-issues.sh")
    done = subprocess.run([script, "--not-running"], capture_output=True, text=True)
    if done.returncode != 0:
        raise QueueUnreadable(done.stderr)
    return [line.split()[0] for line in done.stdout.splitlines() if line.strip()]


def wait():
    time.sleep(2)


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
    deadline = clock() + max_wait if max_wait is not None else None
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
        for issue in started:
            if issue not in live:
                state = run_state(issue).split(" ")[0]
                if not state:
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
