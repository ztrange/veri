"""tick-ledger.sh's tick, run in-process."""
import sys

import ledger
import tests_frozen
from build_verify_prompt import INTERFACE_PHASES

USAGE = "usage: tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase>] <ledger-file> <matcher>"


def complain(message):
    print(f"tick-ledger.sh: {message}", file=sys.stderr)


def main(argv):
    pending, phase, owed = False, None, False
    while True:
        if argv[:1] == ["--refactor-pending"]:
            pending, argv = True, argv[1:]
        elif argv[:1] == ["--phase"] and len(argv) > 1:
            phase, argv = argv[1], argv[2:]
        elif argv[:1] == ["--phase-owed"] and len(argv) > 1:
            phase, owed, argv = argv[1], True, argv[2:]
        else:
            break
    if pending and phase:
        complain("--phase and --refactor-pending cannot be combined")
        return 2
    if owed and phase not in INTERFACE_PHASES[2:]:
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
        if ticked and ledger.listed_phases(next(
                old for old, line in zip(text.split("\n"), new.split("\n")) if old != line)):
            complain("step lists phases; mark one with --phase <phase>")
            return 2
    if not ticked:
        return 3
    left = ledger.rewrite_ledger(argv[0], new)
    if left is None:
        ticked_line = next(line for old, line in zip(text.split("\n"), new.split("\n")) if old != line)
        if "⟦diff-checked⟧" in ticked_line:
            return tests_frozen._rerecord_earlier(argv[0], ticked_line.split("] ", 1)[1])
        return 0
    if left:
        complain(f"left {left} behind")
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
