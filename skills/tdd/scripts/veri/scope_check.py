"""scope-check.sh's pytest basename collision scan, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import event
import ledger
import tunables

USAGE = "usage: scope-check.sh <ledger> <repo-root>"
PY_ROOT = "skills/tdd/scripts/tests/py"
NAMED = re.compile(re.escape(PY_ROOT) + r"/(?:unit/)?test_\w+\.py")


def existing_by_basename(root):
    found = {}
    for top, dirs, files in os.walk(os.path.join(root, PY_ROOT)):
        dirs.sort()
        for name in sorted(files):
            found.setdefault(name, os.path.relpath(os.path.join(top, name), root))
    return found


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    path, root = argv
    existing = existing_by_basename(root)
    with open(path, encoding="utf-8") as lines:
        text = lines.read()
    steps = ledger.ledger_steps(text)
    refusal = ledger.multi_tag_refusal(steps)
    if refusal:
        print("scope-check.sh: " + refusal, file=sys.stderr)
        return 1
    named = NAMED.findall(text)
    clashes = []
    for named_path in dict.fromkeys(named):
        taken = existing.get(os.path.basename(named_path))
        if taken and not os.path.exists(os.path.join(root, named_path)):
            clashes.append(f"{named_path} is new but its basename exists at {taken}")
    if not clashes:
        issue = re.fullmatch(r"issue-(\d+)\.md", os.path.basename(path))
        if issue:
            tdd = os.path.dirname(os.path.abspath(path))
            event.mark(os.path.dirname(tdd), event.context(tunables.with_values(VERI_ISSUE=issue.group(1))),
                       "plan", ["steps=%d" % len(steps)])
        return 0
    print("\n".join(clashes), file=sys.stderr)
    return 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
