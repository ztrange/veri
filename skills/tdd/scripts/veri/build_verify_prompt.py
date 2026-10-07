"""build-verify-prompt.sh's argument checks and rendering, run in-process."""
import os
import re
import sys

PHASES = ("red", "green", "refactor", "pin", "plan", "rebase", "transform", "diff")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USAGE = "usage: build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]"


def _write(stream, text):
    stream.buffer.write(os.fsencode(text + "\n"))


def _refuse(message=None):
    if message is not None:
        _write(sys.stderr, message)
    _write(sys.stderr, USAGE)
    return 2


def _has_heading(path, heading):
    try:
        with open(path, "rb") as f:
            text = f.read()
    except OSError:
        return False
    return re.search(rb"^## " + heading + rb"[ \t\r\v\f]*$", text, re.M) is not None


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
    paths = [f"{prompts}/verify-{phase}.md", f"{prompts}/_shared.md", spec]
    if _has_heading(spec, b"Bug"):
        paths.append(f"{prompts}/_verify-red-bug.md")
    if phase == "plan" and _has_heading(spec, b"Refactor"):
        paths.append(f"{prompts}/_verify-plan-refactor.md")
    if phase == "green" and "⟦replaces-case⟧" in options["--step"]:
        paths.append(f"{prompts}/_verify-green-replaces-case.md")
    if phase == "green" and "⟦suite-repair⟧" in options["--step"]:
        paths.append(f"{prompts}/_verify-green-suite-repair.md")
    if phase == "plan":
        paths.append(argv[2])
    for path in paths:
        if not os.access(path, os.R_OK):
            _write(sys.stderr, f"build-verify-prompt: cannot read '{path}'")
            return 2
    with open(spec, "rb") as f:
        f.read()
    return 0

