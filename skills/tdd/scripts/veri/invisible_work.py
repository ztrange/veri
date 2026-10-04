"""invisible-work.sh's sweep, run in-process."""
import re
import subprocess
import sys


def git(*args, **kwargs):
    return subprocess.run(["git", *args], **kwargs)


def main(argv):
    if git("ls-remote", "--heads", "origin", stdout=subprocess.DEVNULL).returncode != 0:
        print("invisible-work.sh: cannot reach origin", file=sys.stderr)
        return 2

    if git("symbolic-ref", "--short", "refs/remotes/origin/HEAD",
           stdout=subprocess.PIPE, text=True).returncode != 0:
        return 2
    return 3


def head(pr):
    return pr["headRefName"] if "headRefName" in pr else pr["head"]["ref"]


def report(branches, locals_, documents):
    from json_documents import items

    issues_text, prs_text = documents.split("\0")
    issues = {i["number"]: i["state"].upper() for i in items(issues_text)}
    prs = items(prs_text)
    with_pr = {head(p) for p in prs}
    decided = {head(p) for p in prs if p["state"].upper() in ("MERGED", "CLOSED")}
    findings = []

    for row in branches.splitlines():
        name, tip, ahead = row.split()
        if name in with_pr:
            continue
        finding = f"invariant 2 (no PR): {name} tip {tip} {ahead} commits ahead"
        m = re.match(r"tdd/(\d+)-", name)
        if m:
            n = int(m.group(1))
            state = issues.get(n, "unknown")
            finding += f", issue #{n} {state}"
        findings.append(finding)

    for row in locals_.splitlines():
        name, tip, lacks, worktree = row.split(" ", 3)
        if name in decided:
            continue
        finding = f"invariant 1 (not on origin): {name} tip {tip} {lacks} commits origin lacks"
        if worktree:
            finding += f", worktree {worktree}"
        findings.append(finding)

    for finding in findings:
        print(finding)

    return 0 if findings else 3


if __name__ == "__main__":
    sys.exit(report(sys.argv[1], sys.argv[2], sys.stdin.read()))
