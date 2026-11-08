"""dispatch.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys
from datetime import datetime

import paths
import status
import watch_runs
from ledger import ledger_path

USAGE = "usage: dispatch.sh --target <N>\n"


solvable_issues = watch_runs.solvable_issues
wait = watch_runs.wait
live_conductors = watch_runs.live_conductors


def now():
    return datetime.now().isoformat(timespec="seconds")


def launch(issue):
    scripts = paths.scripts_of(__file__)
    log = os.path.join(status.main_working_tree(), ".tdd", f"conductor-{issue}.log")
    with open(log, "ab") as out:
        subprocess.Popen([os.path.join(scripts, "detach-leaf.sh"), os.path.join(scripts, "run-conductor.sh"), issue],
                         stdin=subprocess.DEVNULL, stdout=out, stderr=out)


def main(argv):
    if not argv:
        sys.stderr.write(USAGE)
        return 2
    target = int(argv[1])
    previous = None
    while True:
        ledger = previous and ledger_path(os.path.join(status.main_working_tree(), ".tdd", "wt", previous), previous)
        if len(live_conductors()) < target and (previous is None or os.path.exists(ledger)):
            previous = solvable_issues()[0]
            launch(previous)
            with open(os.path.join(status.main_working_tree(), ".tdd", "dispatch.log"), "a") as log:
                log.write(f"launched {previous} {now()}\n")
        wait()


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
