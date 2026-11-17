"""capture-spec.sh's spec, built in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

from github import NoAnswer, gh_issue_view

USAGE = "capture-spec: usage: capture-spec.sh <issue-number>"
BUG_HEADINGS = ("What happened", "Expected", "Steps to reproduce", "Environment")
BOTH_KINDS = "capture-spec: issue %s is labelled both `legacy` and `refactor`; a run has one kind"


class TwoKinds(Exception):
    pass


def capture(n):
    labels = gh_issue_view(n, "labels").rstrip("\n").split("\n")
    if "legacy" in labels and "refactor" in labels:
        raise TwoKinds(BOTH_KINDS % n)
    body = gh_issue_view(n, "body").rstrip("\n")
    out = body + "\n"
    if "bug" in labels:
        out += "\n## Bug\n\n"
        for heading in BUG_HEADINGS:
            out += "- %s\n" % heading
    if "refactor" in labels:
        out += "\n## Refactor\n\nRun kind: refactor. This issue changes structure, not behaviour.\n"
    if "legacy" in labels:
        out += "\n## Legacy\n\nRun kind: legacy. Each step names a region and the seam that drives it (LEGACY.md).\n"
    return out


def main(argv):
    if not argv or argv[0] == "":
        print(USAGE, file=sys.stderr)
        return 2
    try:
        out = capture(argv[0])
    except NoAnswer:
        return 2
    except TwoKinds as refusal:
        print(refusal, file=sys.stderr)
        return 2
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
