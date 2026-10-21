"""handoff-state.sh's computation, run in-process."""
import json
import re
import sys

from git import git

import github
import json_documents
import tunables

try:
    from . import status
except ImportError:
    import status


def out(*args):
    return git(*args, capture_output=True, text=True).stdout.strip()


OPEN_PULLS = "repos/{owner}/{repo}/pulls?state=open&per_page=100"


def with_draft_flag(pulls):
    return [dict(pr, isDraft=pr.get("draft", pr.get("isDraft", False))) for pr in pulls]


def rest_open_prs(*extra):
    path = OPEN_PULLS
    if extra:
        path += "&head={owner}:" + extra[-1]
    return with_draft_flag(json_documents.items(github.gh_rest_list(path)))


def open_prs(fields, *extra):
    if tunables.read("VERI_GH_JSON"):
        pulls = json.loads(github.gh_json("prs.json", OPEN_PULLS))
        if extra:
            pulls = [pr for pr in pulls if pr.get("head", {}).get("ref") == extra[-1]]
        return with_draft_flag(pulls)
    driver = tunables.read("VERI_GH_DRIVER", "rest")
    if driver not in ("rest", "graphql", "auto"):
        print("VERI_GH_DRIVER is '%s': expected auto, rest or graphql" % driver, file=sys.stderr)
        raise github.NoAnswer("")
    if driver == "rest":
        return rest_open_prs(*extra)
    try:
        answer = github.GraphQLAdapter().list("pr", "list", *extra, "--state", "open", "--json", fields)
    except github.NoAnswer:
        if driver == "auto":
            return rest_open_prs(*extra)
        raise
    return json.loads(answer or "[]")


def has_open_pr(branch):
    return bool(open_prs("number", "--head", branch))


def parked_reason(run):
    if run["state"] == "bailed":
        return "%s %s" % (run["bail_phase"], run["classification"])
    if run["state"] == "stopped":
        return run["stop_mode"]
    return ""


def main(argv):
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
        for pr in open_prs("number,isDraft,body"):
            closes = re.search(r"\bCloses #(\d+)", pr["body"] or "")
            if closes and not pr["isDraft"]:
                lines.append("PR #%s closes #%s" % (pr["number"], closes.group(1)))
    except github.NoAnswer:
        print("handoff-state.sh: GitHub refused the open PR listing", file=sys.stderr)
        return 2
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
