"""run-finished.sh's checks, run in-process."""
import json
import os
import subprocess
import sys

import github
from ledger import OPEN_STEP, carries_mark, ledger_steps
from status import json_document, main_working_tree

USAGE = "usage: run-finished.sh <issue>\n"


def pr_body(pr):
    number = pr.rstrip("/").rsplit("/", 1)[-1]
    return json.loads(github.gh_json_page("pr.json", "repos/{owner}/{repo}/pulls/" + number))["body"]


def main(argv):
    if len(argv) != 1:
        sys.stderr.write(USAGE)
        return 2
    issue = argv[0]
    run_dir = os.path.join(main_working_tree(), ".tdd", "wt", issue)
    if not os.path.isdir(run_dir):
        sys.stderr.write("run-finished.sh: no run for issue %s\n" % issue)
        return 2
    runs = json.loads(json_document()[1])["runs"]
    run = next((r for r in runs if r["issue"] == issue), None)
    ledger = os.path.join(run_dir, ".tdd", "issue-%s.md" % issue)
    if run is None and not os.path.isfile(ledger):
        sys.stderr.write("run-finished.sh: cannot read %s\n" % ledger)
        return 2
    run = run or {}
    state = run.get("state", "")
    if state != "done":
        print("not-done %s" % state)
        return 1
    pr = run.get("pr", "")
    if not pr:
        sys.stderr.write("run-finished.sh: no PR is recorded for issue %s\n" % issue)
        return 2
    with open(ledger, encoding="utf-8") as f:
        steps = ledger_steps(f.read())
    unmet = [("unchecked", r[6]) for r in steps if r[1] == "open"]
    unmet += [("refactor-pending", r[6]) for r in steps if r[3] == "1"]
    try:
        body = pr_body(pr)
    except (subprocess.CalledProcessError, github.NoAnswer):
        sys.stderr.write("run-finished.sh: the PR body could not be read\n")
        return 2
    open_line = OPEN_STEP + " "
    star_line = "* " + OPEN_STEP[2:] + " "
    unmet += [("human-owed", ln.lstrip()[len(open_line):]) for ln in body.splitlines()
              if ln.lstrip().startswith((open_line, star_line)) and carries_mark(ln, "human-owed")]
    for name, step in unmet:
        print("%s %s" % (name, step))
    return 1 if unmet else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
