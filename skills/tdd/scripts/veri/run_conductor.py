"""run-conductor.sh's launch of one conductor, run in-process."""
import os
import subprocess
import sys

import launch_floor
from git import symref_default

USAGE = "usage: run-conductor.sh <issue>"


def main(argv):
    if launch_floor.bash_refusal("run-conductor") or launch_floor.python_refusal("run-conductor"):
        return 2
    if not argv or not argv[0]:
        sys.stderr.write(USAGE + "\n")
        return 2
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    head_rev = "HEAD"
    if git(base, "remote", "get-url", "origin",
           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        fetches = 0
        while True:
            fetch = git(base, "fetch", "-q", "origin",
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            fetches += 1
            if fetch.returncode == 0:
                break
            sys.stderr.write(fetch.stderr.rstrip("\n") + "\n")
            if "cannot lock ref" in fetch.stderr and fetches < 60:
                if subprocess.run(["sleep", os.environ.get("VERI_FETCH_RETRY_SLEEP") or "1"]).returncode != 0:
                    return 1
                continue
            sys.stderr.write("run-conductor: fetch of origin failed in '%s' — refusing to run a skill that may be stale\n" % base)
            return 2
        head_rev = "refs/remotes/origin/HEAD"
        if not verifies(base, head_rev):
            answer = git(base, "ls-remote", "--symref", "origin", "HEAD",
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            if answer.returncode != 0:
                return 2
            default = symref_default(answer.stdout)
            if not default:
                return refuse_unpinned(base, "origin names no default branch")
            head_rev = "refs/remotes/origin/" + default
            if not verifies(base, head_rev):
                return refuse_unpinned(base, "origin's default branch '%s' has no %s" % (default, head_rev))
    git(base, "rev-parse", head_rev,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return 0


def verifies(base, ref):
    return git(base, "rev-parse", "-q", "--verify", ref, stdout=subprocess.DEVNULL).returncode == 0


def git(base, *args, **kwargs):
    return subprocess.run(["git", "-C", base] + list(args), **kwargs)


def refuse_unpinned(base, why):
    sys.stderr.write("run-conductor: refs/remotes/origin/HEAD is not set in '%s' and %s — refusing to run unpinned\n" % (base, why))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
