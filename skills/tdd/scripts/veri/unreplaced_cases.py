"""unreplaced-cases.sh's answer: the bash cases a replaces-case step names that have no pytest replacement."""
import os
import re
import sys

import replaces_case

USAGE = "usage: unreplaced-cases.sh"


PY_TESTS = "skills/tdd/scripts/tests/py"


def def_pattern(name):
    return r"^\s*(?:async\s+)?def " + re.escape(name) + r"\b"


def bare_name_count(name):
    found = 0
    for root, _, files in os.walk(PY_TESTS):
        for file in files:
            if not file.endswith(".py"):
                continue
            try:
                with open(os.path.join(root, file), encoding="utf-8") as handle:
                    found += len(re.findall(def_pattern(name), handle.read(), re.M))
            except OSError:
                continue
    return found


def is_bare_name(test_id):
    return re.fullmatch(r"\w+", test_id.strip()) is not None


def exists_in_tree(test_id):
    path, sep, name = test_id.strip().partition("::")
    if not sep:
        return is_bare_name(path) and bare_name_count(path.strip()) == 1
    try:
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
    except OSError:
        return False
    return re.search(def_pattern(name.split("::")[-1]), source, re.M) is not None


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
    not_found = set()
    ambiguous = set()
    for report in reports:
        with open(report, encoding="utf-8") as handle:
            for m in re.finditer(r"^(?:[-*] )?REPLACES: (.*?) => (.*)$", handle.read(), re.M):
                if exists_in_tree(m.group(2)):
                    replaced.add(m.group(1))
                    replaced.add(re.sub("^(" + re.escape(quote) + ")(.*)\\1$", r"\2", m.group(1)))
                elif is_bare_name(m.group(2)) and bare_name_count(m.group(2).strip()) == 0:
                    not_found.add(m.group(1))
                elif is_bare_name(m.group(2)) and bare_name_count(m.group(2).strip()) > 1:
                    ambiguous.add(m.group(1))
    missing = [name for name in (parsed[0] if parsed else []) if name not in replaced and unescape(name) not in replaced]
    for name in missing:
        note = ""
        if name in not_found or unescape(name) in not_found:
            note = " (no test of that name was found)"
        elif name in ambiguous or unescape(name) in ambiguous:
            note = " (the test name is ambiguous: several tests of that name exist)"
        print(name + note)
    return 1 if missing else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
