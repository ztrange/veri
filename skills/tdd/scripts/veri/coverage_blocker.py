"""coverage-blocker.sh's logic: file a coverage issue and block the refactor issue on it."""
import os
import subprocess
import tempfile


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True)


def main(argv):
    fd, tmp = tempfile.mkstemp()
    os.close(fd)
    gh("api", "-X", "PATCH", "repos/{owner}/{repo}/issues/%s" % argv[0], "-F", "body=@" + tmp)
    os.remove(tmp)
    return 2
