"""suite-reported.sh's computation, run in-process."""
import os
import re
import sys

import event
import leaf_role
import tunables
import report_formats

USAGE = "usage: suite-reported.sh <leaf-name>"


def _exempt_keys(leaf):
    prompts = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "prompts")
    name = "develop-revise-diff" if leaf.startswith("revise-diff-") else leaf
    role = leaf_role.leaf_role(leaf)
    if role and name == leaf:
        name = leaf.split("-", 1)[0] + "-" + role["VERI_PHASE"]

    def expand(text):
        def include(match):
            with open(os.path.join(prompts, match[1]), encoding="utf-8") as part:
                return expand(part.read())
        return re.sub(r"\{\{INCLUDE:([^}]*)\}\}", include, text)

    try:
        with open(os.path.join(prompts, name + ".md"), encoding="utf-8") as prompt:
            declared = report_formats.parse(expand(prompt.read()))
    except (OSError, ValueError):
        return []
    return [f["keys"] for f in declared if f["suite"] == "exempt"]


def main(argv):
    if len(argv) != 1 or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        with open(f".tdd/{argv[0]}.out", encoding="utf-8", errors="replace") as out:
            lines = out.read().splitlines()
        if any(line.startswith("SUITE:") for line in lines):
            return 0
        for keys in _exempt_keys(argv[0]):
            if all(any(line.startswith(key) for line in lines) for key in keys):
                return 0
    except OSError:
        pass
    event.mark("", event.context(tunables.environment()), "report-missing", ["name=" + argv[0], "missing=SUITE"])
    print(f"suite-reported.sh: {argv[0]} left no SUITE: line", file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
