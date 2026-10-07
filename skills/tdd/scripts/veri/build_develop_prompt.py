"""build-develop-prompt.sh's argument checks and rendering, run in-process."""
import os
import re
import sys

PHASES = ("red", "green", "refactor", "cover", "transform", "diff", "structural", "predicate", "revise",
          "reconcile", "exhausted", "over-budget", "rebase")
REVISE_PHASES = ("red", "green", "refactor", "diff")
WANT = {"red": 4, "green": 7, "refactor": 5, "cover": 4, "transform": 4, "diff": 5, "structural": 5,
        "predicate": 5, "revise": 6, "reconcile": 6, "exhausted": 5, "over-budget": 6, "rebase": 7}
WANT_PHASES = "|".join(PHASES)
WANT_REVISE_PHASES = "|".join(REVISE_PHASES)
USAGE = f"build-develop-prompt.sh: usage: {WANT_PHASES} <issue-spec-file> <step-text> <test-cmd> ..."


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
        return _refuse(f"build-develop-prompt.sh: unknown phase '{phase}' (want {WANT_PHASES})")
    if len(argv) < WANT[phase]:
        return _refuse(f"build-develop-prompt: {phase} needs {WANT[phase]} arguments, got {len(argv)}")
    args = argv[1:]
    revised_phase = ""
    if phase == "revise":
        revised_phase = args.pop(0)
        if not revised_phase:
            return _refuse("build-develop-prompt: missing <phase> being revised")
        if not re.fullmatch(f"({WANT_REVISE_PHASES})", revised_phase):
            return _refuse(f"build-develop-prompt.sh: unknown phase to revise '{revised_phase}' "
                           f"(want {WANT_REVISE_PHASES})")
    names = ["<issue-spec-file>", "<step-text>", "<test-cmd>"] + {
        "diff": ["<fast-cmd>"],
        "green": ["<test-path>", "<target-test>", "<fast-cmd>"],
        "structural": ["<issue-touched-files>"],
        "predicate": ["<issue-touched-files>"],
        "refactor": ["<touched-files>"],
        "revise": ["<reason-file>"] + (["<fast-cmd>"] if revised_phase == "diff" else []),
        "exhausted": ["<reason-file>"],
        "reconcile": ["<branch>", "<remote-sha>"],
        "rebase": ["<onto-sha>", "<pre-rebase-sha>", "<conflicting-files>"],
        "over-budget": ["<spent>", "<budget>"],
    }.get(phase, [])
    for index, name in enumerate(names):
        if not (args[index] if index < len(args) else ""):
            return _refuse(f"build-develop-prompt: missing {name}")
    return 0
