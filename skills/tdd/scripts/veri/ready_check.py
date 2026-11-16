"""ready-check.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import subprocess
import sys

import git
import launch_floor
import paths
import tunables
from github import gh_probe as gh
from case_reader import is_test_path
from wait_ci import trigger_lines

USAGE = "usage: ready-check.sh [repo-root]"


def default_tip():
    name = git.default_branch(remote=False)
    return "refs/remotes/origin/" + name if name else "main"


def triggers_on(event):
    tip = default_tip()
    names = git.git("ls-tree", "--name-only", tip, ".github/workflows/", capture_output=True, text=True).stdout.split()
    for name in names:
        text = git.git("show", tip + ":" + name, capture_output=True, text=True).stdout
        if any(event in line for line in trigger_lines(text)):
            return True
    return False


def detect_tier(tier):
    """detect-test-command.sh --tier <tier>'s exit code."""
    detect = os.path.join(paths.resolved_scripts_of(__file__), "detect-test-command.sh")
    return subprocess.run([detect, "--tier", tier], capture_output=True).returncode


def tier_row(tier):
    def check():
        code = detect_tier(tier)
        if code == 2:
            return f"{tier} tier", f"no answer was obtained (exit 2 from detect-test-command.sh --tier {tier})"
        return f"{tier} tier", None if code != 3 else f"add a `veri: {tier} tests:` line to CLAUDE.md"
    return check


def one_test_file_row():
    code = detect_tier("one test file")
    if code == 2:
        return "one test file", 'no answer was obtained (exit 2 from detect-test-command.sh --tier "one test file")'
    return "one test file", None if code == 0 else (
        'add a `veri: one test file: <command>` line to CLAUDE.md, the command taking the test file as "$1"')


def pull_request_row():
    holds = bool(tunables.read("VERI_CI_ON_PR")) or triggers_on("pull_request")
    return "pull_request", None if holds else "add a workflow under .github/workflows/ that triggers on pull_request, or set VERI_CI_ON_PR"


def push_row():
    return "push", None if triggers_on("push") else "add a workflow under .github/workflows/ that triggers on push to the default branch"


def test_file_row():
    holds = any(is_test_path(f) for f in git.git("ls-files", capture_output=True, text=True).stdout.splitlines())
    return "test file", None if holds else "track at least one test file"


def tdd_ignored_row():
    return ".tdd/", None if git.git("check-ignore", "-q", ".tdd/issue-0-spec.md", capture_output=True, text=True).returncode == 0 else "add `.tdd/` to .gitignore"


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
    label = tunables.get("VERI_LABEL")
    if not label:
        return "label", "VERI_LABEL is set but empty: name a label or leave VERI_LABEL unset"
    listed = gh("label", "list", "--json", "name")
    try:
        names = [entry["name"] for entry in json.loads(listed.stdout)] if listed.returncode == 0 else []
    except (ValueError, KeyError, TypeError):
        names = []
    return f"label {label}", None if label in names else f"create the `{label}` label in the repository"


class Neutral(str):
    """A row's verdict that is neither ok nor fail: printed as its own word, and counted as no fail."""


NOT_VERIFIABLE = Neutral("not verifiable")


def granted_scopes():
    """The scopes `gh api -i user`'s X-OAuth-Scopes header lists; None with no such header (a fine-grained token)."""
    head = gh("api", "-i", "user").stdout.split("\r\n\r\n", 1)[0].split("\n\n", 1)[0]
    for line in head.splitlines():
        name, _, value = line.partition(":")
        if name.strip().lower() == "x-oauth-scopes":
            return [scope.strip() for scope in value.split(",") if scope.strip()]
    return None


def origin_is_https():
    return git.git("remote", "get-url", "origin", capture_output=True, text=True).stdout.strip().startswith("https://")


def token_scopes_row():
    needed = ["repo", "workflow"] if origin_is_https() else ["repo"]
    granted = granted_scopes()
    if granted is None:
        return "token scopes", NOT_VERIFIABLE
    missing = [scope for scope in needed if scope not in granted]
    return "token scopes", "gh auth refresh -s " + ",".join(missing) if missing else None


def bash_row():
    holds = launch_floor.bash_refusal("ready-check") == 0
    return "bash", None if holds else "install bash 5 or newer (`brew install bash`) and put it first on PATH"


def python_row():
    holds = launch_floor.python_refusal("ready-check") == 0
    return "Python", None if holds else f"install Python {launch_floor.python_floor()} or newer and put it first on PATH"


CHECKS = (tier_row("fast"), tier_row("all"), one_test_file_row, pull_request_row, push_row, test_file_row, tdd_ignored_row,
          gh_auth_row, push_access_row, label_row, bash_row, python_row)


def main(argv):
    if len(argv) > 1 or any(a.startswith("-") for a in argv):
        print(USAGE, file=sys.stderr)
        return 2
    if argv:
        os.chdir(argv[0])
    else:
        listing = git.git("worktree", "list", "--porcelain", capture_output=True, text=True).stdout.split("\n", 1)[0]
        if listing.startswith("worktree "):
            os.chdir(listing[len("worktree "):])
    inside = git.git("rev-parse", "--git-dir", capture_output=True, text=True)
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
