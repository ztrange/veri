"""build-develop-prompt.sh's argument checks and rendering, run in-process."""
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
REVISE_PHASES = ("red", "green", "refactor", "diff")
WANT = {"red": 4, "green": 7, "refactor": 5, "cover": 4, "transform": 4, "diff": 5, "structural": 5,
        "predicate": 5, "revise": 6, "reconcile": 6, "exhausted": 5, "over-budget": 6, "rebase": 7,
        "replaces-report": 6, "red-contradicted": 5, "red-repair": 6, "red-missing": 5, "red-supersede": 6,
        **dict.fromkeys(INTERFACE_PHASES, 4)}
WANT_PHASES = "|".join(PHASES)
REVISABLE_PHASES = REVISE_PHASES + INTERFACE_PHASES
GREEN_FREEZE_RULE = (
    "\n\n**Do not modify the test.** Not its assertions, not its inputs, not its name. Making the\n"
    "bar easier to clear is not clearing it: a pass bought by weakening, skipping or deleting\n"
    "the case is a rejected step. If the test itself looks wrong, say so in your report as one\n"
    "`WRONG_TEST: <why>` line and stop \u2014 do not edit it.").encode()
GUARD_SUBJECT_GRANT = (
    "\n\n**One exception: the step's guard-subject file.** The step names it in its `\u27e6guard-subject: <path>\u27e7` marker:\n"
    "you may edit that file, and no other test file. The case Red wrote stays frozen.").encode()
REPAIR_TEST_EDIT = (
    "\n\n**You may edit the failing test.** This step repairs a full run, and the fix is often an edit to the\n"
    "test file that run left red: edit that file, only as far as the repair needs. Every other test stays\n"
    "frozen. Making the bar easier to clear is not clearing it: a pass bought by weakening, skipping or\n"
    "deleting a case the repair does not require is a rejected step.").encode()
TEST_REWRITE_GRANT = (
    "**A rewritten test is a new test, and owes a new prediction**: predict its failure\n"
    "   before you run any suite, in `.tdd/red-prediction.md` \u2014 which assertion fires first against the unmodified\n"
    "   production code, the observed-versus-expected values it fires on, and the shape of the\n"
    "   message the suite will print \u2014 then run, saving the run's output to `.tdd/red-run-output.txt`, and compare what it printed against that\n"
    "   prediction; never adjust the prediction to fit what you saw. The leaf whose attempt was\n"
    "   rejected predicted a different test, so there is nothing here for you to inherit.").encode()
WRONG_TEST_REPORT = (
    "\n\nor, when the green you are redoing has a test that looks wrong, those lines replaced by one:\n\n"
    "WRONG_TEST: <why the test looks wrong>\n\n"
    "Name in that line the existing test case the step's criterion contradicts.\n\n"
    "or, when older cases fail only because the step supersedes what they pin, those lines replaced by\n"
    "one per such case:\n\n"
    "SUPERSEDED: <the older case>\n\n"
    "A case the step's change does not supersede is a `WRONG_TEST:` line, never a `SUPERSEDED:` one.").encode()
WRONG_TEST_FORMAT = (
    "\n\nREPORT-FORMAT revise-wrong-test | keys WRONG_TEST: SUPERSEDED: | suite exempt: the test is wrong, "
    "so nothing was changed and no suite ran").encode()
TEST_REWRITE_NONE = b"**Leave the test files as they are**: this phase has no test of its own to redo."
TEST_MOVE_CONTRACT_A = (
    "**Move the tests off the old interface, as contract-a does**: rewrite or delete only the tests the\n"
    "   rejection names that still exercise it. No new failing test is written, so no prediction is owed.").encode()
WANT_REVISE_PHASES = "|".join(REVISABLE_PHASES)
HERE = paths.scripts_of(__file__)
NODE_ID_RULE = (b"The test id is the pytest node id, `<path from the repository root>::<test name>`, "
                b"and the line starts at column 0 with no bullet or other prefix.")
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
    if phase == "red" and carries_mark(markers, "ci-repair"):
        marked["CI_REPAIR"] = f"{prompts}/_develop-red-ci-repair.md"
    if "green" in (phase, revised_phase):
        if replaces_case:
            marked["REPLACES_CASE"] = f"{prompts}/_develop-green-replaces-case.md"
        if carries_mark(markers, "suite-repair"):
            marked["SUITE_REPAIR"] = f"{prompts}/_develop-green-suite-repair.md"
        if carries_mark(markers, "fixture-repair"):
            marked["FIXTURE_REPAIR"] = f"{prompts}/_develop-green-fixture-repair.md"
    if revised_phase in INTERFACE_PHASES:
        frozen = "production" if revised_phase == "contract-a" else "test"
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
    values["NODE_ID_RULE"] = NODE_ID_RULE
    values["RED_CASES"] = (b"One criterion, one case \xe2\x80\x94 no extra cases, and no generality the step does\n"
                           b"not ask for.")
    values["RED_LEAD"] = b"Add exactly **ONE** new failing test case, and write **NO** production code."
    if phase == "revise":
        values["RED_CASES"] = b""
    if "red" in (phase, revised_phase) and replaces_case:
        values["RED_LEAD"] = b"Add the replacement test cases the step names, and write **NO** production code."
        values["RED_CASES"] = (b"\n\n" if phase == "revise" else b"") + (
            b"This step replaces cases, so it is not one criterion, one case: write one pytest replacement\n"
            b"case for each bash case the step named, each in its own `def test_...`, no extra cases, and no\n"
            b"generality the step does not ask for. For each of them, report one line\n"
            b"`REPLACES: <case name> => <pytest test id>` for each case the step named, the case name\n"
            b"exactly as the step spells it, without the quote characters the step wraps it in. " + NODE_ID_RULE)
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
    values["TEST_REWRITE"] = {"red": TEST_REWRITE_GRANT, "contract-a": TEST_MOVE_CONTRACT_A}.get(revised_phase, TEST_REWRITE_NONE)
    repair = carries_mark(markers, "suite-repair") or carries_mark(markers, "ci-repair")
    if "green" in (phase, revised_phase):
        values["FREEZE_RULE"] = REPAIR_TEST_EDIT if repair else GREEN_FREEZE_RULE
        if not repair and "\u27e6guard-subject: " in markers:
            values["FREEZE_RULE"] += GUARD_SUBJECT_GRANT
    if revised_phase == "green" and repair:
        values["TEST_REWRITE"] = REPAIR_TEST_EDIT.lstrip(b"\n")
    if revised_phase == "green":
        values["WRONG_TEST_REPORT"] = WRONG_TEST_REPORT
        values["WRONG_TEST_FORMAT"] = WRONG_TEST_FORMAT
    try:
        text = _expand(_read(paths[0]), prompts_b)
        values["SHARED"] = _expand(_read(paths[1]), prompts_b)
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
    for name, value in values.items():
        text = text.replace(b"{{" + name.encode() + b"}}", value)
    run_state = os.fsencode(os.path.join(event.toplevel() or os.getcwd(), ".tdd"))
    for name in (b"red-prediction.md", b"red-run-output.txt"):
        text = text.replace(b"`.tdd/" + name + b"`", b"`" + run_state + b"/" + name + b"`")
    sys.stdout.buffer.write(text + b"\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
