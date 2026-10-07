"""build-verify-prompt.sh's argument checks and rendering, run in-process."""
import os
import sys

PHASES = ("red", "green", "refactor", "pin", "plan", "rebase", "transform", "diff")
USAGE = "usage: build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]"


def _write(stream, text):
    stream.buffer.write(os.fsencode(text + "\n"))


def _refuse(message=None):
    if message is not None:
        _write(sys.stderr, message)
    _write(sys.stderr, USAGE)
    return 2


def main(argv):
    options = {"--step": "", "--fast-cmd": ""}
    while argv[:1] and argv[0] in options:
        if len(argv) < 2:
            return _refuse(f"build-verify-prompt: {argv[0]} needs a value")
        options[argv[0]] = argv[1]
        argv = argv[2:]
    if len(argv) < 3 or not all(argv[:3]):
        return _refuse()
    phase = argv[0]
    if phase not in PHASES:
        return _refuse(f"build-verify-prompt: unknown phase '{phase}' (want red|green|refactor|pin|plan|rebase|transform|diff)")
    if phase in ("green", "diff") and not options["--fast-cmd"]:
        return _refuse(f"build-verify-prompt: {phase} needs --fast-cmd '<fast-tier test command>'")
    return 0

