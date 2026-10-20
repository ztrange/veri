"""watch-runs.sh's computation, run in-process."""
import json
import os
import subprocess
import sys
import time

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


def solvable_issues():
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solvable-issues.sh")
    out = subprocess.run([script, "--not-running"], capture_output=True, text=True).stdout
    return [line.split()[0] for line in out.splitlines() if line.strip()]


def wait():
    time.sleep(2)


def clock():
    return time.monotonic()


def _whole_number(text):
    return text.isascii() and text.isdigit() and int(text) >= 1


def main(argv):
    if argv[:1] in (["--target"], ["--max-wait"]) and not (len(argv) > 1 and _whole_number(argv[1])):
        print("usage: watch-runs.sh [--target <N>] [--max-wait <seconds>]  (N, seconds: whole numbers >= 1)",
              file=sys.stderr)
        return 2
    target = int(argv[1]) if argv[:1] == ["--target"] else None
    max_wait = int(argv[1]) if argv[:1] == ["--max-wait"] else None
    started = live_conductors()
    deadline = clock() + max_wait if max_wait is not None else None
    while True:
        wait()
        live = live_conductors()
        if target is not None and len(live) < target:
            solvable = solvable_issues()
            if solvable:
                print("slot-free %d/%d next %s" % (len(live), target, solvable[0]))
                return 0
        for issue in started:
            if issue not in live:
                print("exited %s %s" % (issue, run_state(issue).split(" ")[0]))
                return 0
        if deadline is not None and clock() >= deadline:
            print("timeout")
            return 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
