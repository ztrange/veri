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


def main(argv):
    target = int(argv[1]) if argv[:1] == ["--target"] else None
    started = live_conductors()
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


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
