"""The commands a leaf prompt gives for running suites, read from the repository at <root>
(PRD 031.4's LG28, LG29; #4263).

Interface:
  own_tree(root=".")      whether <root> is veri's own tree: `skills/tdd/scripts/tests/py` is a directory there.
  own_tree_at(commit, root=".")
                          whether <commit> (a commit git resolves in <root>) is veri's own tree: it holds
                          `skills/tdd/scripts/tests/py` as a directory. What a script a verifier runs decides by, so a
                          working tree that adds the directory gains nothing.
  quiet_prefix(root=".", claude_md=None)
                          the argv prefix `["sh", "-c", '<quiet> "$@"', "sh"]` running the command <root>'s CLAUDE.md
                          declares as `veri: quiet test files: <quiet>` over the paths appended to it, or None when it
                          declares none (never the inferred default) or <root> is veri's own tree. With <claude_md>
                          (bytes, a branch base's CLAUDE.md) that text is read in place of the file.
  base_claude_md(root=".", branch_base="")
                          CLAUDE.md's bytes as they stood at <branch_base> (b"" when that commit holds none), or None
                          when nothing is read there (no <branch_base>, or <root> is no git tree). Raises BaseUnresolved
                          as run_lines does. What build-verify-prompt.sh reads the `veri: lint:` line from.
  full_line(root=".", branch_base="")
                          the full test command a verifier runs, as bytes: the repo's all-tier command, read as
                          run_lines reads its lines (at <branch_base>, declared lines only, BaseUnresolved likewise),
                          or `the test command` when it declares none. veri's own tree declares `make test`.
  run_lines(root=".", branch_base="")
                          (changed, one) as bytes: the command running the test files affected-suites.sh printed,
                          and the
                          one invocation for a single suite. In veri's own tree today's `make test TESTS="…"` text;
                          elsewhere the repo's `veri: one test file:` command run once per path through `sh -c`, `"$1"`
                          being that path, or, when the repo declares none, its fast command once for both, so a
                          leaf never times a broader tier; only a repo declaring neither gets its all-tier command.
                          A declared quiet command (quiet_prefix) replaces the changed one, run once over every path.
                          With <branch_base> (a hex commit name), the `veri: one test file:`, `veri: fast tests:`,
                          `veri: all tests:` and `veri: quiet test files:` lines are read from CLAUDE.md as it stood at
                          that commit, never from the working tree's, and only a line it declares counts: no tier is
                          inferred from other files.
                          Whether <root> is veri's own tree is then read at <branch_base> too (the directory is in
                          that commit), so a branch that adds it gains nothing. Raises BaseUnresolved when <root> is a
                          git tree in which <branch_base> names no commit; a commit holding no CLAUDE.md reads as one
                          declaring nothing.

Blindness: the only inputs are <root>'s files, as detect-test-command.sh reads them (its CLAUDE.md lines first), and
the CLAUDE.md git holds at <branch_base>, a commit name build-verify-prompt.sh already takes and hex-checks. No other
argument, option or environment variable reaches the result, so a builder that fills it gains no input.
"""
import os
import shlex

import detect_test_command
import git

PYTEST_DIR = "skills/tdd/scripts/tests/py"
OWN = (b'make test TESTS="<those paths>"', b'make test TESTS="<pytest file or node id>"')
UNDECLARED = b"the test command"


def own_tree(root="."):
    return os.path.isdir(os.path.join(root, PYTEST_DIR))


def quiet_prefix(root=".", claude_md=None):
    claude = os.path.join(root, "CLAUDE.md")
    if claude_md is None and (own_tree(root) or not os.path.isfile(claude)):
        return None
    try:
        if claude_md is None:
            detect_test_command.answer_from_file(claude, b"veri: quiet test files:")
        for line in (claude_md or b"").split(b"\n"):
            detect_test_command.answer_from(line, b"veri: quiet test files:")
    except detect_test_command.Answer as found:
        return ["sh", "-c", '%s "$@"' % os.fsdecode(found.command), "sh"]
    return None


class BaseUnresolved(Exception):
    """<branch_base> names no commit git can resolve in <root>."""


def _at_base(branch_base, root):
    """(CLAUDE.md's bytes, b"" when it holds none; whether PYTEST_DIR is a directory) at <branch_base>, or None when
    nothing is read there: no <branch_base>, or <root> is no git tree."""
    if not branch_base or not os.path.exists(os.path.join(root, ".git")):
        return None
    if not git.ok("rev-parse", "--verify", "--quiet", f"{branch_base}^{{commit}}", cwd=root):
        raise BaseUnresolved(branch_base)
    shown = git.git("show", f"{branch_base}:./CLAUDE.md", cwd=root, capture_output=True)
    return shown.stdout if shown.returncode == 0 else b"", own_tree_at(branch_base, root)


def own_tree_at(commit, root="."):
    kind = git.git("cat-file", "-t", f"{commit}:{PYTEST_DIR}", cwd=root, capture_output=True)
    return kind.stdout.strip() == b"tree"


def base_claude_md(root=".", branch_base=""):
    at_base = _at_base(branch_base, root)
    return None if at_base is None else at_base[0]


def full_line(root=".", branch_base=""):
    return detect_test_command.resolved("all", None, root, base_claude_md(root, branch_base)) or UNDECLARED


def run_lines(root=".", branch_base=""):
    at_base = _at_base(branch_base, root)
    if own_tree(root) if at_base is None else at_base[1]:
        return OWN
    claude_md = None if at_base is None else at_base[0]
    one = detect_test_command.resolved("one test file", None, root, claude_md)
    if one is None:
        changed = single = (detect_test_command.resolved("fast", None, root, claude_md)
                            or detect_test_command.resolved("all", None, root, claude_md) or UNDECLARED)
    else:
        command = os.fsdecode(one)
        loop = 'for f; do set -- "$f"; %s || s=$?; done; exit ${s:-0}' % command
        changed = os.fsencode("sh -c %s sh <those paths>" % shlex.quote(loop))
        single = os.fsencode('sh -c %s sh "<test file>"' % shlex.quote(command))
    quiet = quiet_prefix(root, claude_md)
    if quiet:
        changed = os.fsencode("%s <those paths>" % shlex.join(quiet))
    return changed, single
