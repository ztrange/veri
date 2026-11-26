"""invisible-work.sh's sweep, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import subprocess
import sys

from entry import no_arguments
from git import GitFailed, git, symref_default
from git import default_branch as local_default_branch
from git import out as git_value
from github import NoAnswer, gh_json, open_pulls_text, pulls_in
from json_documents import items


def git_out(*args):
    return git(*args, stdout=subprocess.PIPE, text=True).stdout


def refs(prefix):
    for line in git_out("for-each-ref", "--format=%(refname) %(objectname)", prefix).splitlines():
        ref, tip = line.split(" ", 1)
        yield ref, tip


def default_branch():
    name = local_default_branch(remote=False)
    if name is not None:
        return name
    name = symref_default(git_out("ls-remote", "--symref", "origin", "HEAD"))
    if name is not None:
        return name
    print("invisible-work.sh: no refs/remotes/origin/HEAD and origin names no default branch",
          file=sys.stderr)
    raise GitFailed(("ls-remote", "--symref", "origin", "HEAD"), 0, "names no default branch")


def remote_rows(default):
    rows = []
    for ref, tip in refs("refs/remotes/origin/"):
        name = ref.removeprefix("refs/remotes/origin/")
        if name in (default, "HEAD"):
            continue
        ahead = git_value("rev-list", "--count", f"origin/{default}..{ref}")
        rows.append((name, tip, ahead))
    return rows


def worktrees():
    worktree_of, path = {}, ""
    for line in git_out("worktree", "list", "--porcelain").splitlines():
        fields = line.split(None, 1)
        key = fields[0] if fields else ""
        value = fields[1].strip() if len(fields) > 1 else ""
        if key == "worktree":
            path = value
        elif key == "branch":
            worktree_of[value] = path
    return worktree_of


def local_rows():
    worktree_of = worktrees()
    rows = []
    for ref, tip in refs("refs/heads/"):
        name = ref.removeprefix("refs/heads/")
        if git("show-ref", "-q", "--verify", f"refs/remotes/origin/{name}").returncode == 0:
            continue
        lacks = git_value("rev-list", "--count", ref, "--not", "--remotes=origin")
        rows.append((name, tip, lacks, worktree_of.get(ref, "")))
    return rows


USAGE = "usage: invisible-work.sh"


def main(argv):
    refused = no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    if git("ls-remote", "--heads", "origin", stdout=subprocess.DEVNULL).returncode != 0:
        print("invisible-work.sh: cannot reach origin", file=sys.stderr)
        return 2

    try:
        issues_text = gh_json("issues.json", "repos/{owner}/{repo}/issues?state=all&per_page=100",
                              "issue", "list", "--state", "all", "--limit", "10000",
                              "--json", "number,state")
        prs_text = open_pulls_text("headRefName,headRefOid,state", state="all")
    except (NoAnswer, OSError):
        print("invisible-work.sh: cannot read issues and PRs from gh (unauthenticated?)",
              file=sys.stderr)
        return 2

    try:
        default = default_branch()
        branches = remote_rows(default)
        locals_ = local_rows()
    except GitFailed:
        return 2

    return report(branches, locals_, issues_text, prs_text)


def report(branches, locals_, issues_text, prs_text):
    issues = {i["number"]: i["state"].upper() for i in items(issues_text)}
    prs = pulls_in(prs_text)
    with_pr = {p.head_ref for p in prs}
    decided = {(p.head_ref, p.head_sha) for p in prs if p.state in ("MERGED", "CLOSED")}
    findings = []

    for name, tip, ahead in branches:
        if name in with_pr:
            continue
        finding = f"invariant 2 (no PR): {name} tip {tip} {ahead} commits ahead"
        m = re.match(r"tdd/(\d+)-", name)
        if m:
            n = int(m.group(1))
            state = issues.get(n, "unknown")
            finding += f", issue #{n} {state}"
        findings.append(finding)

    for name, tip, lacks, worktree in locals_:
        if (name, tip) in decided:
            continue
        finding = f"invariant 1 (not on origin): {name} tip {tip} {lacks} commits origin lacks"
        if worktree:
            finding += f", worktree {worktree}"
        findings.append(finding)

    for finding in findings:
        print(finding)

    return 0 if findings else 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
