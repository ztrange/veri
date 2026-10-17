"""unreplaced-cases.sh's answer: the bash cases a replaces-case step names that have no pytest replacement."""
import re
import sys

import replaces_case

USAGE = "usage: unreplaced-cases.sh"


def exists_in_tree(test_id):
    path, _, name = test_id.strip().partition("::")
    try:
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
    except OSError:
        return False
    return re.search(r"^\s*(?:async\s+)?def " + re.escape(name.split("::")[-1]) + r"\b", source, re.M) is not None


def unescape(name):
    return re.sub(r"\\([`\"$\\])", r"\1", name)


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(USAGE + "\n")
        return 2
    step, *reports = argv
    parsed = replaces_case.parse(step)
    quote = step[re.search(r"\breplaces (?=['\"`])", step).end()] if parsed else ""
    replaced = set()
    for report in reports:
        with open(report, encoding="utf-8") as handle:
            for m in re.finditer(r"^(?:[-*] )?REPLACES: (.*?) => (.*)$", handle.read(), re.M):
                if exists_in_tree(m.group(2)):
                    replaced.add(m.group(1))
                    replaced.add(re.sub("^(" + re.escape(quote) + ")(.*)\\1$", r"\2", m.group(1)))
    missing = [name for name in (parsed[0] if parsed else []) if name not in replaced and unescape(name) not in replaced]
    for name in missing:
        print(name)
    return 1 if missing else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
