"""queued-merge.sh's logic, run in-process."""
import json
import os
import subprocess
import sys

try:
    from github import gh_api
    from wait_ci import PASSING, pr_head
except ImportError:
    from .github import gh_api
    from .wait_ci import PASSING, pr_head

USAGE = "usage: queued-merge.sh <pr> <worktree> <branch> <tag-message|->"
SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _script(name, *args):
    return subprocess.run([os.path.join(SCRIPTS, name), *args]).returncode


def _repo(pr):
    return pr.removeprefix("https://github.com/").rsplit("/pull/", 1)[0]


def ci_verdict(pr):
    repo = _repo(pr)
    _, head, _ = pr_head(repo, pr)
    runs = json.loads(gh_api("repos/%s/commits/%s/check-runs" % (repo, head)).stdout)["check_runs"]
    return 1 if any(r.get("conclusion") and r["conclusion"].lower() not in PASSING for r in runs) else 0


def main(argv):
    if argv[:1] == ["--ci"]:
        return ci_verdict(argv[1])
    if len(argv) != 4:
        print(USAGE, file=sys.stderr)
        return 2
    pr = argv[0]
    pid = str(os.getpid())
    _script("merge-lock.sh", "take", "--pid", pid)
    code = _script("merge-lock.sh", "gate", "--pid", pid, "--", sys.executable, os.path.abspath(__file__), "--ci", pr)
    if code:
        return code
    for git_args in (("rebase", "origin/main"), ("push", "--force-with-lease", "origin", argv[2])):
        code = _script("merge-lock.sh", "gate", "--keep", "--pid", pid, "--", "git", "-C", argv[1], *git_args)
        if code:
            return code
    _, head, _ = pr_head(_repo(pr), pr)
    code = _script("merge-lock.sh", "gate", "--pid", pid, "--", "gh", "pr", "merge", pr, "--rebase", "--match-head-commit", head)
    if code:
        return code
    _script("merge-lock.sh", "release", "--pid", pid)
    subprocess.run(["git", "-C", argv[1], "push", "origin", "--delete", argv[2]])
    subprocess.run(["git", "-C", argv[1], "worktree", "remove", argv[1]])
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
