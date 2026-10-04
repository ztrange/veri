"""refactor-budget.sh's comparison, run in-process."""
import os
import re
import sys

DEFAULT_BUDGET = 5
DEFAULT_ISSUE_BUDGET = 3
USAGE = "usage: refactor-budget.sh [--issue] <count>"


def main(argv):
    budget_var, default = "VERI_REFACTOR_BUDGET", DEFAULT_BUDGET
    if argv[:1] == ["--issue"]:
        argv = argv[1:]
        budget_var, default = "VERI_ISSUE_REFACTOR_BUDGET", DEFAULT_ISSUE_BUDGET
    budget = os.environ.get(budget_var) or str(default)
    count = argv[0] if argv else ""
    if not re.fullmatch(r"[0-9]+", budget):
        print(f"refactor-budget: {budget_var} must be a whole number >= 0: {budget}", file=sys.stderr)
        return 2
    if not re.fullmatch(r"[0-9]+", count):
        print(f"refactor-budget: <count> must be a whole number >= 0: {count}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    spent = int(count) >= int(budget)
    print(f"refactor {count}/{budget} — {'budget spent' if spent else 'another transform may run'}")
    return 3 if spent else 0
