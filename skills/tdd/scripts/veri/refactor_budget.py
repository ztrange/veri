"""refactor-budget.sh's comparison, run in-process."""
import re
import sys

DEFAULT_BUDGET = 5
DEFAULT_ISSUE_BUDGET = 3
USAGE = "usage: refactor-budget.sh [--issue] <count>"


def main(argv):
    budget = str(DEFAULT_BUDGET)
    if argv[:1] == ["--issue"]:
        argv = argv[1:]
        budget = str(DEFAULT_ISSUE_BUDGET)
    count = argv[0]
    if not re.fullmatch(r"[0-9]+", count):
        print(f"refactor-budget: <count> must be a whole number >= 0: {count}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    spent = int(count) >= int(budget)
    print(f"refactor {count}/{budget} — {'budget spent' if spent else 'another transform may run'}")
    return 3 if spent else 0
