"""build-verify-prompt.sh's argument checks and rendering, run in-process."""
import os
import re
import sys

PHASES = ("red", "green", "refactor", "pin", "plan", "rebase", "transform", "diff")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USAGE = "usage: build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]"
GREEN_PARAGRAPHS = {"REPLACES_CASE": "replaces-case", "SUITE_REPAIR": "suite-repair"}


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


def _has_heading(path, heading):
    try:
        text = _read(path)
    except OSError:
        return False
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
    phase = argv[0]
    if phase not in PHASES:
        return _refuse(f"build-verify-prompt: unknown phase '{phase}' (want red|green|refactor|pin|plan|rebase|transform|diff)")
    if phase in ("green", "refactor", "diff") and not options["--fast-cmd"]:
        return _refuse(f"build-verify-prompt: {phase} needs --fast-cmd '<fast-tier test command>'")
    fourth = argv[3] if len(argv) > 3 else ""
    if phase == "diff":
        if not options["--step"]:
            return _refuse("build-verify-prompt: diff needs --step '<STEP>'")
        shas = (("<step-base-sha>", fourth), ("<base-sha>", argv[2]))
    elif phase in ("refactor", "transform"):
        shas = (("<base-sha>", fourth),)
    elif phase == "rebase":
        shas = tuple(("<onto-sha> <pre-rebase-sha>", value) for value in (argv[2], fourth))
    else:
        shas = ()
    for label, value in shas:
        if not re.fullmatch(r"[0-9a-f]{7,40}", value):
            return _refuse(f"build-verify-prompt: {phase} needs {label} as 7-40 lowercase hex characters, got '{value}'")
    prompts = f"{HERE}/prompts"
    spec = argv[1]
    optional = {}
    if _has_heading(spec, b"Bug"):
        optional["BUG_REPRODUCTION"] = f"{prompts}/_verify-red-bug.md"
    if phase == "plan" and _has_heading(spec, b"Refactor"):
        optional["REFACTOR_PLAN"] = f"{prompts}/_verify-plan-refactor.md"
    for placeholder, mark in GREEN_PARAGRAPHS.items():
        if phase == "green" and f"⟦{mark}⟧" in options["--step"]:
            optional[placeholder] = f"{prompts}/_verify-green-{mark}.md"
    paths = [f"{prompts}/verify-{phase}.md", f"{prompts}/_shared.md", spec, *optional.values()]
    if phase == "plan":
        optional["LEDGER"] = argv[2]
        paths.append(argv[2])
    for path in paths:
        if not os.access(path, os.R_OK):
            _write(sys.stderr, f"build-verify-prompt: cannot read '{path}'")
            return 2
    prompts_b = os.fsencode(prompts)
    values = dict.fromkeys(("BUG_REPRODUCTION", "REFACTOR_PLAN", "REPLACES_CASE", "SUITE_REPAIR", "LEDGER"), b"")
    try:
        template = _expand(_read(paths[0]), prompts_b)
        shared = _expand(_read(paths[1]), prompts_b)
        for placeholder, path in optional.items():
            values[placeholder] = _read(path)
            if placeholder in GREEN_PARAGRAPHS:
                values[placeholder] = _expand(b"\n\n" + values[placeholder], prompts_b)
    except _IncludeRefused as refusal:
        sys.stderr.buffer.write(refusal.args[0] + b"\n")
        return 2
    step = os.fsencode(options["--step"])
    step_block = b""
    if step:
        step_block = (b"### The step under judgement\n\n" + step + b"\n\n"
                      b"Your verdict is about this criterion only: the spec below is the whole issue, and its other\n"
                      b"criteria belong to other steps of the plan.\n\n")
    out = template
    for placeholder, value in ((b"SHARED", shared), (b"STEP", step_block), (b"ISSUE_SPEC", _read(spec)),
                               *((placeholder.encode(), value) for placeholder, value in values.items()),
                               (b"TEST_PATH", os.fsencode(argv[2])),
                               (b"TARGET_TEST", os.fsencode(fourth or "the target test")),
                               (b"BASE_SHA", os.fsencode(argv[2] if phase == "diff" else fourth)),
                               (b"STEP_BASE_SHA", os.fsencode(fourth if phase == "diff" else "")),
                               (b"FAST_CMD", os.fsencode(options["--fast-cmd"])),
                               (b"ONTO_SHA", os.fsencode(argv[2] if phase == "rebase" else "")),
                               (b"PRE_REBASE_SHA", os.fsencode(fourth if phase == "rebase" else "")),
                               (b"TIMED_TEST_RUN", os.fsencode(f"{HERE}/timed-test-run.sh"))):
        out = out.replace(b"{{" + placeholder + b"}}", value)
    sys.stdout.buffer.write(out + b"\n")
    return 0
