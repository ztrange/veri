"""run-finished.sh's checks, run in-process."""
import json
import os
import sys

from ledger import ledger_steps
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
    state = next((r.get("state", "") for r in runs if r["issue"] == issue), "")
    if state != "done":
        print("not-done %s" % state)
        return 1
    with open(os.path.join(run_dir, ".tdd", "issue-%s.md" % issue), encoding="utf-8") as f:
        open_steps = [r[6] for r in ledger_steps(f.read()) if r[1] == "open"]
    for step in open_steps:
        print("unchecked %s" % step)
    return 1 if open_steps else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
