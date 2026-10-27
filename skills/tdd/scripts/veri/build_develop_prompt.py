"""build-develop-prompt.sh's argument checks and rendering, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import paths
import re
import sys

import event
import tunables
from ledger import carries_mark, trailing_markers
from replaces_case import is_replaces_case_step, parse as parse_replaces_case
from entry import write
from build_verify_prompt import INTERFACE_PHASES, _IncludeRefused, _expand, _has_heading, _spec_text

PHASES = ("red", "green", "refactor", "cover", "transform", "diff", "structural", "predicate", "revise",
          "reconcile", "exhausted", "over-budget", "rebase", "replaces-report", "red-contradicted", "red-repair",
          "red-missing", "red-supersede") + INTERFACE_PHASES
REVISE_PHASES = ("red", "green", "refactor", "transform", "diff")
WANT = {"red": 4, "green": 7, "refactor": 5, "cover": 4, "transform": 4, "diff": 5, "structural": 5,
        "predicate": 5, "revise": 6, "reconcile": 6, "exhausted": 5, "over-budget": 6, "rebase": 7,
        "replaces-report": 6, "red-contradicted": 5, "red-repair": 6, "red-missing": 5, "red-supersede": 6,
        **dict.fromkeys(INTERFACE_PHASES, 4)}
WANT_PHASES = "|".join(PHASES)
REVISABLE_PHASES = REVISE_PHASES + INTERFACE_PHASES + ("rebase",)
WANT_REVISE_PHASES = "|".join(REVISABLE_PHASES)
HERE = paths.scripts_of(__file__)
ARGUMENT_PLACEHOLDERS = {"<test-path>": "TEST_PATH", "<target-test>": "TARGET_TEST", "<fast-cmd>": "FAST_CMD",
                         "<touched-files>": "TOUCHED_FILES", "<issue-touched-files>": "TOUCHED_FILES",
                         "<branch>": "BRANCH", "<remote-sha>": "REMOTE_SHA", "<spent>": "SPENT", "<budget>": "BUDGET",
                         "<onto-sha>": "ONTO_SHA", "<pre-rebase-sha>": "PRE_REBASE_SHA",
                         "<conflicting-files>": "CONFLICTING_FILES", "<report-file>": "REPORT_FILE",
                         "<case>": "CASE"}
USAGE = f"build-develop-prompt.sh: usage: {WANT_PHASES} <issue-spec-file> <step-text> <test-cmd> ..."


def _read(path):
    with open(path, "rb") as f:
        return f.read().replace(b"\0", b"").rstrip(b"\n")


def _bullets(cases):
    return "".join(f"\n- {case}" for case in cases)


def _refuse(message=None):
    if message is not None:
        write(sys.stderr, message, before=False, after=False)
    write(sys.stderr, USAGE, before=False, after=False)
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
        if revised_phase not in REVISABLE_PHASES:
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
        "replaces-report": ["<report-file>", "<missing-cases-file>"],
        "red-contradicted": ["<case>"],
        "red-repair": ["<case>", "<report-file>"],
        "red-missing": ["<reason-file>"],
        "red-supersede": ["<report-file>", "<case>"],
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
    if phase in ("revise", "exhausted", "red-missing"):
        optional["REJECTION_REASON"] = args[3]
    if _has_heading(_spec_text(spec), b"Bug"):
        optional["BUG_REPRODUCTION"] = f"{prompts}/_develop-red-bug.md"
    replaces_case = is_replaces_case_step(step)
    markers = trailing_markers(step)
    marked = {}
    freeze = []
    if phase == "red" and carries_mark(markers, "ci-repair"):
        marked["CI_REPAIR"] = f"{prompts}/_develop-red-ci-repair.md"
    if "green" in (phase, revised_phase):
        if replaces_case:
            marked["REPLACES_CASE"] = f"{prompts}/_develop-green-replaces-case.md"
        if carries_mark(markers, "suite-repair"):
            marked["SUITE_REPAIR"] = f"{prompts}/_develop-green-suite-repair.md"
        if carries_mark(markers, "fixture-repair"):
            marked["FIXTURE_REPAIR"] = f"{prompts}/_develop-green-fixture-repair.md"
        repair = carries_mark(markers, "suite-repair") or carries_mark(markers, "ci-repair")
        if not (repair and phase == "revise"):
            freeze.append(f"{prompts}/_develop-{'repair-test-edit' if repair else 'green-freeze-rule'}.md")
        if not repair and "\u27e6guard-subject: " in markers:
            freeze.append(f"{prompts}/_develop-guard-subject-grant.md")
    if revised_phase in INTERFACE_PHASES:
        frozen = "production" if revised_phase in ("cover-new", "contract-a") else "test"
        marked["FREEZE_RULE"] = f"{prompts}/_develop-revise-freeze-{frozen}.md"
    if phase == "red-repair":
        paths.append(args[4])
    if phase == "replaces-report":
        optional["MISSING_CASES"] = args[4]
        paths.append(args[3])
    optional.update(marked)
    paths += optional.values()
    for path in paths:
        if not os.access(path, os.R_OK):
            write(sys.stderr, f"build-develop-prompt: cannot read '{path}'", before=False, after=False)
            return 2
    prompts_b = os.fsencode(prompts)
    values = dict.fromkeys(("SHARED", "ISSUE_SPEC", "BUG_REPRODUCTION", "RED_CASES", "RED_LEAD", "REPLACES_CASE", "SUITE_REPAIR", "FIXTURE_REPAIR", "CI_REPAIR", "STEP",
                            "TEST_CMD", "TEST_PATH", "TARGET_TEST", "FAST_CMD", "TIMED_TEST_RUN", "TOUCHED_FILES",
                            "NODE_ID_RULE", "REFACTOR_BUDGET", "REVISE_PHASE", "FREEZE_RULE", "WRONG_TEST_REPORT", "WRONG_TEST_FORMAT", "TEST_REWRITE", "REJECTION_REASON", "BRANCH",
                            "REMOTE_SHA", "SPENT", "BUDGET", "ONTO_SHA", "PRE_REBASE_SHA", "CONFLICTING_FILES", "REPORT_FILE", "MISSING_CASES", "CASE", "CASES", "WRONG_TEST_REASON", "SUPERSEDED_CASES"), b"")
    for name, value in zip(names[3:], args[3:]):
        if name in ARGUMENT_PLACEHOLDERS:
            values[ARGUMENT_PLACEHOLDERS[name]] = os.fsencode(value)
    if phase == "red-supersede":
        values["CASES"] = os.fsencode(_bullets(args[4:]))
    if phase == "red-repair":
        reason = re.search(rb"^WRONG_TEST:[ \t]*(.*)$", _read(args[4]), re.MULTILINE)
        values["WRONG_TEST_REASON"] = reason.group(1) if reason else b""
        if args[5:]:
            values["SUPERSEDED_CASES"] = os.fsencode(
                "\n\nThe step also supersedes these older cases:" + _bullets(args[5:]))
    if phase == "refactor":
        values["REFACTOR_BUDGET"] = os.fsencode(tunables.read("VERI_REFACTOR_BUDGET") or "5")
    values["REVISE_PHASE"] = os.fsencode(revised_phase)
    try:
        text = _expand(_read(paths[0]), prompts_b)
        values["SHARED"] = _expand(_read(paths[1]), prompts_b)
        def fragment(slot):
            return _expand(b"{{INCLUDE:_develop-" + slot + b".md}}", prompts_b)
        replaces_red = "red" in (phase, revised_phase) and replaces_case
        if b"{{NODE_ID_RULE}}" in text:
            values["NODE_ID_RULE"] = fragment(b"node-id-rule")
        if b"{{RED_LEAD}}" in text:
            values["RED_LEAD"] = fragment(b"red-lead-replaces-case" if replaces_red else b"red-lead")
        if b"{{RED_CASES}}" in text and (phase != "revise" or replaces_red):
            values["RED_CASES"] = fragment(b"red-cases-replaces-case" if replaces_red else b"red-cases")
            if replaces_red and phase == "revise":
                values["RED_CASES"] = b"\n\n" + values["RED_CASES"]
        if b"{{TEST_REWRITE}}" in text:
            values["TEST_REWRITE"] = fragment({"red": b"test-rewrite-grant", "contract-a": b"test-move-contract-a"}
                                              .get(revised_phase, b"test-rewrite-none"))
        if revised_phase == "green":
            if b"{{WRONG_TEST_REPORT}}" in text:
                values["WRONG_TEST_REPORT"] = fragment(b"wrong-test-report")
            if b"{{WRONG_TEST_FORMAT}}" in text:
                values["WRONG_TEST_FORMAT"] = fragment(b"wrong-test-format")
        for placeholder, path in optional.items():
            values[placeholder] = _read(path)
            if placeholder in marked:
                values[placeholder] = _expand(b"\n\n" + values[placeholder], prompts_b)
    except _IncludeRefused as refusal:
        sys.stderr.buffer.write(refusal.args[0] + b"\n")
        return 2
    named = parse_replaces_case(step) if "REPLACES_CASE" in marked else None
    if named:
        names, suite = named
        listing = "".join(f"\n- {name}" for name in names)
        values["REPLACES_CASE"] += (f"\n\nThe step names these cases in {suite}:{listing}\n\n"
                                    "Delete each listed case whose replacement verify-pin passed, not only the case "
                                    "your target test id replaces.").encode()
    if phase == "green" and "REPLACES_CASE" in marked and len(args) > 6 and args[6]:
        values["REPLACES_CASE"] += b"\n\nStill owed for deletion: " + os.fsencode(args[6])
    values.update(ISSUE_SPEC=_read(spec), STEP=os.fsencode(step), TEST_CMD=os.fsencode(args[2]),
                  TIMED_TEST_RUN=os.fsencode(f"{HERE}/timed-test-run.sh"))
    lazy = {}
    if freeze:
        lazy["FREEZE_RULE"] = lambda: b"".join(_expand(b"\n\n" + _read(path), prompts_b) for path in freeze)
        if revised_phase == "green" and repair:
            lazy["TEST_REWRITE"] = lambda: lazy["FREEZE_RULE"]().lstrip(b"\n")
    if phase == "revise" and revised_phase == "green" and repair:
        lazy["TEST_REWRITE"] = lambda: b""
    for name, value in values.items():
        placeholder = b"{{" + name.encode() + b"}}"
        if name in lazy and placeholder in text:
            try:
                value = lazy[name]()
            except _IncludeRefused as refusal:
                sys.stderr.buffer.write(refusal.args[0] + b"\n")
                return 2
        text = text.replace(placeholder, value)
    run_state = os.fsencode(os.path.join(event.toplevel() or os.getcwd(), ".tdd"))
    for name in (b"red-prediction.md", b"red-run-output.txt"):
        text = text.replace(b"`.tdd/" + name + b"`", b"`" + run_state + b"/" + name + b"`")
    if phase == "revise" and not text.strip():
        write(sys.stderr, f"build-develop-prompt: the revise prompt for '{revised_phase}' is empty", before=False, after=False)
        return 2
    sys.stdout.buffer.write(text + b"\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
