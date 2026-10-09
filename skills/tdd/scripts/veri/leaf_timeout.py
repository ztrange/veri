"""leaf-timeout.sh's derivation, run in-process."""
import os
import pathlib
import re
import sys

USAGE = "usage: leaf-timeout.sh <baseline-seconds> [refactor | --full <full-seconds>]"


def is_whole(text):
    return re.fullmatch(r"[0-9]+", text) is not None


def refuse(message):
    print(message, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


def require_seconds(name, value):
    if not is_whole(value):
        return refuse(f"leaf-timeout: {name} must be a whole number >= 0: {value}")
    return 0


def record(timeout):
    issue = os.environ.get("VERI_ISSUE", "")
    if not issue:
        return
    here = pathlib.Path.cwd()
    root = next((d for d in (here, *here.parents) if (d / ".git").exists()), here)
    state = os.path.join(root, ".tdd")
    os.makedirs(state, exist_ok=True)
    try:
        with open(os.path.join(state, f"issue-{issue}-timeout"), "x") as settled:
            settled.write(f"{timeout}\n")
    except FileExistsError:
        pass


def inside_own_scripts():
    scripts = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    here = os.path.realpath(os.getcwd())
    return here == scripts or here.startswith(scripts + os.sep)


def main(argv):
    override = os.environ.get("VERI_TIMEOUT", "")
    if override:
        if not is_whole(override) or int(override) < 1:
            print(f"leaf-timeout: VERI_TIMEOUT must be a whole number >= 1: {override}", file=sys.stderr)
            return 2
        print(int(override))
        return 0
    baseline = argv[0] if argv else ""
    code = require_seconds("<baseline-seconds>", baseline)
    if code:
        return code
    if argv[1:2] == ["--full"]:
        full = argv[2] if len(argv) > 2 else ""
        code = require_seconds("<full-seconds>", full)
        if code:
            return code
        baseline = full
    derived = max(900, int(baseline) * 6)
    if argv[1:2] == ["refactor"]:
        budget = os.environ.get("VERI_REFACTOR_BUDGET") or "5"
        if not is_whole(budget):
            print(f"leaf-timeout: VERI_REFACTOR_BUDGET must be a whole number >= 0: {budget}", file=sys.stderr)
            return 2
        derived = derived * max(1, int(budget))
    if os.environ.get("VERI_ISSUE") and inside_own_scripts():
        print("leaf-timeout.sh: type this from the run's worktree,"
              " not from the skill's own scripts directory", file=sys.stderr)
        return 2
    record(derived)
    print(derived)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
