"""The shape rebased-tip-suite.sh and branch-suite.sh share: print `ci` or `local`, an explicit knob first, else whether CI runs on pull requests."""
import sys

import ci_on_pr
import tunables


def run(script, variable):
    if tunables.read(variable):
        mode, bad = tunables.resolve(variable)
        if bad:
            print("%s: %s '%s' is not %s" % ((script, variable) + bad), file=sys.stderr)
            return 2
        print(mode)
        return 0
    try:
        on_pr = ci_on_pr.runs_on_pull_requests()
    except ValueError as refusal:
        print("%s: %s" % (script, refusal), file=sys.stderr)
        return 2
    print("ci" if on_pr else "local")
    return 0
