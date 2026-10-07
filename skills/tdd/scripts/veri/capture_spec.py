"""capture-spec.sh's spec, built in-process."""
import sys

try:
    from github import NoAnswer, gh_issue_view
except ImportError:
    from .github import NoAnswer, gh_issue_view

USAGE = "capture-spec: usage: capture-spec.sh <issue-number>"
BUG_HEADINGS = ("What happened", "Expected", "Steps to reproduce", "Environment")


def part(body, heading):
    want = "## " + heading
    inside = False
    lines = []
    for line in body.split("\n"):
        if line.startswith("## "):
            inside = line == want
        elif inside:
            lines.append(line + "\n")
    return "".join(lines)


def main(argv):
    if not argv or argv[0] == "":
        print(USAGE, file=sys.stderr)
        return 2
    n = argv[0]
    try:
        labels = gh_issue_view(n, "labels").rstrip("\n").split("\n")
        body = gh_issue_view(n, "body").rstrip("\n")
    except NoAnswer:
        return 2
    out = body + "\n"
    if "bug" in labels:
        out += "\n## Bug\n"
        for heading in BUG_HEADINGS:
            out += "\n### %s\n\n" % heading + part(body, heading)
    if "refactor" in labels:
        out += "\n## Refactor\n\nRun kind: refactor. This issue changes structure, not behaviour.\n"
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
