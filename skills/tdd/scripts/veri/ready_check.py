"""ready-check.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

from wait_ci import trigger_lines

USAGE = "usage: ready-check.sh [repo-root]"


def git(*argv):
    return subprocess.run(["git", *argv], capture_output=True, text=True)


def default_tip():
    head = git("symbolic-ref", "refs/remotes/origin/HEAD")
    return head.stdout.strip() if head.returncode == 0 else "main"


def triggers_on(event):
    tip = default_tip()
    names = git("ls-tree", "--name-only", tip, ".github/workflows/").stdout.split()
    for name in names:
        text = git("show", tip + ":" + name).stdout
        if any(event in line for line in trigger_lines(text)):
            return True
    return False


def main(argv):
    if len(argv) > 1 or any(a.startswith("-") for a in argv):
        print(USAGE, file=sys.stderr)
        return 2
    if argv:
        os.chdir(argv[0])
    else:
        listing = git("worktree", "list", "--porcelain").stdout.split("\n", 1)[0]
        if listing.startswith("worktree "):
            os.chdir(listing[len("worktree "):])
    inside = git("rev-parse", "--git-dir")
    if inside.returncode != 0:
        print(f"ready-check.sh: not a git repository\n{USAGE}", file=sys.stderr)
        return 2
    detect = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "detect-test-command.sh")
    failed = []
    for tier in ("fast", "all"):
        found = subprocess.run([detect, "--tier", tier], capture_output=True)
        if found.returncode == 3:
            failed.append(f"fail  {tier} tier: add a `veri: {tier} tests:` line to CLAUDE.md")
    if not os.environ.get("VERI_CI_ON_PR") and not triggers_on("pull_request"):
        failed.append("fail  pull_request: add a workflow under .github/workflows/ that triggers on pull_request, or set VERI_CI_ON_PR")
    if not triggers_on("push"):
        failed.append("fail  push: add a workflow under .github/workflows/ that triggers on push to the default branch")
    if failed:
        print(*failed, sep="\n")
        print(f"not ready — {len(failed)} rows to fix")
        return 1
    print("ready")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
