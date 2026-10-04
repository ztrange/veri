"""coverage-blocker.sh's logic: file a coverage issue and block the refactor issue on it."""
import os
import subprocess
import sys
import tempfile

USAGE = "usage: coverage-blocker.sh <refactor-issue-number>"


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True)


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    if gh("api", "repos/{owner}/{repo}/issues").returncode != 0:
        return 2
    body = gh("issue", "view", argv[0], "--json", "body", "-q", ".body").stdout
    fd, tmp = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as f:
            f.write(body.rstrip("\n") + "\n")
        gh("api", "-X", "PATCH", "repos/{owner}/{repo}/issues/%s" % argv[0], "-F", "body=@" + tmp)
    finally:
        os.remove(tmp)
    return 2
