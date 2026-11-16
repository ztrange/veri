"""stack-branch.sh's logic, run in-process: the stack branch a repository's CLAUDE.md names."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import entry
import git

USAGE = "usage: stack-branch.sh [repo-root]"
MARKER = "veri: stack branch:"


class Refused(Exception):
    """A named stack branch that cannot be one (stack-branch.sh's exit 2); str() names the CLAUDE.md line and why."""


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
    """The stack branch <root>'s CLAUDE.md names, or None when it names none; Refused when the name cannot be a stack."""
    path = os.path.join(root, "CLAUDE.md")
    stated = stated_line(path)
    if stated is None:
        return None
    line, name = stated
    if not name:
        raise Refused("%s: the line '%s' names no branch" % (path, line))
    if git.git("check-ref-format", "--branch", name, cwd=root, capture_output=True, text=True).returncode != 0:
        raise Refused("%s: the line '%s' names a branch git check-ref-format --branch refuses" % (path, line))
    if name == git.default_branch(cwd=root, remote=False):
        raise Refused("%s: the line '%s' names the default branch, and a stack there would be a direct push to it"
                      % (path, line))
    return name


def run_base(root=None, remote=True):
    """(branch, stacked): the one answer to which branch a run is cut from, rebased onto and diffed against. The stack
    branch <root>'s CLAUDE.md names (exit 0 above; root None: the current directory) with stacked True; else
    git.default_branch(root, remote), None when it cannot be told, with stacked False. Raises Refused (exit 2 above)
    for a name that cannot be a stack."""
    stack = named(root or ".")
    if stack:
        return stack, True
    return git.default_branch(cwd=root, remote=remote), False


def main(argv):
    if len(argv) > 1:
        return entry.refuse(usage=USAGE)
    try:
        name = named(argv[0] if argv and argv[0] else ".")
    except Refused as refused:
        return entry.refuse(str(refused), prefix="stack-branch: ")
    if name is None:
        return 3
    sys.stdout.write(name + "\n")
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
