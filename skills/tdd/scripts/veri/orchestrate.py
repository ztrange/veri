"""orchestrate.sh's loop, run in-process."""
import os
import re
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    budget = os.environ.get("VERI_CONDUCTOR_CTX_BUDGET") or "120000"
    if not re.fullmatch(r"[0-9]+", budget):
        sys.stderr.write("orchestrate.sh: VERI_CONDUCTOR_CTX_BUDGET must be a whole number of tokens: %s\n" % budget)
        return 2
    while True:
        answer = subprocess.run([os.path.join(SCRIPTS, "solvable-issues.sh")], stdout=subprocess.PIPE)
        if answer.returncode == 3:
            return 0
        if answer.returncode != 0:
            sys.stderr.write("orchestrate.sh: solvable-issues.sh exited %d; no answer about the solvable set\n"
                             % answer.returncode)
            return 2
        issue = next((n for n in os.fsdecode(answer.stdout).rstrip("\n").split("\n") if not _parked(n)), "")
        if not issue:
            return 0
        conductor = subprocess.Popen([os.path.join(SCRIPTS, "run-conductor.sh"), issue], stdout=subprocess.PIPE)
        for _ in conductor.stdout:
            pass
        if _parked(issue):
            sys.stdout.write("parked %s\n" % issue)
            sys.stdout.flush()


def _parked(issue):
    return os.path.exists(os.path.join(".tdd", "parked", issue + ".md"))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
