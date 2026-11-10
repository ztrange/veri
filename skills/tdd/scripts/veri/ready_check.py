"""ready-check.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import subprocess
import sys

import launch_floor
import tunables
from github import gh_probe as gh
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


def tier_row(tier):
    def check():
        detect = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "detect-test-command.sh")
        found = subprocess.run([detect, "--tier", tier], capture_output=True)
        if found.returncode == 2:
            return f"{tier} tier", f"no answer was obtained (exit 2 from detect-test-command.sh --tier {tier})"
        return f"{tier} tier", None if found.returncode != 3 else f"add a `veri: {tier} tests:` line to CLAUDE.md"
    return check


def pull_request_row():
    holds = bool(tunables.read("VERI_CI_ON_PR")) or triggers_on("pull_request")
    return "pull_request", None if holds else "add a workflow under .github/workflows/ that triggers on pull_request, or set VERI_CI_ON_PR"


def push_row():
    return "push", None if triggers_on("push") else "add a workflow under .github/workflows/ that triggers on push to the default branch"


def test_file_row():
    holds = any(is_test_path(f) for f in git("ls-files").stdout.splitlines())
    return "test file", None if holds else "track at least one test file"


def tdd_ignored_row():
    return ".tdd/", None if git("check-ignore", "-q", ".tdd/issue-0-spec.md").returncode == 0 else "add `.tdd/` to .gitignore"


def gh_auth_row():
    return "gh auth", None if gh("auth", "status").returncode == 0 else "run `gh auth login`"


def push_access_row():
    pushed = gh("api", "repos/{owner}/{repo}")
    try:
        can_push = json.loads(pushed.stdout)["permissions"]["push"]
    except (ValueError, KeyError, TypeError):
        can_push = False
    return "push access", None if can_push else "ask for write access to the repository, or use an account that has it"


def label_row():
    label = tunables.read("VERI_LABEL", "ready-for-agent")
    if not label:
        return "label", "VERI_LABEL is set but empty: name a label or leave VERI_LABEL unset"
    listed = gh("label", "list", "--json", "name")
    try:
        names = [entry["name"] for entry in json.loads(listed.stdout)] if listed.returncode == 0 else []
    except (ValueError, KeyError, TypeError):
        names = []
    return f"label {label}", None if label in names else f"create the `{label}` label in the repository"


def bash_row():
    holds = launch_floor.bash_refusal("ready-check") == 0
    return "bash", None if holds else "install bash 5 or newer (`brew install bash`) and put it first on PATH"


def python_row():
    holds = launch_floor.python_refusal("ready-check") == 0
    return "Python", None if holds else f"install Python {launch_floor.python_floor()} or newer and put it first on PATH"


CHECKS = (tier_row("fast"), tier_row("all"), pull_request_row, push_row, test_file_row, tdd_ignored_row,
          gh_auth_row, push_access_row, label_row, bash_row, python_row)


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
    results = [check() for check in CHECKS]
    failed = sum(1 for _, fix in results if fix)
    rows = [f"fail  {name}: {fix}" if fix else f"ok    {name}" for name, fix in results]
    print(*rows, sep="\n")
    if failed:
        print(f"not ready — {failed} rows to fix")
        return 1
    print("ready")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
