"""build-develop-prompt.sh's argument checks and rendering, run in-process."""
import os
import re
import sys

from build_verify_prompt import _IncludeRefused, _expand, _has_heading, _spec_text, _write

PHASES = ("red", "green", "refactor", "cover", "transform", "diff", "structural", "predicate", "revise",
          "reconcile", "exhausted", "over-budget", "rebase")
REVISE_PHASES = ("red", "green", "refactor", "diff")
WANT = {"red": 4, "green": 7, "refactor": 5, "cover": 4, "transform": 4, "diff": 5, "structural": 5,
        "predicate": 5, "revise": 6, "reconcile": 6, "exhausted": 5, "over-budget": 6, "rebase": 7}
WANT_PHASES = "|".join(PHASES)
WANT_REVISE_PHASES = "|".join(REVISE_PHASES)
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARGUMENT_PLACEHOLDERS = {"<test-path>": "TEST_PATH", "<target-test>": "TARGET_TEST", "<fast-cmd>": "FAST_CMD",
                         "<touched-files>": "TOUCHED_FILES", "<issue-touched-files>": "TOUCHED_FILES",
                         "<branch>": "BRANCH", "<remote-sha>": "REMOTE_SHA", "<spent>": "SPENT", "<budget>": "BUDGET",
                         "<onto-sha>": "ONTO_SHA", "<pre-rebase-sha>": "PRE_REBASE_SHA",
                         "<conflicting-files>": "CONFLICTING_FILES"}
USAGE = f"build-develop-prompt.sh: usage: {WANT_PHASES} <issue-spec-file> <step-text> <test-cmd> ..."


def _read(path):
    with open(path, "rb") as f:
        return f.read().replace(b"\0", b"").rstrip(b"\n")


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
    if phase == "over-budget":
        for name, value in zip(names[3:], args[3:]):
            if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", value):
                return _refuse(f"build-develop-prompt: {name} '{value}' is not a non-negative decimal number")
    prompts = f"{HERE}/prompts"
    template = "revise-diff" if revised_phase == "diff" else phase
    spec, step = args[0], args[1]
    paths = [f"{prompts}/develop-{template}.md", f"{prompts}/_develop-shared.md", spec]
    optional = {}
    if phase in ("revise", "exhausted"):
        optional["REJECTION_REASON"] = args[3]
    if _has_heading(_spec_text(spec), b"Bug"):
        optional["BUG_REPRODUCTION"] = f"{prompts}/_develop-red-bug.md"
    if "green" in (phase, revised_phase):
        for placeholder, mark in (("REPLACES_CASE", "replaces-case"), ("SUITE_REPAIR", "suite-repair")):
            if f"⟦{mark}⟧" in step:
                optional[placeholder] = f"{prompts}/_develop-green-{mark}.md"
    paths += optional.values()
    for path in paths:
        if not os.access(path, os.R_OK):
            _write(sys.stderr, f"build-develop-prompt: cannot read '{path}'")
            return 2
    prompts_b = os.fsencode(prompts)
    values = dict.fromkeys(("SHARED", "ISSUE_SPEC", "BUG_REPRODUCTION", "REPLACES_CASE", "SUITE_REPAIR", "STEP",
                            "TEST_CMD", "TEST_PATH", "TARGET_TEST", "FAST_CMD", "TIMED_TEST_RUN", "TOUCHED_FILES",
                            "REFACTOR_BUDGET", "REVISE_PHASE", "REJECTION_REASON", "BRANCH", "REMOTE_SHA", "SPENT",
                            "BUDGET", "ONTO_SHA", "PRE_REBASE_SHA", "CONFLICTING_FILES"), b"")
    for name, value in zip(names[3:], args[3:]):
        if name in ARGUMENT_PLACEHOLDERS:
            values[ARGUMENT_PLACEHOLDERS[name]] = os.fsencode(value)
    if phase == "refactor":
        values["REFACTOR_BUDGET"] = os.fsencode(os.environ.get("VERI_REFACTOR_BUDGET") or "5")
    values["REVISE_PHASE"] = os.fsencode(revised_phase)
    try:
        text = _expand(_read(paths[0]), prompts_b)
        values["SHARED"] = _expand(_read(paths[1]), prompts_b)
        for placeholder, path in optional.items():
            values[placeholder] = _read(path)
            if placeholder in ("REPLACES_CASE", "SUITE_REPAIR"):
                values[placeholder] = _expand(b"\n\n" + values[placeholder], prompts_b)
    except _IncludeRefused as refusal:
        sys.stderr.buffer.write(refusal.args[0] + b"\n")
        return 2
    values.update(ISSUE_SPEC=_read(spec), STEP=os.fsencode(step), TEST_CMD=os.fsencode(args[2]),
                  TIMED_TEST_RUN=os.fsencode(f"{HERE}/timed-test-run.sh"))
    for name, value in values.items():
        text = text.replace(b"{{" + name.encode() + b"}}", value)
    sys.stdout.buffer.write(text + b"\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
