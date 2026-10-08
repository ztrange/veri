"""verify.sh's logic, run in-process."""
import os
import subprocess
import sys

from leaf_role import _write
from run_verdict import SCRIPTS, takes_a_value

LEAF_ARGS = ["--permission-mode", "bypassPermissions",
             "--disallowedTools", "Write", "Edit", "MultiEdit", "NotebookEdit"]
USAGE = ("usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file>"
         " <test-path> [<target-test-id>]")


def refuse(*lines):
    for line in lines + (USAGE,):
        _write(sys.stderr, line)
    return 2


def sibling(name):
    return os.path.join(SCRIPTS, name)


def to_contract(code):
    return code if code in (0, 1, 2, 3) else 2


def main(argv):
    args = list(argv)
    while args and takes_a_value(args[0]):
        if len(args) < 2 or not args[1]:
            return refuse("verify: %s needs a value" % args[0])
        args = args[2:]
    if len(args) < 3:
        return refuse()
    try:
        built = subprocess.run(
            [sibling("build-verify-prompt.sh"), *argv],
            stdout=subprocess.PIPE)
    except OSError:
        return 2
    if built.returncode:
        return to_contract(built.returncode)
    phase = args[0]
    prompt_path = ".tdd/verify-%s.prompt" % phase
    os.makedirs(".tdd", exist_ok=True)
    with open(prompt_path, "wb") as prompt:
        prompt.write(built.stdout.rstrip(b"\n"))
    subprocess.run(
        [sibling("supervise.sh"), "verify-%s" % phase,
         sibling("run-leaf.sh"), prompt_path, *LEAF_ARGS])
    return 0
