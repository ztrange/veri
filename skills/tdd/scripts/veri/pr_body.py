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
    current = json.loads(github.gh_api(path).stdout)["body"]
    with open(argv[1]) as f:
        mine = BEGIN + "\n" + f.read() + "\n" + END
    body = re.sub(re.escape(BEGIN) + ".*?" + re.escape(END), lambda _: mine, current, flags=re.S)
    github._gh("api", "-X", "PATCH", path, "-f", "body=" + body)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
