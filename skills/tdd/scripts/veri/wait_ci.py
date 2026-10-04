"""wait-ci.sh's logic, run in-process."""
import json
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
        return ""
    return json.loads(run.stdout)["head"]["sha"]


def sha_state(repo, sha):
    runs = gh_rest_list("repos/%s/commits/%s/check-runs" % (repo, sha), r'"check_runs": *\[ *\]')
    statuses = _gh_api("repos/%s/commits/%s/status" % (repo, sha)).stdout
    docs = documents(runs + statuses)
    states = [s["state"] for s in docs[-1].get("statuses")]
    outcomes = [r.get("conclusion") for p in docs[:-1] for r in p.get("check_runs")]
    if any(o not in PASSING for o in outcomes) or any(s in ("failure", "error") for s in states):
        return "red"
    return "green"


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    pr = argv[0]
    repo = pr.removeprefix("https://github.com/").rsplit("/pull/", 1)[0]
    head = pr_head(repo, pr)
    if not head:
        print("wait-ci.sh: could not read the checks of %s" % pr, file=sys.stderr)
        return 2
    return 0 if sha_state(repo, head) == "green" else 1
