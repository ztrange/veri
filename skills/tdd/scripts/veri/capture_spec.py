"""capture-spec.sh's spec, built in-process."""
import subprocess
import sys

USAGE = "capture-spec: usage: capture-spec.sh <issue-number>"


def gh_issue_view(n, field):
    query = ".labels[].name" if field == "labels" else ".body"
    return subprocess.run(["gh", "issue", "view", n, "--json", field, "-q", query],
                          capture_output=True, text=True).stdout


def main(argv):
    if not argv or argv[0] == "":
        print(USAGE, file=sys.stderr)
        return 2
    n = argv[0]
    gh_issue_view(n, "labels")
    body = gh_issue_view(n, "body")
    print(body.rstrip("\n"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
