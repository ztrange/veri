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
    rc = subprocess.run([os.path.join(SCRIPTS, "solvable-issues.sh")], stdout=subprocess.PIPE).returncode
    if rc == 3:
        return 0
    sys.stderr.write("orchestrate.sh: solvable-issues.sh exited %d; no answer about the solvable set\n" % rc)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
