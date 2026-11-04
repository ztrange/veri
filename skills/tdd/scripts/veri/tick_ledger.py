"""tick-ledger.sh's tick, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import event
import ledger
import tests_frozen
from git import git
from build_verify_prompt import INTERFACE_PHASES

RETIRED_MARK = " ⟂ retired unpinnable"
USAGE = "usage: tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase>] <ledger-file> <matcher>"


def complain(message):
    print(f"tick-ledger.sh: {message}", file=sys.stderr)


def changed_index(text, new):
    return next(i for i, (old, line) in enumerate(zip(text.split("\n"), new.split("\n"))) if old != line)


def changed_line(text, new):
    return new.split("\n")[changed_index(text, new)]


def main(argv):
    pending, phase, owed, reason_file = False, None, False, None
    while True:
        if argv[:1] == ["--unpinnable"] and len(argv) > 1:
            reason_file, argv = argv[1], argv[2:]
            continue
        if argv[:1] == ["--refactor-pending"]:
            pending, argv = True, argv[1:]
        elif argv[:1] == ["--phase"] and len(argv) > 1:
            phase, argv = argv[1], argv[2:]
        elif argv[:1] == ["--phase-owed"] and len(argv) > 1:
            phase, owed, argv = argv[1], True, argv[2:]
        else:
            break
    reason_text = ""
    if reason_file:
        with open(reason_file, encoding="utf-8") as handle:
            reason_text = handle.read()
        if "stays green" not in reason_text:
            return 1
    if pending and phase:
        complain("--phase and --refactor-pending cannot be combined")
        return 2
    if owed and phase not in ("contract-a", "contract-b"):
        complain(f"--phase-owed {phase}: only a contract phase can be owed")
        return 2
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        text = ledger.read_ledger(argv[0])
    except OSError as error:
        complain(f"{argv[0]}: {error.strerror}")
        return 2
    matcher = (argv[1:] or [""])[0]
    if phase:
        try:
            ticked, new = ledger.ledger_mark_phase(text, matcher, phase, owed)
        except ValueError as error:
            complain(str(error))
            return 2
    else:
        ticked, new = ledger.ledger_tick(text, matcher, pending)
        if ticked and reason_file:
            new_lines = new.split("\n")
            new_lines[changed_index(text, new)] += RETIRED_MARK
            new = "\n".join(new_lines)
        if ticked and ledger.listed_phases(
                text.split("\n")[changed_index(text, new)]):
            complain("step lists phases; mark one with --phase <phase>")
            return 2
    if not ticked:
        return 3
    step_line = changed_line(text, new)
    before = re.search(r"mutation-probe\.sh --before ([0-9a-f]{7,40})", step_line)
    control = re.search(r"the go-red control is (\S+) at ([0-9a-f]+)", step_line)
    if before or control:
        record = re.sub(r"\.md$", "", argv[0]) + "-mutations.md"
        named = [before.group(1)] if before else [control.group(1), control.group(2)]
        if not os.path.exists(record) or not re.search(
                "^(?:" + "|".join(map(re.escape, named)) + ")$", open(record, encoding="utf-8").read(), re.M):
            complain(f"{record}: no mutation record for the step's go-red control")
            return 2
    if tests_frozen.is_diff_checked(step_line):
        receipt = os.path.join(os.path.dirname(argv[0]), "pin-recheck-ok")
        if not os.path.exists(receipt):
            complain(f"{argv[0]}: no pin-recheck receipt: run pin-recheck.sh first")
            return 2
        with open(receipt) as handle:
            sha = handle.read().strip()
        diff = git("diff", "--name-only", sha, "HEAD", capture_output=True, text=True,
                   cwd=os.path.dirname(argv[0]) or None)
        if diff.returncode != 0:
            complain(f"{argv[0]}: the pin-recheck receipt's sha does not resolve in git: run pin-recheck.sh again")
            return 2
        if any(not path.startswith(".tdd/") for path in diff.stdout.split()):
            complain(f"{argv[0]}: a path outside .tdd/ changed since the pin-recheck receipt: run pin-recheck.sh again")
            return 2
    left = ledger.rewrite_ledger(argv[0], new)
    if left is None and reason_file:
        step = step_line
        reason = next((l[7:].strip() for l in reason_text.splitlines() if l.startswith("REASON:")), "")
        tdd_parent = os.path.dirname(os.path.dirname(os.path.abspath(argv[0])))
        return event.append(tdd_parent, event.context(os.environ), "unpinnable-step",
                            ["step=" + step.split("] ", 1)[1], "reason=" + reason])
    if left is None:
        ticked_line = step_line
        if tests_frozen.is_diff_checked(ticked_line):
            return tests_frozen.rerecord_earlier(argv[0], ticked_line.split("] ", 1)[1])
        if pending:
            return tests_frozen.rerecord_committed(
                ticked_line.split("] ", 1)[1].removesuffix(ledger.PENDING_MARK),
                os.path.dirname(os.path.dirname(os.path.abspath(argv[0]))))
        return 0
    if left:
        complain(f"left {left} behind")
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
