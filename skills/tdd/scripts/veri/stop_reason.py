"""stop-reason.sh's report, run in-process."""
import json
import os
import sys


def main(argv):
    if len(argv) != 1:
        sys.stderr.write("usage: stop-reason.sh <issue>\n")
        return 2
    if not os.path.isdir(os.path.join(".tdd", "wt", argv[0])):
        sys.stderr.write("stop-reason.sh: no run for issue %s under .tdd/wt\n" % argv[0])
        return 2
    log = os.path.join(".tdd", "wt", argv[0], ".tdd", "events.jsonl")
    with open(log) as f:
        last = json.loads(f.read().splitlines()[-1])
    if last.get("event") == "done":
        sys.stdout.write("done %s\n" % last.get("pr"))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
