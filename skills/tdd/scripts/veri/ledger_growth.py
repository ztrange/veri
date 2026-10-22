"""ledger-growth.sh's check, run in-process."""
import sys

try:
    from .ledger import STEP_RE, is_added, read_ledger
except ImportError:
    from ledger import STEP_RE, is_added, read_ledger

USAGE = "usage: ledger-growth.sh <plan-ledger-file> <ledger-file>"


def step_texts(text):
    steps = []
    for line in text.split("\n"):
        match = STEP_RE.fullmatch(line)
        if match:
            steps.append((match.group(4) or "").split(" ⟂ ", 1)[0])
    return steps


def main(argv):
    if len(argv) != 2 or not argv[0] or not argv[1]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        planned = set(step_texts(read_ledger(argv[0])))
        steps = step_texts(read_ledger(argv[1]))
    except OSError as error:
        print(f"ledger-growth.sh: {error.filename}: {error.strerror}", file=sys.stderr)
        return 2
    off = [step for step in steps if step not in planned and not is_added(step)]
    for step in off:
        print(f"ledger-growth.sh: step added without ⟦added⟧: {step}", file=sys.stderr)
    return 1 if off else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
