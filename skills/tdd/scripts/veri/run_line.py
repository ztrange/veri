"""The commands a leaf prompt gives for running suites, read from the working tree alone (PRD 031.4's LG28, LG29).

Interface:
  own_tree(root=".")      whether <root> is veri's own tree: `skills/tdd/scripts/tests/py` is a directory there.
  quiet_prefix(root=".")  the argv prefix `["sh", "-c", '<quiet> "$@"', "sh"]` running the command <root>'s CLAUDE.md
                          declares as `veri: quiet test files: <quiet>` over the paths appended to it, or None when it
                          declares none (never the inferred default) or <root> is veri's own tree.
  run_lines(root=".")     (changed, one) as bytes: the command running the test files affected-suites.sh printed, and the
                          one invocation for a single suite. In veri's own tree today's `make test TESTS="…"` text;
                          elsewhere the repo's `veri: one test file:` command run once per path through `sh -c`, `"$1"`
                          being that path, or, when the repo declares none, its fast command once for both, so a
                          leaf never times a broader tier; only a repo declaring neither gets its all-tier command.
                          A declared quiet command (quiet_prefix) replaces the changed one, run once over every path.

Blindness: the only input is <root>'s files, as detect-test-command.sh reads them (its CLAUDE.md lines first). No
argument, option or environment variable reaches the result, so a builder that fills it gains no input.
"""
import os
import shlex

import detect_test_command

PYTEST_DIR = "skills/tdd/scripts/tests/py"
OWN = (b'make test TESTS="<those paths>"', b'make test TESTS="<pytest file or node id>"')
UNDECLARED = b"the test command"


def own_tree(root="."):
    return os.path.isdir(os.path.join(root, PYTEST_DIR))


def quiet_prefix(root="."):
    claude = os.path.join(root, "CLAUDE.md")
    if own_tree(root) or not os.path.isfile(claude):
        return None
    try:
        detect_test_command.answer_from_file(claude, b"veri: quiet test files:")
    except detect_test_command.Answer as found:
        return ["sh", "-c", '%s "$@"' % os.fsdecode(found.command), "sh"]
    return None


def run_lines(root="."):
    if own_tree(root):
        return OWN
    one = detect_test_command.resolved("one test file", None, root)
    if one is None:
        changed = single = (detect_test_command.resolved("fast", None, root)
                            or detect_test_command.resolved("all", None, root) or UNDECLARED)
    else:
        command = os.fsdecode(one)
        loop = 'for f; do set -- "$f"; %s || s=$?; done; exit ${s:-0}' % command
        changed = os.fsencode("sh -c %s sh <those paths>" % shlex.quote(loop))
        single = os.fsencode('sh -c %s sh "<test file>"' % shlex.quote(command))
    quiet = quiet_prefix(root)
    if quiet:
        changed = os.fsencode("%s <those paths>" % shlex.join(quiet))
    return changed, single
