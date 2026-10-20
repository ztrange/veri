"""watch-runs.sh's computation, run in-process."""
import json
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


def wait():
    time.sleep(2)


def main(argv):
    started = live_conductors()
    while True:
        wait()
        live = live_conductors()
        for issue in started:
            if issue not in live:
                print("exited %s %s" % (issue, run_state(issue).split(" ")[0]))
                return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
