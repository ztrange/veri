"""comment.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import event
import github
from ledger import ledger_path, ledger_steps

USAGE = "usage: comment.sh <issue> <kind> [--note-file <path>]"


def main(argv):
    if len(argv) < 2 or (len(argv) > 2 and (argv[2] != "--note-file" or len(argv) != 4)):
        print(USAGE, file=sys.stderr)
        return 2
    issue = argv[0]
    with open(ledger_path(".", issue)) as f:
        done = [r for r in ledger_steps(f.read()) if r[1] == "done"]
    body = f"### ✅ Step done\n\n{done[-1][6]}\n"
    if len(argv) > 3:
        with open(argv[3]) as f:
            body += f"\n{f.read()}"
    url = github.gh_issue_comment(issue, body).rstrip("\n")
    return event.append("", {}, "comment", ["kind=step-done", f"url={url}"])


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
