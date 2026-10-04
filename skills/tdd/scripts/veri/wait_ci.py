"""wait-ci.sh's logic, run in-process."""
import json
import os
import subprocess
import sys
import traceback

try:
    from github import NoAnswer, _gh_api, gh_rest_list
    from json_documents import documents
except ImportError:
    from .github import NoAnswer, _gh_api, gh_rest_list
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
    status = _gh_api("repos/%s/commits/%s/status" % (repo, sha))
    if status.returncode != 0:
        raise NoAnswer("")
    statuses = status.stdout
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


def unreadable(what):
    print("wait-ci.sh: could not read the checks of %s" % what, file=sys.stderr)
    return 2


def record(mark, deadline):
    try:
        with open(mark, "w") as out:
            out.write("%d\n" % deadline)
    except OSError as error:
        print("wait-ci.sh: %s" % error, file=sys.stderr)


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    pr = argv[0]
    repo = pr.removeprefix("https://github.com/").rsplit("/pull/", 1)[0]
    span = int(argv[1]) if len(argv) > 1 and argv[1] else 540
    total = int(argv[2])
    want = argv[3] if len(argv) > 3 else ""
    poll = os.environ.get("VERI_POLL") or "10"
    deadline = None
    while True:
        try:
            mergeable, head = pr_head(repo, pr)
        except Exception:
            traceback.print_exc()
            head = ""
        if not head:
            return unreadable(pr)
        try:
            state = sha_state(repo, head)
        except NoAnswer:
            state = None
        except Exception:
            traceback.print_exc()
            state = None
        if state is None:
            return unreadable(head)
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
        now = int(subprocess.run(["date", "+%s"], stdout=subprocess.PIPE, text=True).stdout)
        if deadline is None:
            slice_end = now + span
            key = want or head
            mark = ".tdd/ci-deadline-" + key
            inherited = os.path.isfile(mark)
            if inherited:
                with open(mark) as found:
                    deadline = int(found.read())
            else:
                deadline = now + total
                record(mark, deadline)
        if now >= deadline:
            if inherited:
                print("wait-ci.sh: checks of %s still pending past the deadline recorded for %s"
                      % (pr, key), file=sys.stderr)
                return 2
            break
        if now >= slice_end:
            break
        subprocess.run(["sleep", poll])
    return 3
