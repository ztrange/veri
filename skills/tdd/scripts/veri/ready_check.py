"""ready-check.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import subprocess
import sys

from case_reader import is_test_path
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
    rows = []

    def row(name, holds, fix):
        rows.append(f"ok    {name}" if holds else f"fail  {name}: {fix}")

    for tier in ("fast", "all"):
        found = subprocess.run([detect, "--tier", tier], capture_output=True)
        row(f"{tier} tier", found.returncode != 3, f"add a `veri: {tier} tests:` line to CLAUDE.md")
    row("pull_request", bool(os.environ.get("VERI_CI_ON_PR")) or triggers_on("pull_request"), "add a workflow under .github/workflows/ that triggers on pull_request, or set VERI_CI_ON_PR")
    row("push", triggers_on("push"), "add a workflow under .github/workflows/ that triggers on push to the default branch")
    row("test file", any(is_test_path(f) for f in git("ls-files").stdout.splitlines()), "track at least one test file")
    row(".tdd/", git("check-ignore", "-q", ".tdd/").returncode == 0, "add `.tdd/` to .gitignore")
    row("gh auth", subprocess.run(["gh", "auth", "status"], capture_output=True).returncode == 0, "run `gh auth login`")
    pushed = subprocess.run(["gh", "api", "repos/{owner}/{repo}"], capture_output=True, text=True)
    try:
        can_push = json.loads(pushed.stdout)["permissions"]["push"]
    except (ValueError, KeyError, TypeError):
        can_push = False
    row("push access", can_push, "ask for write access to the repository, or use an account that has it")
    failed = [r for r in rows if r.startswith("fail")]
    print(*rows, sep="\n")
    if failed:
        print(f"not ready — {len(failed)} rows to fix")
        return 1
    print("ready")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
