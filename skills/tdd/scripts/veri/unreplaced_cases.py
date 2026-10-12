"""unreplaced-cases.sh's answer: the bash cases a replaces-case step names that have no pytest replacement."""
import re
import subprocess
import sys

import replaces_case

USAGE = "usage: unreplaced-cases.sh"


def exists_at_head(test_id):
    path, _, name = test_id.strip().partition("::")
    shown = subprocess.run(["git", "show", "HEAD:./" + path], capture_output=True, text=True)
    if shown.returncode != 0:
        return True
    return re.search(r"^\s*(?:async\s+)?def " + re.escape(name.split("::")[-1]) + r"\b", shown.stdout, re.M) is not None


def main(argv):
    if len(argv) != 2:
        sys.stderr.write(USAGE + "\n")
        return 2
    step, report = argv
    with open(report, encoding="utf-8") as handle:
        replaced = {
            m.group(1)
            for m in re.finditer(r"^REPLACES: (.*?) => (.*)$", handle.read(), re.M)
            if exists_at_head(m.group(2))
        }
    missing = [name for name in replaces_case.parse(step)[0] if name not in replaced]
    for name in missing:
        print(name)
    return 1 if missing else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
