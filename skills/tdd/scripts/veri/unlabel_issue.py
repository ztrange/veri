"""unlabel-issue.sh's logic, run in-process."""
import subprocess
import sys
import urllib.parse

import tunables


def main(argv):
    if len(argv) != 1:
        print("usage: unlabel-issue.sh <issue-number>", file=sys.stderr)
        return 2
    label = urllib.parse.quote(tunables.read("VERI_LABEL", "ready-for-agent"), safe="")
    run = subprocess.run(
        ["gh", "api", "-X", "DELETE", "repos/{owner}/{repo}/issues/%s/labels/%s" % (argv[0], label)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if run.returncode != 0 and "404" not in run.stderr:
        sys.stderr.write(run.stderr)
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
