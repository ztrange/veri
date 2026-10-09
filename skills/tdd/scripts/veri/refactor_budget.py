"""refactor-budget.sh's comparison, run in-process."""
import os
import re
import sys

DEFAULT_BUDGET = 5
DEFAULT_ISSUE_BUDGET = 3
USAGE = "usage: refactor-budget.sh [--issue] <count>"


def _write(stream, text):
    stream.buffer.write(os.fsencode(text + "\n"))
    stream.buffer.flush()


def _refused(name, value):
    if re.fullmatch(r"[0-9]+", value):
        return False
    _write(sys.stderr, f"refactor-budget: {name} must be a whole number >= 0: {value}")
    return True


def _arithmetic(value):
    number = int(value) % 2**64
    return number - 2**64 if number >= 2**63 else number


def main(argv):
    budget_var, default = "VERI_REFACTOR_BUDGET", DEFAULT_BUDGET
    if argv[:1] == ["--issue"]:
        argv = argv[1:]
        budget_var, default = "VERI_ISSUE_REFACTOR_BUDGET", DEFAULT_ISSUE_BUDGET
    budget = os.environ.get(budget_var) or str(default)
    count = argv[0] if argv else ""
    if _refused(budget_var, budget):
        return 2
    if _refused("<count>", count):
        _write(sys.stderr, USAGE)
        return 2
    spent = int(count) >= _arithmetic(budget)
    _write(sys.stdout, f"refactor {count}/{budget} — {'budget spent' if spent else 'another transform may run'}")
    return 3 if spent else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
