"""classify-bail.sh's classification, run in-process."""
import os
import sys

USAGE = "usage: classify-bail.sh <cause>"

CATEGORIES = {
    **dict.fromkeys(
        ("killed-stuck", "no-verdict", "reconcile-failed", "ci-timeout", "ci-conflict"), "system"),
    **dict.fromkeys(
        ("revise-exhausted", "untestable-criterion", "step-too-big", "rebase-unresolved",
         "uncovered", "ci-red", "suite-red", "rebased-tip-red"), "process"),
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
    sys.exit(main(sys.argv[1:]))
