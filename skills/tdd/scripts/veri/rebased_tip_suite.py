"""rebased-tip-suite.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import tunables
from wait_ci import trigger_lines

WORKFLOWS = ".github/workflows"


def triggers_on_pull_request():
    if not os.path.isdir(WORKFLOWS):
        return False
    for name in os.listdir(WORKFLOWS):
        with open(os.path.join(WORKFLOWS, name)) as workflow:
            if any("pull_request" in line for line in trigger_lines(workflow.read())):
                return True
    return False


def main(argv):
    if tunables.read("VERI_REBASED_TIP_SUITE"):
        mode, bad = tunables.resolve("VERI_REBASED_TIP_SUITE")
        if bad:
            print("rebased-tip-suite.sh: VERI_REBASED_TIP_SUITE '%s' is not %s" % bad, file=sys.stderr)
            return 2
        print(mode)
        return 0
    on_pr = tunables.read("VERI_CI_ON_PR")
    if on_pr not in ("", "0", "1"):
        print("rebased-tip-suite.sh: VERI_CI_ON_PR '%s' is not 0 or 1" % on_pr, file=sys.stderr)
        return 2
    if on_pr == "1" or not on_pr and triggers_on_pull_request():
        print("ci")
    else:
        print("local")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
