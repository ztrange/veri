"""parse-adjudication.sh's answer reader, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

USAGE = "usage: parse-adjudication.sh <leaf-output>"


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    with open(argv[0]) as f:
        lines = [l for l in f.read().splitlines() if l.startswith("ADJUDICATION:")]
    outcome, _, reason = lines[-1][len("ADJUDICATION:"):].strip().partition(" — ")
    kind, _, token = outcome.partition(" ")
    doc = os.path.join(os.path.dirname(__file__), "..", "..", "ADJUDICATE.md")
    with open(doc) as f:
        eligible = re.findall(r"- `[^`]+`:(.*)$", f.read(), re.M)
    listed_route = kind == "route" and any(token in re.findall(r"`([^`]+)`", t) for t in eligible)
    if not listed_route and outcome not in ("retry", "bail", "route"):
        return 2
    print(outcome)
    print(reason)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
