"""scope-check.sh's pytest basename collision scan, run in-process."""
import os
import re
import sys

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
    ledger, root = argv
    existing = existing_by_basename(root)
    with open(ledger, encoding="utf-8") as lines:
        named = NAMED.findall(lines.read())
    clashes = []
    for path in dict.fromkeys(named):
        taken = existing.get(os.path.basename(path))
        if taken and not os.path.exists(os.path.join(root, path)):
            clashes.append(f"{path} is new but its basename exists at {taken}")
    if not clashes:
        return 0
    print("\n".join(clashes), file=sys.stderr)
    return 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
