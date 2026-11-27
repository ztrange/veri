"""stack-branch.sh's logic, run in-process: the stack branch a repository's CLAUDE.md names."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import os
import re
import sys

import entry
import git

USAGE = "usage: stack-branch.sh [repo-root]"
MARKER = "veri: stack branch:"


class Refused(Exception):
    """A named stack branch that cannot be one (stack-branch.sh's exit 2); str() names the CLAUDE.md line and why."""


def stated_lines(path):
    """Every line of <path> that starts with MARKER, outside a ``` or ~~~ code fence, and the value after it, backticks
    unwrapped: [(line, value)]; empty when none does or the file cannot be read. A quoted (`>`) or indented line does
    not start with the marker, so it names nothing."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError:
        return []
    stated, fence = [], None
    for line in lines:
        opener = line.lstrip()[:3]
        if fence is None and opener in ("```", "~~~"):
            fence = opener
            continue
        if fence is not None:
            if line.lstrip().startswith(fence):
                fence = None
            continue
        if line.startswith(MARKER):
            value = line[len(MARKER):].strip()
            if value.startswith("`"):
                value = value[1:].split("`", 1)[0].strip()
            stated.append((line, value))
    return stated


def default_names(root, remote=True):
    """The default branch as origin states it (`git ls-remote --symref origin HEAD`, bounded by
    VERI_GIT_NETWORK_TIMEOUT, asked only when <remote>) and as refs/remotes/origin/HEAD records it: the set of names
    either gives, empty when neither does."""
    asked = git.network("ls-remote", "--symref", "origin", "HEAD", cwd=root) if remote else None
    remote = git.symref_default(asked.stdout) if asked and asked.returncode == 0 else None
    return {name for name in (remote, git.default_branch(cwd=root, remote=False)) if name}


def named(root, remote=True):
    """The stack branch <root>'s CLAUDE.md names, or None when it names none; Refused when the name cannot be a stack.
    With <remote> False the default branch is read from refs/remotes/origin/HEAD alone, asking origin nothing."""
    path = os.path.join(root, "CLAUDE.md")
    stated = stated_lines(path)
    if not stated:
        return None
    if len(stated) > 1:
        raise Refused("%s: %d lines name a stack branch, so none is the one: %s"
                      % (path, len(stated), "; ".join("'%s'" % line for line, _ in stated)))
    line, name = stated[0]
    if not name:
        raise Refused("%s: the line '%s' names no branch" % (path, line))
    if "<" in name or ">" in name:
        raise Refused("%s: the line '%s' holds a placeholder, not a branch name" % (path, line))
    if name.startswith(("refs/", "origin/")):
        raise Refused("%s: the line '%s' names a ref or a remote-tracking spelling; name the branch alone"
                      % (path, line))
    if git.git("check-ref-format", "--branch", name, cwd=root, capture_output=True, text=True).returncode != 0:
        raise Refused("%s: the line '%s' names a branch git check-ref-format --branch refuses" % (path, line))
    told = default_names(root, remote)
    if not told:
        raise Refused("%s: the line '%s' names a stack, but the default branch cannot be told (no"
                      " refs/remotes/origin/HEAD, and origin gave no answer) — refusing, since the stack may be the"
                      " default branch" % (path, line))
    if name.casefold() in {default.casefold() for default in told}:
        raise Refused("%s: the line '%s' names the default branch, and a stack there would be a direct push to it"
                      % (path, line))
    return name


def ahead(root="."):
    """(stack, default, commits): the stack branch <root>'s CLAUDE.md names, the default branch, and the commits of
    origin/<default>..origin/<stack> as [(sha, subject)], oldest first, read after a fetch of origin; commits is empty
    when origin holds no stack branch. None when CLAUDE.md names no stack. Refused for a name that cannot be a stack,
    a fetch that got no answer, a default branch that cannot be told or that origin lacks, or a log git refuses."""
    stack = named(root)
    if stack is None:
        return None
    fetch = git.network("-C", root, "fetch", "origin")
    if fetch.returncode:
        raise Refused("git fetch origin got no answer (exit %d): %s"
                      % (fetch.returncode, " ".join(fetch.stderr.split())[:200]))
    told = default_names(root)
    if len(told) != 1:
        raise Refused("the default branch cannot be told: origin and refs/remotes/origin/HEAD name %s"
                      % (" and ".join(sorted(told)) or "none"))
    default = told.pop()
    refs = {}
    for name in (default, stack):
        found = git.git("-C", root, "rev-parse", "--verify", "--quiet", "refs/remotes/origin/" + name,
                        capture_output=True, text=True)
        refs[name] = found.stdout.strip() if found.returncode == 0 else None
    if not refs[default]:
        raise Refused("origin has no %s branch, the default branch" % default)
    if not refs[stack]:
        return stack, default, []
    log = git.git("-C", root, "log", "--reverse", "--format=%H %s", "%s..%s" % (refs[default], refs[stack]),
                  capture_output=True, text=True)
    if log.returncode:
        raise Refused("git log origin/%s..origin/%s failed (exit %d): %s" % (
            default, stack, log.returncode, " ".join(log.stderr.split())[:200]))
    return stack, default, [tuple(line.split(" ", 1)) if " " in line else (line, "")
                            for line in log.stdout.splitlines()]


def recorded_base(root):
    """(path, text) of the one `.tdd/issue-<n>-base` file under <root>, the base issue-worktree.sh recorded when it cut
    a stacked run there; None when there is none. Refused when there are several."""
    # issue-<n>-base only: issue-<n>-branch-base, the branch base preflight records, matches the glob too (#4374).
    found = sorted(path for path in glob.glob(os.path.join(glob.escape(root), ".tdd", "issue-*-base"))
                   if re.fullmatch(r"issue-\d+-base", os.path.basename(path)))
    if len(found) > 1:
        raise Refused("several recorded bases, cannot tell which is this run's: %s (the named stack branch is %r)"
                      % (", ".join(found), named(root)))
    if not found:
        return None
    with open(found[0], encoding="utf-8", errors="replace") as f:
        return found[0], f.read()


def run_base(root=None, remote=True):
    """(branch, stacked): the one answer to which branch a run is cut from, rebased onto and diffed against, from an
    observed fact about that run: the stack, with stacked True, only when its cut recorded it (`.tdd/issue-<n>-base`
    under <root>, root None: the current directory) and it is still the stack CLAUDE.md names; else
    git.default_branch(root, remote), exactly as without a stack, None when it cannot be told. Raises Refused for a
    garbled record, one that no longer names the named stack (naming both), or a name that cannot be a stack."""
    record = recorded_base(root or ".")
    if record is None:
        return git.default_branch(cwd=root, remote=remote), False
    path, text = record
    lines = text.splitlines()
    stack = named(root or ".")
    if len(lines) != 1 or not lines[0].strip() or lines[0].strip() != stack:
        raise Refused("%s records the base %r, but the named stack branch is %r — refusing to guess which this run"
                      " is based on" % (path, text.strip()[:80], stack))
    return stack, True


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
