"""capture-spec.sh's spec, built in-process."""
import json
import subprocess
import sys

USAGE = "capture-spec: usage: capture-spec.sh <issue-number>"
BUG_HEADINGS = ("What happened", "Expected", "Steps to reproduce", "Environment")


class NoAnswer(Exception):
    pass


def gh_issue_view(n, field):
    query = ".labels[].name" if field == "labels" else ".body"
    view = subprocess.run(["gh", "issue", "view", n, "--json", field, "-q", query],
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if view.returncode == 0:
        return view.stdout.rstrip("\n")
    rest = subprocess.run(["gh", "api", "repos/{owner}/{repo}/issues/%s" % n],
                          stdout=subprocess.PIPE, text=True)
    try:
        issue = json.loads(rest.stdout)
    except json.JSONDecodeError as error:
        print("json.decoder.JSONDecodeError: %s" % error, file=sys.stderr)
        raise NoAnswer
    if rest.returncode != 0:
        raise NoAnswer
    if field == "labels":
        return "\n".join(label["name"] for label in issue["labels"])
    return (issue["body"] or "").rstrip("\n")


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
        labels = gh_issue_view(n, "labels").split("\n")
        body = gh_issue_view(n, "body")
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
