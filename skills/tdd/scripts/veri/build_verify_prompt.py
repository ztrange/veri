"""build-verify-prompt.sh's argument checks and rendering, run in-process."""
import os
import paths
import re
import sys

from ledger import carries_mark, trailing_markers
from replaces_case import is_replaces_case_step

PHASES = ("red", "green", "refactor", "pin", "plan", "rebase", "transform", "diff")
INTERFACE_PHASES = ("expand", "migrate", "contract-a", "contract-b")
WANT_PHASES = "|".join(PHASES + INTERFACE_PHASES)
NEEDS = {"green": {"fast-cmd"}, "refactor": {"fast-cmd", "base-sha"}, "diff": {"fast-cmd"},
         "transform": {"base-sha"}, **dict.fromkeys(INTERFACE_PHASES, {"fast-cmd", "base-sha"})}
HERE = paths.scripts_of(__file__)
USAGE = "usage: build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]"
GREEN_PARAGRAPHS = {"REPLACES_CASE": "replaces-case", "SUITE_REPAIR": "suite-repair",
                    "CI_REPAIR": "ci-repair", "FIXTURE_REPAIR": "fixture-repair"}


def _last_phase_check(step_arg, phase, number):
    listed = re.search(r"⟦phases:([^⟧]*)⟧", step_arg)
    if not listed or listed[1].split(",")[-1].strip() != phase:
        return b""
    return (f"\n{number}. **Every case the step asks for exists:** each test case the step's text asks for "
            "exists at `HEAD` and passes, even when this phase made no commit. REJECT, naming "
            "the missing case, when one is absent.").encode()


def _write(stream, text):
    stream.buffer.write(os.fsencode(text + "\n"))


def _refuse(message=None):
    if message is not None:
        _write(sys.stderr, message)
    _write(sys.stderr, USAGE)
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


def main(argv):
    options = {"--step": "", "--fast-cmd": ""}
    while argv[:1] and argv[0] in options:
        if len(argv) < 2 or not argv[1]:
            return _refuse(f"build-verify-prompt: {argv[0]} needs a value")
        options[argv[0]] = argv[1]
        argv = argv[2:]
    if len(argv) < 3 or not all(argv[:3]):
        return _refuse()
    if len(argv) > 4:
        return _refuse("build-verify-prompt: too many arguments")
    code, out = build(options["--step"], options["--fast-cmd"], *argv)
    sys.stdout.buffer.write(out)
    return code


def _refused(message=None):
    return _refuse(message), b""


def build(step_arg, fast_cmd, phase, spec_arg, test_path, test_id=""):
    if phase not in PHASES + INTERFACE_PHASES:
        return _refused(f"build-verify-prompt: unknown phase '{phase}' (want {WANT_PHASES})")
    if "fast-cmd" in NEEDS.get(phase, ()) and not fast_cmd:
        return _refused(f"build-verify-prompt: {phase} needs --fast-cmd '<fast-tier test command>'")
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
        if not re.fullmatch(r"[0-9a-f]{7,40}", value):
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
    paths = [f"{prompts}/verify-{phase}.md", f"{prompts}/_shared.md", spec, *optional.values()]
    if phase == "plan":
        optional["LEDGER"] = test_path
        paths.append(test_path)
    for path in paths:
        if not os.access(path, os.R_OK):
            _write(sys.stderr, f"build-verify-prompt: cannot read '{path}'")
            return 2, b""
    prompts_b = os.fsencode(prompts)
    values = dict.fromkeys(("BUG_REPRODUCTION", "REFACTOR_PLAN", *GREEN_PARAGRAPHS, "LEDGER"), b"")
    try:
        template = _expand(_read(paths[0]), prompts_b)
        shared = _expand(_read(paths[1]), prompts_b)
        for placeholder, path in optional.items():
            values[placeholder] = _read(path)
            if placeholder in GREEN_PARAGRAPHS:
                values[placeholder] = _expand(b"\n\n" + values[placeholder], prompts_b)
    except _IncludeRefused as refusal:
        sys.stderr.buffer.write(refusal.args[0] + b"\n")
        return 2, b""
    step = os.fsencode(step_arg)
    step_block = b""
    if step:
        step_block = (b"### The step under judgement\n\n" + step + b"\n\n"
                      b"Your verdict is about this criterion only: the spec below is the whole issue, and its other\n"
                      b"criteria belong to other steps of the plan.\n\n")
    out = template
    written = b"**one new failing test**"
    if phase == "red" and is_replaces_case_step(step_arg):
        written = (b"**one replacement case per named case** (judge each of them, not only the target test)")
    number = 5 if phase in ("expand", "migrate") else 4
    for placeholder, value in ((b"LAST_PHASE_CHECK", _last_phase_check(step_arg, phase, number)),
                               (b"RED_WRITTEN", written), (b"SHARED", shared), (b"STEP", step_block), (b"ISSUE_SPEC", _read(spec)),
                               *((placeholder.encode(), value) for placeholder, value in values.items()),
                               (b"TEST_PATH", os.fsencode(test_path)),
                               (b"TARGET_TEST", os.fsencode(fourth or "the target test")),
                               (b"BASE_SHA", os.fsencode(slots["BASE_SHA"])),
                               (b"STEP_BASE_SHA", os.fsencode(slots["STEP_BASE_SHA"])),
                               (b"FAST_CMD", os.fsencode(fast_cmd)),
                               (b"ONTO_SHA", os.fsencode(slots["ONTO_SHA"])),
                               (b"PRE_REBASE_SHA", os.fsencode(slots["PRE_REBASE_SHA"])),
                               (b"TIMED_TEST_RUN", os.fsencode(f"{HERE}/timed-test-run.sh"))):
        out = out.replace(b"{{" + placeholder + b"}}", value)
    return 0, out + b"\n"


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
