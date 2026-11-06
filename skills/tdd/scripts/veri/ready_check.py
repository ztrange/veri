"""ready-check.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

USAGE = "usage: ready-check.sh [repo-root]"


def main(argv):
    if len(argv) > 1 or any(a.startswith("-") for a in argv):
        print(USAGE, file=sys.stderr)
        return 2
    inside = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True)
    if inside.returncode != 0:
        print(f"ready-check.sh: not a git repository\n{USAGE}", file=sys.stderr)
        return 2
    detect = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "detect-test-command.sh")
    fast = subprocess.run([detect, "--tier", "fast"], capture_output=True)
    if fast.returncode == 3:
        print("fail  fast tier: add a `veri: fast tests:` line to CLAUDE.md")
        print("not ready — 1 rows to fix")
        return 1
    print("ready")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
