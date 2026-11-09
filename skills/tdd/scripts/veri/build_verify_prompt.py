"""build-verify-prompt.sh's argument checks and rendering, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import itertools
import os
import paths
import re
import sys

import event_log
from entry import write
from ledger import carries_mark, ledger_steps, trailing_markers
from replaces_case import is_replaces_case_step

PHASES = ("red", "green", "refactor", "pin", "plan", "rebase", "transform", "diff")
INTERFACE_PHASES = ("expand", "cover-new", "migrate", "contract-a", "contract-b")
VERIFY_ONLY_PHASES = ("beside", "dual-stub")
WANT_PHASES = "|".join(PHASES + INTERFACE_PHASES)
NEEDS = {"green": {"fast-cmd"}, "refactor": {"fast-cmd", "base-sha"}, "diff": {"fast-cmd"},
         "transform": {"base-sha"}, **dict.fromkeys(INTERFACE_PHASES + VERIFY_ONLY_PHASES, {"fast-cmd", "base-sha"})}
HERE = paths.scripts_of(__file__)
USAGE = ("usage: build-verify-prompt.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] [--supersede-base <sha>]"
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


def _refuse(message=None):
    if message is not None:
        write(sys.stderr, message, before=False, after=False)
    write(sys.stderr, USAGE, before=False, after=False)
    return 2


def _read(path):
    with open(path, "rb") as f:
        return f.read().rstrip(b"\n")


def _spec_text(path):
    try:
        return _read(path)
    except OSError:
        return b""


def _has_heading(text, heading):
    return re.search(rb"^## " + heading + rb"[ \t\r\v\f]*$", text, re.M) is not None


class _IncludeRefused(Exception):
    pass


def _expand(text, prompts, chain=()):
    out = b""
    while (match := re.search(rb"\{\{INCLUDE:([^}]*)\}\}", text)):
        part = prompts + b"/" + match[1]
        out += text[:match.start()]
        text = text[match.end():]
        if not os.access(part, os.R_OK):
            raise _IncludeRefused(b"missing partial: " + part)
        if part in chain:
            raise _IncludeRefused(b"partial includes itself: " + part)
        try:
            content = _read(part)
        except IsADirectoryError:
            sys.stderr.buffer.write(b"cat: " + part + b": Is a directory\n")
            content = b""
        out += _expand(content, prompts, chain + (part,))
    return out + text


def _later_steps(ledger, step_arg):
    unchecked = [step[6] for step in ledger_steps(_read(ledger).decode()) if step[1] == "open"]
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
    options = {"--step": "", "--fast-cmd": "", "--branch-base": "", "--ledger": "", "--supersede-base": ""}
    while argv[:1] and argv[0] in options:
        if len(argv) < 2 or not argv[1]:
            return _refuse(f"build-verify-prompt: {argv[0]} needs a value")
        options[argv[0]] = argv[1]
        argv = argv[2:]
    if len(argv) < 3 or not all(argv[:3]):
        return _refuse()
    if len(argv) > 4:
        return _refuse("build-verify-prompt: too many arguments")
    base = options["--supersede-base"]
    if base and not _HEX_SHA.fullmatch(base):
        return _refuse(f"build-verify-prompt: --supersede-base needs 7-40 lowercase hex characters, got '{base}'")
    code, out = build(options["--step"], options["--fast-cmd"], *argv, branch_base=options["--branch-base"],
                      ledger=options["--ledger"], supersede_base=options["--supersede-base"])
    sys.stdout.buffer.write(out)
    return code


_HEX_SHA = re.compile(r"[0-9a-f]{7,40}")


def _refused(message=None):
    return _refuse(message), b""


def build(step_arg, fast_cmd, phase, spec_arg, test_path, test_id="", branch_base="", ledger="", supersede_base=""):
    if branch_base and not _HEX_SHA.fullmatch(branch_base):
        return _refused(f"build-verify-prompt: --branch-base needs 7-40 lowercase hex characters, got '{branch_base}'")
    if phase not in PHASES + INTERFACE_PHASES + VERIFY_ONLY_PHASES:
        return _refused(f"build-verify-prompt: unknown phase '{phase}' (want {WANT_PHASES})")
    if "fast-cmd" in NEEDS.get(phase, ()) and not fast_cmd:
        return _refused(f"build-verify-prompt: {phase} needs --fast-cmd '<fast-tier test command>'")
    if phase == "pin" and not branch_base:
        return _refused("build-verify-prompt: pin needs --branch-base '<sha>'")
    fourth = test_id
    if phase == "diff":
        if not step_arg:
            return _refused("build-verify-prompt: diff needs --step '<STEP>'")
        shas = (("<step-base-sha>", "STEP_BASE_SHA", fourth), ("<base-sha>", "BASE_SHA", test_path))
    elif "base-sha" in NEEDS.get(phase, ()):
        shas = (("<base-sha>", "BASE_SHA", fourth),)
    elif phase == "rebase":
        shas = (("<onto-sha> <pre-rebase-sha>", "ONTO_SHA", test_path),
                ("<onto-sha> <pre-rebase-sha>", "PRE_REBASE_SHA", fourth))
    else:
        shas = ()
    slots = {"BASE_SHA": fourth, "STEP_BASE_SHA": "", "ONTO_SHA": "", "PRE_REBASE_SHA": ""}
    for label, slot, value in shas:
        if not _HEX_SHA.fullmatch(value):
            return _refused(f"build-verify-prompt: {phase} needs {label} as 7-40 lowercase hex characters, got '{value}'")
        slots[slot] = value
    prompts = f"{HERE}/prompts"
    spec = spec_arg
    optional = {}
    spec_text = _spec_text(spec)
    if _has_heading(spec_text, b"Bug"):
        optional["BUG_REPRODUCTION"] = f"{prompts}/_verify-red-bug.md"
    if phase == "plan" and _has_heading(spec_text, b"Refactor"):
        optional["REFACTOR_PLAN"] = f"{prompts}/_verify-plan-refactor.md"
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
    values = dict.fromkeys(("BUG_REPRODUCTION", "REFACTOR_PLAN", "RED_FAST_CHECK", *GREEN_PARAGRAPHS, "LEDGER"), b"")
    try:
        template = _expand(_read(paths[0]), prompts_b)
        shared = _expand(_read(paths[1]), prompts_b)
        for placeholder, path in optional.items():
            values[placeholder] = _read(path)
            if placeholder in GREEN_PARAGRAPHS:
                values[placeholder] = _expand(b"\n\n" + values[placeholder], prompts_b)
            elif placeholder == "RED_FAST_CHECK":
                values[placeholder] = b"\n\n" + values[placeholder].rstrip(b"\n")
    except _IncludeRefused as refusal:
        sys.stderr.buffer.write(refusal.args[0] + b"\n")
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
    written = b"**one new failing test**"
    if phase == "red" and is_replaces_case_step(step_arg):
        written = (b"**one replacement case per named case** (judge each of them, not only the target test)")
    number = 5 if phase in ("expand", "cover-new", "migrate") else 4
    for placeholder, value in ((b"LAST_PHASE_CHECK", _last_phase_check(step_arg, phase, number)),
                               (b"RED_WRITTEN", written), (b"SHARED", shared), (b"STEP", step_block), (b"ISSUE_SPEC", _read(spec)),
                               *((placeholder.encode(), value) for placeholder, value in values.items()),
                               (b"TEST_PATH", os.fsencode(test_path)),
                               (b"TARGET_TEST", os.fsencode(fourth or "the target test")),
                               (b"BASE_SHA", os.fsencode(slots["BASE_SHA"])),
                               (b"STEP_BASE_SHA", os.fsencode(slots["STEP_BASE_SHA"])),
                               (b"BRANCH_BASE", os.fsencode(branch_base)),
                               (b"FAST_CMD", os.fsencode(fast_cmd)),
                               (b"ONTO_SHA", os.fsencode(slots["ONTO_SHA"])),
                               (b"PRE_REBASE_SHA", os.fsencode(slots["PRE_REBASE_SHA"])),
                               (b"TIMED_TEST_RUN", os.fsencode(f"{HERE}/timed-test-run.sh")),
                               (b"MUTATION_PROBE", os.fsencode(f"{HERE}/mutation-probe.sh"))):
        out = out.replace(b"{{" + placeholder + b"}}", value)
    if phase == "diff":
        out += _author_less_block(os.environ.get("VERI_ISSUE", ""))
    return 0, out + b"\n"


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
