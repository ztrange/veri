"""run-finished.sh's checks, run in-process."""
import json
import os
import subprocess
import sys

from ledger import OPEN_STEP, ledger_steps
from status import json_document, main_working_tree

USAGE = "usage: run-finished.sh <issue>\n"


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
    run = next((r for r in runs if r["issue"] == issue), {})
    state = run.get("state", "")
    if state != "done":
        print("not-done %s" % state)
        return 1
    with open(os.path.join(run_dir, ".tdd", "issue-%s.md" % issue), encoding="utf-8") as f:
        steps = ledger_steps(f.read())
    unmet = [("unchecked", r[6]) for r in steps if r[1] == "open"]
    unmet += [("refactor-pending", r[6]) for r in steps if r[3] == "1"]
    try:
        body = json.loads(subprocess.run(
            ["gh", "pr", "view", run.get("pr", ""), "--json", "body"],
            capture_output=True, text=True, check=True).stdout)["body"]
    except subprocess.CalledProcessError:
        sys.stderr.write("run-finished.sh: the PR body could not be read\n")
        return 2
    unmet += [("human-owed", ln[len(OPEN_STEP) + 1:]) for ln in body.splitlines()
              if ln.startswith(OPEN_STEP + " ") and "⟦human-owed⟧" in ln]
    for name, step in unmet:
        print("%s %s" % (name, step))
    return 1 if unmet else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
