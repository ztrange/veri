"""build-verify-prompt.sh's argument checks and rendering, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import itertools
import os
import paths
import re
import sys

import case_reader
import detect_test_command
import event_log
import git
import run_line
import tunables
from entry import write
from prompt_template import IncludeRefused, expand_includes, fill, has_heading, read as _read, spec_text_of
from ledger import INTERFACE_PHASES, carries_mark, ledger_steps, trailing_markers
from replaces_case import is_replaces_case_step

PHASES = ("red", "green", "refactor", "pin", "plan", "rebase", "transform", "diff", "surround", "break")
VERIFY_ONLY_PHASES = ("beside", "dual-stub")
WANT_PHASES = "|".join(PHASES + INTERFACE_PHASES)
NEEDS = {"green": {"fast-cmd"}, "refactor": {"fast-cmd", "base-sha"}, "break": {"fast-cmd", "base-sha"}, "diff": {"fast-cmd"},
         "transform": {"fast-cmd", "base-sha"}, **dict.fromkeys(INTERFACE_PHASES + VERIFY_ONLY_PHASES, {"fast-cmd", "base-sha"})}
HERE = paths.scripts_of(__file__)
USAGE = ("usage: build-verify-prompt.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] [--supersede-base <sha>]"
         " [--step-green <sha>]"
         " <phase> <issue-spec-file> <test-path> [<target-test-id>]")
GREEN_PARAGRAPHS = {"REPLACES_CASE": "replaces-case", "SUITE_REPAIR": "suite-repair",
                    "CI_REPAIR": "ci-repair", "FIXTURE_REPAIR": "fixture-repair"}


def _last_phase_check(step_arg, phase, number):
    listed = re.search(r"⟦phases:([^⟧]*)⟧", step_arg)
    if not listed or listed[1].split(",")[-1].strip() != phase:
        return b""
    return (f"\n{number}. **Every case the step asks for exists:** each test case the step's text asks for "
            "exists at `HEAD` and passes, even when this phase made no commit. REJECT, naming "
            "the missing case, when one is absent.").encode()


def refuse(message=None):
    if message is not None:
        write(sys.stderr, message, before=False, after=False)
    write(sys.stderr, USAGE, before=False, after=False)
    return 2


def _later_steps(ledger, step_arg):
    unchecked = [step.text for step in ledger_steps(_read(ledger).decode()) if step.state == "open"]
    return list(itertools.dropwhile(lambda text: text != step_arg, unchecked))[1:]


def _author_less_block(issue):
    try:
        events = event_log.read_events(".tdd/events.jsonl", skip_unreadable=True)
    except OSError:
        return b""
    units = sorted({e["unit"] for e in events if e.get("event") == "skill-edit-no-author"
                    and str(e.get("issue")) == issue and e.get("unit")})
    if not units:
        return b""
    return ("\n\n### Units whose prose was already present\n\n"
            "The prose of these units was already present before this run, so a unit with no prose diff "
            "is not a shortfall:\n\n" + "\n".join(f"- {unit}" for unit in units)).encode()


def main(argv):
    options = {"--step": "", "--fast-cmd": "", "--branch-base": "", "--ledger": "", "--supersede-base": "",
               "--step-green": ""}
    while argv[:1] and argv[0] in options:
        if len(argv) < 2 or not argv[1]:
            return refuse(f"build-verify-prompt: {argv[0]} needs a value")
        options[argv[0]] = argv[1]
        argv = argv[2:]
    if len(argv) < 3 or not all(argv[:3]):
        return refuse()
    if len(argv) > 4:
        return refuse("build-verify-prompt: too many arguments")
    if argv[0] == "surround" and options["--ledger"]:
        return refuse("build-verify-prompt: surround takes the pin phase's inputs, and --ledger is not one")
    base = options["--supersede-base"]
    if base and not HEX_SHA.fullmatch(base):
        return refuse(f"build-verify-prompt: --supersede-base needs 7-40 lowercase hex characters, got '{base}'")
    code, out = build(options["--step"], options["--fast-cmd"], *argv, branch_base=options["--branch-base"],
                      ledger=options["--ledger"], supersede_base=options["--supersede-base"],
                      step_green=options["--step-green"])
    sys.stdout.buffer.write(out)
    return code


HEX_SHA = re.compile(r"[0-9a-f]{7,40}")


TOUCHING_HEADING = b"### Test cases touching the files the plan names"
SKIPPED_DIRS = {".git", ".tdd", ".venv", "node_modules"}


def _tree_files():
    """The files git tracks under the current directory, relative to it, none under a SKIPPED_DIRS directory."""
    for path in sorted(name for name in git.out("ls-files", "-z").split("\0") if name):
        if not SKIPPED_DIRS.intersection(path.split("/")[:-1]):
            yield path


READ_LANGUAGES = re.compile(r"\.(?:py|go)$|" + case_reader.JS_EXT)
TEST_LOOKING = re.compile(r"(?i:(?:^|[._-])(?:test|spec)s?(?:[._-]|$))|Tests?\.\w+$")
UNREADABLE = "unreadable"
NO_TOUCHING = "No test case touches a file the plan names."
NONE_READ = ("No case name could be read from the test files touching the files the plan names; "
             "read these in the repository:")


def _hits(stems, text):
    return sum(len(re.findall(r"(?<!\w)" + re.escape(stem) + r"(?!\w)", text)) for stem in stems)


def _touching_names(path, stems, full_stems):
    """((rank, names) for the test file at `path`: names [] unless it holds one of `stems` as a whole word, `-` read as
    `_`, and UNREADABLE for a file that cannot be read, or that touches one and whose cases cannot be cut: a call that
    never closes, or a test-looking file in a language the reader does not read. The rank puts first a file holding
    a stem of a path a step gives in full, then the one with more hits."""
    try:
        with open(path, "rb") as handle:
            text = handle.read().decode(errors="replace").replace("-", "_")
    except OSError:
        return (1, 0), UNREADABLE
    hits = _hits(stems, text)
    rank = (0 if _hits(full_stems, text) else 1, -hits)
    if not hits:
        return rank, []
    if not READ_LANGUAGES.search(path):
        return rank, UNREADABLE if TEST_LOOKING.search(os.path.basename(path)) else []
    try:
        return rank, [name for name, _ in case_reader.cut_cases(text)]
    except case_reader.UnclosedCase:
        return rank, UNREADABLE


def _stem(path):
    return os.path.splitext(os.path.basename(path))[0].replace("-", "_")


def _touching_cases(ledger):
    """The section naming, under each touching test file, its case names: computed from the ledger and the tree only."""
    files = list(_tree_files())
    words = {word.rstrip(".") for step in ledger_steps(_read(ledger).decode(errors="replace"))
             for word in re.findall(r"[\w./-]+", step.text)}
    stems = {_stem(path) for path in files if path in words or os.path.basename(path) in words}
    full_stems = {_stem(path) for path in files if path in words}
    candidates = [path for path in files if stems and case_reader.is_test_path(path) and not os.path.islink(path)]
    ranked = sorted(((*_touching_names(path, stems, full_stems), path) for path in candidates),
                    key=lambda found: (found[0], found[2]))
    lines, more, unread_more, room = [], [], 0, int(tunables.get("VERI_PLAN_TOUCHING_CASES"))
    read_any = False
    for _, names, path in ranked:
        if names == UNREADABLE:
            if room > 0:
                lines.append(f"{path}: cases not readable")
                room -= 1
            else:
                unread_more += 1
            continue
        shown, room = names[:room], room - len(names[:room])
        read_any = read_any or bool(names)
        if shown:
            lines += [path, *(f"- {name}" for name in shown), ""]
        if len(names) > len(shown):
            more.append(f"{path}: {len(names) - len(shown)} more cases")
    if unread_more:
        more.append(f"{unread_more} more test files whose cases are not readable")
    listing = "\n".join(lines + more).rstrip("\n")
    if listing and not read_any:
        listing = NONE_READ + "\n\n" + listing
    return TOUCHING_HEADING + b"\n\n" + (listing or NO_TOUCHING).encode()


def _refused(message=None):
    return refuse(message), b""


def build(step_arg, fast_cmd, phase, spec_arg, test_path, test_id="", branch_base="", ledger="", supersede_base="",
          root=".", step_green=""):
    if branch_base and not HEX_SHA.fullmatch(branch_base):
        return _refused(f"build-verify-prompt: --branch-base needs 7-40 lowercase hex characters, got '{branch_base}'")
    if step_green and not HEX_SHA.fullmatch(step_green):
        return _refused(f"build-verify-prompt: --step-green needs 7-40 lowercase hex characters, got '{step_green}'")
    if step_green and phase != "refactor":
        return _refused(f"build-verify-prompt: --step-green is the refactor phase's alone, not {phase}'s")
    if phase not in PHASES + INTERFACE_PHASES + VERIFY_ONLY_PHASES:
        return _refused(f"build-verify-prompt: unknown phase '{phase}' (want {WANT_PHASES})")
    cap = tunables.get("VERI_PLAN_TOUCHING_CASES")
    if phase == "plan" and not tunables.parses("VERI_PLAN_TOUCHING_CASES", cap):
        write(sys.stderr, f"build-verify-prompt: VERI_PLAN_TOUCHING_CASES must be a whole number, got '{cap}'",
              before=False, after=False)
        return 2, b""
    if "fast-cmd" in NEEDS.get(phase, ()) and not fast_cmd:
        return _refused(f"build-verify-prompt: {phase} needs --fast-cmd '<fast-tier test command>'")
    if phase in ("pin", "surround") and not branch_base:
        return _refused(f"build-verify-prompt: {phase} needs --branch-base '<sha>'")
    if phase == "surround" and (fast_cmd or supersede_base):
        return _refused("build-verify-prompt: surround takes the pin phase's inputs, and --fast-cmd and "
                        "--supersede-base are not among them")
    fourth = test_id
    if phase == "diff":
        if not step_arg:
            return _refused("build-verify-prompt: diff needs --step '<STEP>'")
        if fourth:
            return _refused("build-verify-prompt: diff takes <spec-file> <step-base-sha>, and its branch base from "
                            f"--branch-base, not a third positional ('{fourth}')")
        shas = (("<step-base-sha>", "STEP_BASE_SHA", test_path), ("--branch-base", "BASE_SHA", branch_base))
    elif "base-sha" in NEEDS.get(phase, ()):
        shas = (("<base-sha>", "BASE_SHA", fourth),)
    elif phase == "rebase":
        shas = (("<onto-sha> <pre-rebase-sha>", "ONTO_SHA", test_path),
                ("<onto-sha> <pre-rebase-sha>", "PRE_REBASE_SHA", fourth))
    else:
        shas = ()
    slots = {"BASE_SHA": fourth, "STEP_BASE_SHA": "", "ONTO_SHA": "", "PRE_REBASE_SHA": ""}
    for label, slot, value in shas:
        if not HEX_SHA.fullmatch(value):
            return _refused(f"build-verify-prompt: {phase} needs {label} as 7-40 lowercase hex characters, got '{value}'")
        slots[slot] = value
    if phase == "refactor" and not step_green:
        return _refused("build-verify-prompt: refactor needs --step-green <sha>, the step's green tick")
    prompts = f"{HERE}/prompts"
    spec = spec_arg
    optional = {}
    spec_text = spec_text_of(spec)
    if has_heading(spec_text, b"Bug"):
        optional["BUG_REPRODUCTION"] = f"{prompts}/_verify-red-bug.md"
    if phase == "plan" and has_heading(spec_text, b"Refactor"):
        optional["REFACTOR_PLAN"] = f"{prompts}/_verify-plan-refactor.md"
    if phase == "plan" and has_heading(spec_text, b"Legacy"):
        optional["LEGACY_PLAN"] = f"{prompts}/_verify-plan-legacy.md"
    trailing = trailing_markers(step_arg)
    for placeholder, mark in GREEN_PARAGRAPHS.items():
        marked = is_replaces_case_step(step_arg) if mark == "replaces-case" else carries_mark(
            trailing if mark in ("suite-repair", "ci-repair") else step_arg, mark)
        if phase == "green" and marked:
            optional[placeholder] = f"{prompts}/_verify-green-{mark}.md"
    if phase == "red" and fast_cmd:
        optional["RED_FAST_CHECK"] = f"{prompts}/_verify-red-fast.md"
    paths = [f"{prompts}/verify-{phase}.md", f"{prompts}/_shared.md", spec, *optional.values()]
    if phase == "plan":
        optional["LEDGER"] = test_path
        paths.append(test_path)
    for path in paths:
        if not os.access(path, os.R_OK):
            write(sys.stderr, f"build-verify-prompt: cannot read '{path}'", before=False, after=False)
            return 2, b""
    prompts_b = os.fsencode(prompts)
    values = dict.fromkeys(("BUG_REPRODUCTION", "REFACTOR_PLAN", "LEGACY_PLAN", "RED_FAST_CHECK", *GREEN_PARAGRAPHS,
                            "LEDGER"), b"")
    try:
        template = expand_includes(_read(paths[0]), prompts_b)
        shared = expand_includes(_read(paths[1]), prompts_b)
        for placeholder, path in optional.items():
            values[placeholder] = _read(path)
            if placeholder == "LEDGER":
                values[placeholder] += b"\n\n" + _touching_cases(path)
            elif placeholder in GREEN_PARAGRAPHS:
                values[placeholder] = expand_includes(b"\n\n" + values[placeholder], prompts_b)
            elif placeholder == "RED_FAST_CHECK":
                values[placeholder] = b"\n\n" + values[placeholder].rstrip(b"\n")
    except IncludeRefused as refusal:
        sys.stderr.buffer.write(refusal.args[0] + b"\n")
        return 2, b""
    except git.GitFailed as failed:
        reason = " ".join((failed.stderr or "").split()) or str(failed)
        write(sys.stderr, f"build-verify-prompt: git ls-files failed, so no touching cases can be listed: {reason}",
              before=False, after=False)
        return 2, b""
    step = os.fsencode(step_arg)
    step_block = b""
    if step:
        step_block = (b"### The step under judgement\n\n" + step + b"\n\n"
                      b"Your verdict is about this criterion only: the spec below is the whole issue, and its other\n"
                      b"criteria belong to other steps of the plan.\n\n")
        later = _later_steps(ledger, step_arg) if phase == "green" and ledger else []
        if later:
            step_block += (b"### The ledger's later unchecked steps\n\n"
                           + b"\n".join(b"- " + os.fsencode(text) for text in later) + b"\n\n")
    out = template
    supersede = b""
    if supersede_base:
        supersede = _read(f"{prompts}/_verify-diff-supersede.md").replace(
            b"{{SUPERSEDE_BASE}}", os.fsencode(supersede_base)) + b"\n"
    out = out.replace(b"{{SUPERSEDE}}", supersede)
    try:
        run_lines = run_line.run_lines(root, branch_base=branch_base)
    except run_line.BaseUnresolved:
        write(sys.stderr, f"build-verify-prompt: --branch-base '{branch_base}' names no commit git can resolve",
              before=False, after=False)
        return 2, b""
    lint_repair = b""
    if phase == "diff" and carries_mark(trailing, "lint-repair"):
        lint = detect_test_command.resolved("lint", "", root, run_line.base_claude_md(root, branch_base))
        if lint is None:
            write(sys.stderr, "build-verify-prompt: a lint-repair step needs the repo's declared lint command, and its"
                  " CLAUDE.md declares no `veri: lint:` line", before=False, after=False)
            return 2, b""
        lint_repair = _read(f"{prompts}/_verify-diff-lint-repair.md").replace(b"{{LINT_CMD}}", lint) + b"\n"
    out = out.replace(b"{{LINT_REPAIR}}", lint_repair)
    written = b"**one new failing test**"
    if phase == "red" and is_replaces_case_step(step_arg):
        written = (b"**one replacement case per named case** (judge each of them, not only the target test)")
    number = 5 if phase in ("expand", "cover-new", "migrate") else 4
    out = fill(out, ((b"LAST_PHASE_CHECK", _last_phase_check(step_arg, phase, number)),
                               (b"RED_WRITTEN", written), (b"SHARED", shared), (b"STEP", step_block), (b"ISSUE_SPEC", _read(spec)),
                               *((placeholder.encode(), value) for placeholder, value in values.items()),
                               (b"TEST_PATH", os.fsencode(test_path)),
                               (b"TARGET_TEST", os.fsencode(fourth or "the target test")),
                               (b"BASE_SHA", os.fsencode(slots["BASE_SHA"])),
                               (b"STEP_BASE_SHA", os.fsencode(slots["STEP_BASE_SHA"])),
                               # The step's green tick, the refactor's file bounds; the ledger's last commit, BASE_SHA,
                               # is past a re-pin step's commits and bounds only the reviewed range (#4544).
                               (b"STEP_GREEN_SHA", os.fsencode(step_green)),
                               (b"BRANCH_BASE", os.fsencode(branch_base)),
                               (b"FAST_CMD", os.fsencode(fast_cmd)),
                               (b"FULL_CMD", lambda: run_line.full_line(root, branch_base)),
                               (b"ONTO_SHA", os.fsencode(slots["ONTO_SHA"])),
                               (b"PRE_REBASE_SHA", os.fsencode(slots["PRE_REBASE_SHA"])),
                               (b"TIMED_TEST_RUN", os.fsencode(f"{HERE}/timed-test-run.sh")),
                               *zip((b"AFFECTED_RUN_LINE", b"RUN_LINE"), run_lines),
                               (b"MUTATION_PROBE", os.fsencode(f"{HERE}/mutation-probe.sh")),
                               (b"NEAR_DUPLICATES", os.fsencode(f"{HERE}/near-duplicates.sh"))))
    if phase == "diff":
        out += _author_less_block(tunables.read("VERI_ISSUE"))
    return 0, out + b"\n\n" + _read(f"{prompts}/_verify-output-contract.md") + b"\n"


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
