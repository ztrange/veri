"""coverage-blocker.sh's logic: file a coverage issue and block the refactor issue on it."""
import os
import subprocess
import tempfile


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True)


def main(argv):
    gh("api", "repos/{owner}/{repo}/issues")
    body = gh("issue", "view", argv[0], "--json", "body", "-q", ".body").stdout
    fd, tmp = tempfile.mkstemp()
    with os.fdopen(fd, "w") as f:
        f.write(body.rstrip("\n") + "\n")
    gh("api", "-X", "PATCH", "repos/{owner}/{repo}/issues/%s" % argv[0], "-F", "body=@" + tmp)
    os.remove(tmp)
    return 2
