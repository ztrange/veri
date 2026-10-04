"""coverage-blocker.sh's logic: file a coverage issue and block the refactor issue on it."""
import json
import os
import subprocess
import sys
import tempfile

USAGE = "usage: coverage-blocker.sh <refactor-issue-number>"


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True)


def read_body(number):
    view = gh("issue", "view", number, "--json", "body", "-q", ".body")
    if view.returncode == 0:
        return view.stdout
    return json.loads(gh("api", "repos/{owner}/{repo}/issues/%s" % number).stdout)["body"] or ""


def block(body, new):
    return "\n".join("- #" + new if line.startswith("None") else line for line in body.split("\n"))


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    create = gh("api", "repos/{owner}/{repo}/issues")
    if create.returncode != 0:
        return 2
    new = create.stdout.rsplit("/", 1)[-1]
    body = block(read_body(argv[0]), new)
    fd, tmp = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as f:
            f.write(body.rstrip("\n") + "\n")
        edit = gh("api", "-X", "PATCH", "repos/{owner}/{repo}/issues/%s" % argv[0], "-F", "body=@" + tmp)
    finally:
        os.remove(tmp)
    return 0 if edit.returncode == 0 else 2
