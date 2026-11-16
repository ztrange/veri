"""stack-branch.sh's logic, run in-process: the stack branch a repository's CLAUDE.md names."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import entry

USAGE = "usage: stack-branch.sh [repo-root]"
MARKER = "veri: stack branch:"


def stated_line(path):
    """The first line of <path> stating MARKER outside a backtick span, and the value after it, backticks unwrapped:
    (line, value), or None when no line states it or the file cannot be read."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError:
        return None
    for line in lines:
        rest, seen = line, ""
        while MARKER in rest:
            before, rest = rest.split(MARKER, 1)
            seen += before
            if seen.count("`") % 2 == 0:
                value = rest.strip()
                if value.startswith("`"):
                    value = value[1:].split("`", 1)[0].strip()
                return line, value
            seen += MARKER
    return None


def named(root):
    """The stack branch <root>'s CLAUDE.md names, or None when it names none."""
    stated = stated_line(os.path.join(root, "CLAUDE.md"))
    if stated is None:
        return None
    return stated[1]


def main(argv):
    if len(argv) > 1:
        return entry.refuse(usage=USAGE)
    name = named(argv[0] if argv and argv[0] else ".")
    if name is None:
        return 3
    sys.stdout.write(name + "\n")
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
