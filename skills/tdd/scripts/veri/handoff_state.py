"""handoff-state.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import sys

from git import git

import github

import status
import entry


def out(*args):
    return git(*args, capture_output=True, text=True).stdout.strip()


def has_open_pr(branch):
    return bool(github.open_pulls("number", head=branch, limit=None))


def parked_reason(run):
    if run["state"] == "bailed":
        return "%s %s" % (run["bail_phase"], run["classification"])
    if run["state"] == "stopped":
        return run["stop_mode"]
    return ""


USAGE = "usage: handoff-state.sh"


def main(argv):
    refused = entry.no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    sha = out("rev-parse", "main")
    tags = out("tag", "--sort=-v:refname").splitlines()
    tag = tags[0] if tags else "(none)"
    lines = ["main %s %s" % (sha, tag), "## Running"]
    code, document = status.json_document()
    runs = json.loads(document)["runs"] if code == 0 else []
    for run in runs:
        if run["state"] == "running":
            lines.append("#%s %s | step %s | %s | $%s | %ss" % (
                run["issue"], run["title"], run["step"], run["phase"], run["dollars"], run["elapsed_seconds"]))
    lines.append("## Parked")
    try:
        for run in runs:
            if run["state"] in ("bailed", "stopped", "stale") and has_open_pr(run.get("branch", "")):
                lines.append(("#%s %s %s" % (run["issue"], run["state"], parked_reason(run))).rstrip())
        lines.append("## Ready to merge")
        for pr in github.open_pulls("number,isDraft,body", limit=None):
            closes = github.closed_issues(pr.body)
            if closes and pr.draft is not True:
                lines.append("PR #%s closes #%s" % (pr.number, closes[0]))
    except github.NoAnswer:
        print("handoff-state.sh: GitHub refused the open PR listing", file=sys.stderr)
        return 2
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
