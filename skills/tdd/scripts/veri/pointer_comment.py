"""pointer-comment.sh's logic: the one `### 📍 Run state` comment on an issue, posted when it has none and edited in
place otherwise, saying where the issue's run is."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import datetime
import re
import subprocess
import sys

import entry
import event_log
import git
import github
import ledger
import run_dir
import tunables

HEADING = "### 📍 Run state"
USAGE = "usage: pointer-comment.sh <issue-number>"
LAST_PUSH = "Last push: "


def branch():
    try:
        return git.out("rev-parse", "--abbrev-ref", "HEAD") or "none"
    except git.GitFailed:
        return "none"


def pr_url(name):
    if name == "none":
        return "none"
    pulls = github.rest_items("repos/{owner}/{repo}/pulls?state=all&per_page=100&head={owner}:%s" % name)
    return next((p.get("html_url") or p.get("url") for p in pulls if (p.get("head") or {}).get("ref") == name), "none")


def step(issue):
    try:
        with open(run_dir.ledger(".", issue), encoding="utf-8") as f:
            steps = ledger.ledger_steps(f.read())
    except FileNotFoundError:
        return "none"
    current = next((s.number for s in steps if s.state == "open"), str(len(steps)))
    return "%s/%d" % (current, len(steps))


def phase(issue):
    named = [e["phase"] for e in event_log.events(".", skip_unreadable=True)
             if str(e.get("issue", "")) == issue and e.get("phase")]
    return named[-1] if named else "none"


def now():
    """The current local time, ISO-8601 to the second with its UTC offset."""
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def last_push(previous):
    return next((line.removeprefix(LAST_PUSH) for line in previous.splitlines() if line.startswith(LAST_PUSH)), "none")


def machine():
    """VERI_MACHINE_NAME, or what `hostname -s` prints when that is unset or empty."""
    named = tunables.get("VERI_MACHINE_NAME")
    if named:
        return named
    try:
        short = subprocess.run(["hostname", "-s"], capture_output=True, text=True).stdout.strip()
    except OSError:
        short = ""
    return short or "unknown"


def render(issue, pushed_at):
    name = branch()
    return "\n".join([
        HEADING,
        "",
        "Branch: %s" % name,
        "PR: %s" % pr_url(name),
        "Step: %s" % step(issue),
        "Phase: %s" % phase(issue),
        LAST_PUSH + pushed_at,
        "Machine: %s" % machine(),
        "Resume: $S/run-conductor.sh %s" % issue,
    ]) + "\n"


def write(issue, pushed_at=None):
    """Post or edit issue <issue>'s pointer comment; <pushed_at> is the push just made, else the comment keeps its own.
    0 written; 2 when gh gave no answer, said in one stderr line naming the issue."""
    try:
        held = [c for c in github.issue_comments(issue) if (c.get("body") or "").startswith(HEADING)]
        body = render(issue, pushed_at or last_push(held[0]["body"] if held else ""))
        if held:
            github.gh_comment_edit(held[0]["id"], body)
        else:
            github.gh_comment_post(issue, body)
    except github.NoAnswer as failed:
        said = " ".join(failed.detail.split())
        sys.stderr.write("pointer-comment: no answer from gh writing #%s's pointer comment%s\n"
                         % (issue, ": " + said if said else ""))
        return 2
    return 0


def mirror(issue, pushed_at=None):
    """write, for a caller whose own exit code the pointer comment never changes."""
    write(issue, pushed_at)


def run_issue(name):
    """The issue a run's branch `tdd/<n>-<slug>` names, or None for any other branch."""
    found = re.fullmatch(r"tdd/(\d+)-.+", name)
    return found.group(1) if found else None


def after_push():
    """The pointer comment of the issue the current branch names, stamped with this push; nothing on another branch."""
    issue = run_issue(branch())
    if issue:
        mirror(issue, pushed_at=now())


def main(argv):
    if len(argv) != 1 or not argv[0].isdecimal():
        return entry.refuse(usage=USAGE)
    return write(argv[0])


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
