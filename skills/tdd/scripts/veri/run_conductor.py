"""run-conductor.sh's launch of one conductor, run in-process."""
import os
import subprocess
import sys

import launch_floor

USAGE = "usage: run-conductor.sh <issue>"


def main(argv):
    if launch_floor.bash_refusal("run-conductor") or launch_floor.python_refusal("run-conductor"):
        return 2
    if not argv or not argv[0]:
        sys.stderr.write(USAGE + "\n")
        return 2
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if subprocess.run(["git", "-C", base, "remote", "get-url", "origin"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        fetches = 0
        while True:
            fetch = subprocess.run(["git", "-C", base, "fetch", "-q", "origin"],
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
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
