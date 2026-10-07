"""build-develop-prompt.sh's argument checks and rendering, run in-process."""
import os
import re
import sys

PHASES = ("red", "green", "refactor", "cover", "transform", "diff", "structural", "predicate", "revise",
          "reconcile", "exhausted", "over-budget", "rebase")
REVISE_PHASES = ("red", "green", "refactor", "diff")
WANT = {"red": 4, "green": 7, "refactor": 5, "cover": 4, "transform": 4, "diff": 5, "structural": 5,
        "predicate": 5, "revise": 6, "reconcile": 6, "exhausted": 5, "over-budget": 6, "rebase": 7}
USAGE = f"build-develop-prompt.sh: usage: {'|'.join(PHASES)} <issue-spec-file> <step-text> <test-cmd> ..."


def _write(stream, text):
    stream.buffer.write(os.fsencode(text + "\n"))


def _refuse(message=None):
    if message is not None:
        _write(sys.stderr, message)
    _write(sys.stderr, USAGE)
    return 2


def main(argv):
    if not argv:
        return _refuse()
    phase = argv[0]
    if phase not in PHASES:
        return _refuse(f"build-develop-prompt.sh: unknown phase '{phase}' (want {'|'.join(PHASES)})")
    if len(argv) < WANT[phase]:
        return _refuse(f"build-develop-prompt: {phase} needs {WANT[phase]} arguments, got {len(argv)}")
    if phase == "revise":
        revised_phase = argv[1]
        if not re.fullmatch(f"({'|'.join(REVISE_PHASES)})", revised_phase):
            return _refuse(f"build-develop-prompt.sh: unknown phase to revise '{revised_phase}' "
                           f"(want {'|'.join(REVISE_PHASES)})")
        if revised_phase == "diff" and not (argv[6] if len(argv) > 6 else ""):
            return _refuse("build-develop-prompt: missing <fast-cmd>")
    return 0
