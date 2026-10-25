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


def _gate(pid, cmd, keep=False):
    return _script("merge-lock.sh", "gate", *(["--keep"] if keep else []), "--pid", pid, "--", *cmd)


def _repo(pr):
    return pr.removeprefix("https://github.com/").rsplit("/pull/", 1)[0]


def ci_verdict(pr):
    repo = _repo(pr)
    _, head, _ = pr_head(repo, pr)
    runs = json.loads(gh_api("repos/%s/commits/%s/check-runs" % (repo, head)).stdout)["check_runs"]
    return 1 if any(r.get("conclusion") and r["conclusion"].lower() not in PASSING for r in runs) else 0


def _tag(worktree, message):
    tags = subprocess.run(["git", "-C", worktree, "tag", "--sort=-v:refname"], capture_output=True, text=True).stdout.split()
    major, minor = tags[0].removeprefix("v").split(".")
    name = "v%s.%d" % (major, int(minor) + 1)
    subprocess.run(["git", "-C", worktree, "tag", "-a", name, "-m", message, "origin/main"])
    subprocess.run(["git", "-C", worktree, "push", "origin", name])


def main(argv):
    if argv[:1] == ["--ci"]:
        return ci_verdict(argv[1])
    if len(argv) != 4:
        print(USAGE, file=sys.stderr)
        return 2
    pr = argv[0]
    repo = _repo(pr)
    pid = str(os.getpid())
    _script("merge-lock.sh", "take", "--pid", pid)
    code = _gate(pid, (sys.executable, os.path.abspath(__file__), "--ci", pr))
    if code:
        return code
    for git_args in (("rebase", "origin/main"), ("push", "--force-with-lease", "origin", argv[2])):
        code = _gate(pid, ("git", "-C", argv[1], *git_args), keep=True)
        if code:
            return code
    _, head, _ = pr_head(repo, pr)
    code = _gate(pid, ("gh", "pr", "merge", pr, "--rebase", "--match-head-commit", head))
    if code:
        return code
    landed = json.loads(gh_api("repos/%s/pulls/%s" % (repo, pr.rsplit("/pull/", 1)[-1])).stdout).get("merged") is not False
    _script("merge-lock.sh", "release", "--pid", pid)
    if not landed:
        return 1
    subprocess.run(["git", "-C", argv[1], "push", "origin", "--delete", argv[2]])
    subprocess.run(["git", "-C", argv[1], "worktree", "remove", argv[1]])
    if argv[3] != "-":
        _tag(argv[1], argv[3])
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
