"""wait-ci.sh's logic, run in-process."""
import json
import subprocess
import sys

try:
    from github import _gh_api, gh_rest_list
    from json_documents import documents
except ImportError:
    from .github import _gh_api, gh_rest_list
    from .json_documents import documents

USAGE = "usage: wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha]"
PASSING = ("success", "neutral", "skipped")


def pr_head(repo, pr):
    run = _gh_api("repos/%s/pulls/%s" % (repo, pr.rsplit("/pull/", 1)[-1]))
    if run.returncode != 0:
        return None, ""
    pull = json.loads(run.stdout)
    return pull.get("mergeable"), pull["head"]["sha"] or ""


def sha_state(repo, sha):
    runs = gh_rest_list("repos/%s/commits/%s/check-runs" % (repo, sha), r'"check_runs": *\[ *\]')
    statuses = _gh_api("repos/%s/commits/%s/status" % (repo, sha)).stdout
    docs = documents(runs + statuses)
    states = [s["state"] for s in docs[-1].get("statuses") or []]
    runs = [r for p in docs[:-1] for r in p.get("check_runs") or []]
    outcomes = [r.get("conclusion") if r.get("status") == "completed" else None for r in runs]
    if any(o is not None and o not in PASSING for o in outcomes) \
            or any(s in ("failure", "error") for s in states):
        return "red"
    if not runs and not states:
        return "none"
    if None in outcomes or all(o == "skipped" for o in outcomes) or "pending" in states:
        return "pending"
    return "green"


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    pr = argv[0]
    repo = pr.removeprefix("https://github.com/").rsplit("/pull/", 1)[0]
    want = argv[3] if len(argv) > 3 else ""
    mergeable, head = pr_head(repo, pr)
    if not head:
        print("wait-ci.sh: could not read the checks of %s" % pr, file=sys.stderr)
        return 2
    state = sha_state(repo, head)
    if state == "none" and mergeable is False:
        print("wait-ci.sh: %s conflicts with its base branch; no workflow will start until it is rebased"
              % pr, file=sys.stderr)
        return 2
    if want and head != want:
        state = "pending"
    if state == "green":
        return 0
    if state == "red":
        return 1
    subprocess.run(["date", "+%s"], stdout=subprocess.PIPE, text=True)
    return 3
