"""verify.sh's logic, run in-process."""
import glob
import io
import os
import subprocess
import sys

import parse_verdict

from leaf_model import is_echo_flag, resolve
from leaf_role import _write, leaf_role
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


def leaf_args():
    words = os.environ.get("VERIFY_LEAF_ARGS")
    if not words:
        return LEAF_ARGS
    return [path for word in words.split()
            for path in (sorted(glob.glob(word)) or [word])]


def main(argv):
    args = list(argv)
    while args and takes_a_value(args[0]):
        if len(args) < 2 or not args[1]:
            return refuse("verify: %s needs a value" % args[0])
        args = args[2:]
    if len(args) < 3:
        return refuse()
    leaf = "verify-" + args[0]
    if os.environ.get("VERIFY_LEAF_ARGS"):
        model = resolve(leaf) or ""
        if model and not is_echo_flag(model) and "--model" in leaf_args():
            _write(sys.stderr, "verify: VERIFY_LEAF_ARGS carries its own --model and a role model"
                   " variable resolved '%s' — which one the leaf would run on is flag order;"
                   " unset one of them" % model)
            return 2
    try:
        built = subprocess.run(
            [sibling("build-verify-prompt.sh"), *argv],
            stdout=subprocess.PIPE)
    except OSError:
        return 2
    if built.returncode:
        return to_contract(built.returncode)
    prompt_path = ".tdd/%s.prompt" % leaf
    os.makedirs(".tdd", exist_ok=True)
    with open(prompt_path, "wb") as prompt:
        prompt.write(built.stdout.rstrip(b"\n"))
    launched = subprocess.run(
        [sibling("supervise.sh"), leaf,
         sibling("run-leaf.sh"), prompt_path, *leaf_args()],
        stdout=subprocess.PIPE)
    code, reason = parse(launched.stdout)
    word = {0: "PASS", 1: "REJECT"}.get(code, "malformed")
    subprocess.run(
        [sibling("event.sh"), "verdict", "verdict=" + word,
         "reason=" + reason.split("\n", 1)[0]],
        env={**os.environ, **leaf_role(leaf)})
    _write(sys.stdout, reason)
    return to_contract(code)


def parse(out):
    stdin, stdout = sys.stdin, sys.stdout
    sys.stdin = io.StringIO(out.decode("utf-8", "surrogateescape"))
    sys.stdout = io.StringIO()
    try:
        code = parse_verdict.main([])
        return code, sys.stdout.getvalue().rstrip("\n")
    finally:
        sys.stdin, sys.stdout = stdin, stdout
