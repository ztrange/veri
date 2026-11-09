"""pr-body.sh's body write, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import re
import sys

try:
    from veri import github
except ImportError:
    import github

BEGIN, END = "<!-- veri:run-body -->", "<!-- /veri:run-body -->"
USAGE = "usage: pr-body.sh <pr-number> <body-file>"


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    path = "repos/{owner}/{repo}/pulls/%s" % argv[0]
    read = github.gh_api(path)
    if read.returncode != 0:
        print("pr-body.sh: cannot read the body of PR #%s" % argv[0], file=sys.stderr)
        return 2
    current = json.loads(read.stdout)["body"] or ""
    with open(argv[1]) as f:
        mine = BEGIN + "\n" + f.read() + "\n" + END
    pattern = re.compile(re.escape(BEGIN) + ".*?" + re.escape(END), re.S)
    body, replaced = pattern.subn(lambda _: mine, current)
    if not replaced:
        body = mine
    write = github._gh("api", "-X", "PATCH", path, "-f", "body=" + body)
    if write.returncode != 0:
        print("pr-body.sh: cannot write the body of PR #%s" % argv[0], file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
