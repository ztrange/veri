"""build-develop-prompt.sh's argument checks and rendering, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import paths
import re
import shlex
import sys

import entry
import event
import event_log
import run_line
import tidy_first
import tunables
from ledger import BEFORE_STATE_GREEN, INTERFACE_PHASES, carries_mark, trailing_markers
from replaces_case import is_replaces_case_step, parse as parse_replaces_case
from entry import write
from prompt_template import IncludeRefused, expand_includes, fill, has_heading, spec_text_of

DEVELOP_INTERFACE_PHASES = INTERFACE_PHASES[:1] + ("beside",) + INTERFACE_PHASES[1:]
PHASES = ("red", "green", "refactor", "cover", "seam", "break", "surround", "transform", "diff", "structural", "predicate", "revise",
          "reconcile", "exhausted", "over-budget", "rebase", "replaces-report", "red-contradicted", "red-repair",
          "red-missing", "red-supersede", "test-quality") + DEVELOP_INTERFACE_PHASES
REVISE_PHASES = ("red", "green", "refactor", "transform", "diff")
WANT = {"red": 4, "green": 7, "refactor": 5, "cover": 4, "seam": 4, "break": 4, "surround": 4, "transform": 4, "diff": 5, "structural": 5,
        "predicate": 5, "revise": 6, "reconcile": 6, "exhausted": 5, "over-budget": 6, "rebase": 7,
        "replaces-report": 6, "red-contradicted": 5, "red-repair": 6, "red-missing": 5, "red-supersede": 6,
        "test-quality": 4,
        **dict.fromkeys(DEVELOP_INTERFACE_PHASES, 4)}
ACCEPTED_WANT = {**WANT, "dual-stub": 4}
WANT_PHASES = "|".join(PHASES + ("dual-stub",))
REVISABLE_PHASES = REVISE_PHASES + DEVELOP_INTERFACE_PHASES + ("dual-stub", "rebase", "surround", "break")
WANT_REVISE_PHASES = "|".join(REVISABLE_PHASES)
HERE = paths.scripts_of(__file__)
ARGUMENT_PLACEHOLDERS = {"<test-path>": "TEST_PATH", "<target-test>": "TARGET_TEST", "<fast-cmd>": "FAST_CMD",
                         "<touched-files>": "TOUCHED_FILES", "<issue-touched-files>": "TOUCHED_FILES",
                         "<branch>": "BRANCH", "<remote-sha>": "REMOTE_SHA", "<spent>": "SPENT", "<budget>": "BUDGET",
                         "<onto-sha>": "ONTO_SHA", "<pre-rebase-sha>": "PRE_REBASE_SHA",
                         "<conflicting-files>": "CONFLICTING_FILES", "<report-file>": "REPORT_FILE",
                         "<case>": "CASE"}
USAGE = f"usage: build-develop-prompt.sh {WANT_PHASES} <issue-spec-file> <step-text> <test-cmd> ..."


def _read(path):
    with open(path, "rb") as f:
        return f.read().replace(b"\0", b"").rstrip(b"\n")


def _without_test_command(spec):
    return b"\n".join(line for line in spec.split(b"\n") if not line.startswith(b"Test command:")).rstrip(b"\n")


def _bullets(cases):
    return "".join(f"\n- {case}" for case in cases)


class Refusal:
    """A refusal: `message` (str or bytes; None for the usage line alone), exit `code` 2, and whether the usage line
    follows (`usage`; the refusals of arguments do, those of rendering do not)."""
    __slots__ = ("message", "code", "usage")

    def __init__(self, message, usage=True):
        self.message = message
        self.code = 2
        self.usage = usage


class Arguments:
    """The checked arguments: `phase`, `revised_phase` ("" unless phase is revise), the `names` each argument after the phase
    goes by (`args` aligned to them, the revised phase already taken off) and `args`."""
    __slots__ = ("phase", "revised_phase", "names", "args")

    def __init__(self, phase, revised_phase, names, args):
        self.phase = phase
        self.revised_phase = revised_phase
        self.names = names
        self.args = args


def arguments(argv):
    """The `Arguments` of argv, or a `Refusal` of the first check it fails; a pure answer, nothing is written.

    The checks run in this order and the order is part of the behaviour: no argument; unknown phase; too few arguments
    for the phase; (revise) an empty then an unknown phase to revise; the first empty required argument by position;
    (over-budget) a non-decimal spent or budget; and last, for revise of red, a verify-pin.reason file whose REASON line
    carries a before-state-green clause. Only that last check reads a file, and it does so before any readability check
    of the files the prompt is built from.
    """
    if not argv:
        return Refusal(None)
    phase = argv[0]
    if phase not in ACCEPTED_WANT:
        return Refusal(f"build-develop-prompt.sh: unknown phase '{phase}' (want {WANT_PHASES})")
    if len(argv) < ACCEPTED_WANT[phase]:
        return Refusal(f"build-develop-prompt: {phase} needs {ACCEPTED_WANT[phase]} arguments, got {len(argv)}")
    args = argv[1:]
    if phase == "test-quality":
        args.insert(1, "-")  # no step: the leaf reads the run's test files, not one step
    revised_phase = ""
    if phase == "revise":
        revised_phase = args.pop(0)
        if not revised_phase:
            return Refusal("build-develop-prompt: missing <phase> being revised")
        if revised_phase not in REVISABLE_PHASES:
            return Refusal(f"build-develop-prompt.sh: unknown phase to revise '{revised_phase}' "
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
        "test-quality": ["<test-file>"],
    }.get(phase, [])
    for index, name in enumerate(names):
        if not (args[index] if index < len(args) else ""):
            return Refusal(f"build-develop-prompt: missing {name}")
    if phase == "over-budget":
        for name, value in zip(names[3:], args[3:]):
            if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", value):
                return Refusal(f"build-develop-prompt: {name} '{value}' is not a non-negative decimal number")
    if (phase == "revise" and revised_phase == "red" and os.path.basename(args[3]) == "verify-pin.reason"
            and any(BEFORE_STATE_GREEN.search(line)
                    for line in _read(args[3]).decode("utf-8", "replace").splitlines()
                    if line.startswith("REASON:"))):
        return Refusal("build-develop-prompt: a verify-pin rejection with a before-state-green clause is routed "
                       "by pin-reject-route.sh, not revised")
    return Arguments(phase, revised_phase, names, args)


class Fragments:
    """The prompt fragments a phase uses, as file names under `scripts/prompts/`:
    `template` (the phase's own file), `bug` (the bug-reproduction file or None), `marked` (slot -> file, ordered: one per
    step marker or revise sub-phase that brings a paragraph), `freeze` (the files the FREEZE_RULE slot joins, ordered),
    `inline` (slot -> file, ordered: spliced where the template carries the slot), `repair` (the step is a suite or ci
    repair) and `replaces_red` (the red cases are a replaces-case step's)."""
    __slots__ = ("template", "bug", "marked", "freeze", "inline", "repair", "replaces_red")


def fragments(phase, revised_phase, step, has_bug):
    """The `Fragments` for a phase, the phase it revises ("" unless revise), the step text and whether the spec has a
    Bug section; a pure function of its inputs, reading no file.

    The orders are behaviour: `marked` is the order its files are checked for readability (after the spec, the phase's
    argument files and the bug file), `inline` the order they are expanded, so the first refusal printed is the first
    in that order. The ci-repair mark counts for the freeze rule only with a green phase, and a revise of a repair
    gets no freeze rule at all."""
    chosen = Fragments()
    chosen.template = f"develop-{'revise-diff' if revised_phase == 'diff' else phase}.md"
    chosen.bug = "_develop-red-bug.md" if has_bug else None
    replaces_case = is_replaces_case_step(step)
    markers = trailing_markers(step)
    marked = {}
    freeze = []
    repair = False
    if "diff" in (phase, revised_phase) and carries_mark(markers, "test-quality"):
        marked["TEST_QUALITY"] = "_develop-diff-test-quality.md"
    if phase == "red" and carries_mark(markers, "ci-repair"):
        marked["CI_REPAIR"] = "_develop-red-ci-repair.md"
    if "green" in (phase, revised_phase):
        if replaces_case:
            marked["REPLACES_CASE"] = "_develop-green-replaces-case.md"
        if carries_mark(markers, "suite-repair"):
            marked["SUITE_REPAIR"] = "_develop-green-suite-repair.md"
        if carries_mark(markers, "fixture-repair"):
            marked["FIXTURE_REPAIR"] = "_develop-green-fixture-repair.md"
        repair = carries_mark(markers, "suite-repair") or carries_mark(markers, "ci-repair")
        if not (repair and phase == "revise"):
            freeze.append("_develop-repair-test-edit.md" if repair else "_develop-green-freeze-rule.md")
        if not repair and "⟦guard-subject: " in markers:
            freeze.append("_develop-guard-subject-grant.md")
    if revised_phase in DEVELOP_INTERFACE_PHASES + ("dual-stub",):
        frozen = "production" if revised_phase in ("cover-new", "contract-a", "dual-stub") else "test"
        marked["FREEZE_RULE"] = f"_develop-revise-freeze-{frozen}.md"
    replaces_red = "red" in (phase, revised_phase) and replaces_case
    inline = {"NODE_ID_RULE": "_develop-node-id-rule.md",
              "RED_LEAD": "_develop-red-lead-replaces-case.md" if replaces_red else "_develop-red-lead.md"}
    if phase != "revise" or replaces_red:
        inline["RED_CASES"] = "_develop-red-cases-replaces-case.md" if replaces_red else "_develop-red-cases.md"
    inline["TEST_REWRITE"] = "_develop-" + {"red": "test-rewrite-grant", "contract-a": "test-move-contract-a",
                                            "surround": "test-rewrite-surround"}.get(revised_phase, "test-rewrite-none") + ".md"
    if revised_phase == "green":
        inline["WRONG_TEST_REPORT"] = "_develop-wrong-test-report.md"
        inline["WRONG_TEST_FORMAT"] = "_develop-wrong-test-format.md"
    chosen.marked, chosen.freeze, chosen.inline = marked, freeze, inline
    chosen.repair, chosen.replaces_red = repair, replaces_red
    return chosen


def render(parsed, chosen):
    """The prompt text (bytes, no trailing newline) for the checked `Arguments` and their `Fragments`, or a `Refusal` with
    no usage line.

    Files are read in this order, and the order is behaviour: every file the prompt is built from is first checked
    readable (template, shared rules, spec, the phase's argument files, then the optional and marked fragments), the
    first unreadable one refused; then the template and shared rules are read, VERI_ISSUE is demanded when the template
    carries ISSUE_NUMBER, the inline fragments are expanded (the first missing partial is refused), and last the
    placeholders are filled in the order of `values`, a later value seeing what an earlier one inserted. A revise
    prompt that renders empty is refused."""
    phase, revised_phase, names, args = parsed.phase, parsed.revised_phase, parsed.names, parsed.args
    prompts = f"{HERE}/prompts"
    spec, step = args[0], args[1]
    paths = [f"{prompts}/{chosen.template}", f"{prompts}/_develop-shared.md", spec]
    optional = {}
    if phase in ("revise", "exhausted", "red-missing"):
        optional["REJECTION_REASON"] = args[3]
    if chosen.bug:
        optional["BUG_REPRODUCTION"] = f"{prompts}/{chosen.bug}"
    if phase == "red-repair":
        paths.append(args[4])
    if phase == "replaces-report":
        optional["MISSING_CASES"] = args[4]
        paths.append(args[3])
    marked = {slot: f"{prompts}/{name}" for slot, name in chosen.marked.items()}
    optional.update(marked)
    paths += optional.values()
    freeze = [f"{prompts}/{name}" for name in chosen.freeze]
    repair = chosen.repair
    for path in paths:
        if not os.access(path, os.R_OK):
            return Refusal(f"build-develop-prompt: cannot read '{path}'", usage=False)
    prompts_b = os.fsencode(prompts)
    values = dict.fromkeys(("SHARED", "ISSUE_SPEC", "BUG_REPRODUCTION", "RED_CASES", "RED_LEAD", "REPLACES_CASE", "SUITE_REPAIR", "FIXTURE_REPAIR", "CI_REPAIR", "TEST_QUALITY", "STEP",
                            "TEST_CMD", "TEST_PATH", "TARGET_TEST", "FAST_CMD", "TIMED_TEST_RUN", "TOUCHED_FILES",
                            "NODE_ID_RULE", "REFACTOR_BUDGET", "REVISE_PHASE", "FREEZE_RULE", "WRONG_TEST_REPORT", "WRONG_TEST_FORMAT", "TEST_REWRITE", "REJECTION_REASON", "BRANCH",
                            "REMOTE_SHA", "SPENT", "BUDGET", "ONTO_SHA", "PRE_REBASE_SHA", "CONFLICTING_FILES", "REPORT_FILE", "MISSING_CASES", "CASE", "CASES", "WRONG_TEST_REASON", "SUPERSEDED_CASES", "ISSUE_NUMBER", "STEP_ARGUMENT",
                            "AFFECTED_RUN_LINE", "RUN_LINE", "TEST_FILES", "SMELL_NAMES", "NEAR_DUPLICATES"), b"")
    for name, value in zip(names[3:], args[3:]):
        if name in ARGUMENT_PLACEHOLDERS:
            values[ARGUMENT_PLACEHOLDERS[name]] = os.fsencode(value)
    if phase == "test-quality":
        values["TEST_FILES"] = os.fsencode(_bullets(args[3:]).lstrip("\n"))
    if phase == "red-supersede":
        values["CASES"] = os.fsencode(_bullets(args[4:]))
    if phase == "red-repair":
        reason = re.search(rb"^WRONG_TEST:[ \t]*(.*)$", _read(args[4]), re.MULTILINE)
        values["WRONG_TEST_REASON"] = reason.group(1) if reason else b""
        if args[5:]:
            values["SUPERSEDED_CASES"] = os.fsencode(
                "\n\nThe step also supersedes these older cases:" + _bullets(args[5:]))
    if phase == "refactor":
        values["REFACTOR_BUDGET"] = os.fsencode(tunables.get("VERI_REFACTOR_BUDGET", unless_empty=True))
        values["NEAR_DUPLICATES"] = b"none"
    values["REVISE_PHASE"] = os.fsencode(revised_phase)
    try:
        text = expand_includes(_read(paths[0]), prompts_b)
        values["SHARED"] = expand_includes(_read(paths[1]), prompts_b)
        def splice(slots):
            done = set()
            for slot in slots:
                if slot in chosen.inline and b"{{" + slot.encode() + b"}}" in text:
                    values[slot] = expand_includes(b"{{INCLUDE:" + chosen.inline[slot].encode() + b"}}", prompts_b)
                    done.add(slot)
            return done
        if b"{{ISSUE_NUMBER}}" in text:
            issue = tunables.read("VERI_ISSUE") or ""
            if entry.whole_number(issue, 0) is None:
                return Refusal("build-develop-prompt: a revise prompt needs VERI_ISSUE, the run's issue number",
                               usage=False)
            values["ISSUE_NUMBER"] = issue.encode()
            try:
                rerouted = [e.get("case") for e in event_log.events(".", "reroute")
                            if e.get("step") == step
                            and e.get("kind") in ("red", "repair", "supersede") and e.get("case")]
            except OSError:
                rerouted = []
            values["STEP_ARGUMENT"] = os.fsencode(" ".join(
                [shlex.quote(step)] + ["--except " + shlex.quote(c) for c in dict.fromkeys(rerouted)]))
        if "RED_CASES" in splice(("NODE_ID_RULE", "RED_LEAD", "RED_CASES", "TEST_REWRITE")) and chosen.replaces_red and phase == "revise":
            values["RED_CASES"] = b"\n\n" + values["RED_CASES"]
        if phase == "revise" and revised_phase != "red":
            text = re.sub(rb"^(?:FAIL_OUTPUT|PREDICTION_NOTE|SETUP):.*\n", b"", text, flags=re.MULTILINE)
            text = text.replace(b" PREDICTION: FAIL_OUTPUT: PREDICTION_NOTE: SETUP:? |", b" PREDICTION: |")
        splice(("WRONG_TEST_REPORT", "WRONG_TEST_FORMAT"))
        for placeholder, path in optional.items():
            values[placeholder] = _read(path)
            if placeholder in marked:
                values[placeholder] = expand_includes(b"\n\n" + values[placeholder], prompts_b)
    except IncludeRefused as refusal:
        return Refusal(refusal.args[0], usage=False)
    named = parse_replaces_case(step) if "REPLACES_CASE" in marked else None
    if named:
        names, suite = named
        listing = "".join(f"\n- {name}" for name in names)
        values["REPLACES_CASE"] += (f"\n\nThe step names these cases in {suite}:{listing}\n\n"
                                    "Delete each listed case whose replacement verify-pin passed, not only the case "
                                    "your target test id replaces.").encode()
    if phase == "green" and "REPLACES_CASE" in marked and len(args) > 6 and args[6]:
        values["REPLACES_CASE"] += b"\n\nStill owed for deletion: " + os.fsencode(args[6])
    values.update(ISSUE_SPEC=_without_test_command(_read(spec)), STEP=os.fsencode(step), TEST_CMD=os.fsencode(args[2]),
                  TIMED_TEST_RUN=os.fsencode(f"{HERE}/timed-test-run.sh"))
    values["AFFECTED_RUN_LINE"], values["RUN_LINE"] = run_line.run_lines()
    if b"{{SMELL_NAMES}}" in text:
        values["SMELL_NAMES"] = tidy_first.catalogue_names().encode()
    lazy = {}
    if freeze:
        lazy["FREEZE_RULE"] = lambda: b"".join(expand_includes(b"\n\n" + _read(path), prompts_b) for path in freeze)
        if revised_phase == "green" and repair:
            lazy["TEST_REWRITE"] = lambda: lazy["FREEZE_RULE"]().lstrip(b"\n")
    if phase == "revise" and revised_phase == "green" and repair:
        lazy["TEST_REWRITE"] = lambda: b""
    try:
        text = fill(text, ((name.encode(), lazy.get(name, value)) for name, value in values.items()))
    except IncludeRefused as refusal:
        return Refusal(refusal.args[0], usage=False)
    run_state = os.fsencode(os.path.join(event.toplevel() or os.getcwd(), ".tdd"))
    for name in (b"red-prediction.md", b"red-run-output.txt"):
        text = text.replace(b"`.tdd/" + name + b"`", b"`" + run_state + b"/" + name + b"`")
    if phase == "revise" and not text.strip():
        return Refusal(f"build-develop-prompt: the revise prompt for '{revised_phase}' is empty", usage=False)
    return text


def main(argv):
    parsed = arguments(argv)
    if isinstance(parsed, Arguments):
        spec, step = parsed.args[0], parsed.args[1]
        chosen = fragments(parsed.phase, parsed.revised_phase, step, has_heading(spec_text_of(spec), b"Bug"))
        parsed = render(parsed, chosen)
    if isinstance(parsed, Refusal):
        if parsed.usage:
            entry.refuse(parsed.message, usage=USAGE)
        else:
            write(sys.stderr, parsed.message, before=False, after=False)
        return parsed.code
    sys.stdout.buffer.write(parsed + b"\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
