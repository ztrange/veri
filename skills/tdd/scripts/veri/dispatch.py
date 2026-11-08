"""dispatch.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

import paths
import status
import watch_runs

USAGE = "usage: dispatch.sh --target <N>\n"


solvable_issues = watch_runs.solvable_issues
wait = watch_runs.wait


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
    while True:
        launch(solvable_issues()[0])
        wait()


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
