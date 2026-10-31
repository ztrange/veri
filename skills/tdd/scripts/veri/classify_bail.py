"""classify-bail.sh's classification, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

USAGE = "usage: classify-bail.sh <cause>"

CATEGORIES = {
    **dict.fromkeys(
        ("killed-stuck", "killed-external", "report-missing", "no-verdict", "reconcile-failed", "ci-timeout",
         "ci-conflict", "step-add-refused", "replaces-report-failed", "criterion-unreadable", "setup-failed",
         "preflight-refused", "pr-ready-failed"), "system"),
    **dict.fromkeys(
        ("revise-exhausted", "revise-impossible", "untestable-criterion", "step-too-big", "rebase-unresolved",
         "uncovered", "ci-red", "suite-red", "rebased-tip-red", "unreplaced-cases", "needs-user", "step-added-off-route",
         "fixture-owed", "missing-reroutes-exhausted", "graded-edit-outside-skill-edit"),"process"),
}


def main(argv):
    cause = argv[0] if argv else ""
    category = CATEGORIES.get(cause)
    if category is None:
        sys.stderr.buffer.write(os.fsencode("classify-bail: unknown cause: %s\n%s\n" % (cause, USAGE)))
        return 2
    sys.stdout.write(category + "\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
