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


def tdd_dir():
    return os.path.join(status.main_working_tree(), ".tdd")


def launch(issue):
    scripts = paths.scripts_of(__file__)
    log = os.path.join(tdd_dir(), f"conductor-{issue}.log")
    with open(log, "ab") as out:
        subprocess.Popen([os.path.join(scripts, "detach-leaf.sh"), os.path.join(scripts, "run-conductor.sh"), issue],
                         stdin=subprocess.DEVNULL, stdout=out, stderr=out)


def last_comment(issue):
    out = subprocess.run(["gh", "issue", "view", issue, "--json", "comments", "--jq", ".comments[-1].body"],
                         capture_output=True, text=True, check=True)
    return out.stdout


def main(argv):
    if not argv:
        sys.stderr.write(USAGE)
        return 2
    target = int(argv[1])
    previous = None
    seen = []
    while True:
        live = live_conductors()
        for issue in seen:
            if issue not in live:
                heading = last_comment(issue).splitlines()[0]
                if heading.startswith("### ⛔ Bailed"):
                    sys.stdout.write(f"bail {issue}\n")
                    return 0
                if not heading.startswith("### ✅ Done"):
                    sys.stdout.write(f"silent-exit {issue}\n")
                    return 0
                sys.stdout.write(f"done {issue} {heading.split()[-1]}\n")
                return 0
        seen = live
        ledger = previous and ledger_path(os.path.join(tdd_dir(), "wt", previous), previous)
        if len(live) < target and (previous is None or os.path.exists(ledger)):
            previous = solvable_issues()[0]
            launch(previous)
            with open(os.path.join(tdd_dir(), "dispatch.log"), "a") as log:
                log.write(f"launched {previous} {now()}\n")
        wait()


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
