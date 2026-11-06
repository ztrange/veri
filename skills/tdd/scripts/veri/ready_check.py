"""ready-check.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

from wait_ci import trigger_lines

USAGE = "usage: ready-check.sh [repo-root]"


def default_tip():
    head = subprocess.run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
                          capture_output=True, text=True)
    return head.stdout.strip() if head.returncode == 0 else "main"


def triggers_on_pull_request():
    tip = default_tip()
    names = subprocess.run(["git", "ls-tree", "--name-only", tip, ".github/workflows/"],
                           capture_output=True, text=True).stdout.split()
    for name in names:
        text = subprocess.run(["git", "show", tip + ":" + name], capture_output=True, text=True).stdout
        if any("pull_request" in line for line in trigger_lines(text)):
            return True
    return False


def main(argv):
    if len(argv) > 1 or any(a.startswith("-") for a in argv):
        print(USAGE, file=sys.stderr)
        return 2
    if argv:
        os.chdir(argv[0])
    inside = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True)
    if inside.returncode != 0:
        print(f"ready-check.sh: not a git repository\n{USAGE}", file=sys.stderr)
        return 2
    detect = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "detect-test-command.sh")
    failed = 0
    for tier in ("fast", "all"):
        found = subprocess.run([detect, "--tier", tier], capture_output=True)
        if found.returncode == 3:
            print(f"fail  {tier} tier: add a `veri: {tier} tests:` line to CLAUDE.md")
            failed += 1
    if not triggers_on_pull_request():
        print("fail  pull_request: add a workflow under .github/workflows/ that triggers on pull_request, or set VERI_CI_ON_PR")
        failed += 1
    if failed:
        print(f"not ready — {failed} rows to fix")
        return 1
    print("ready")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
