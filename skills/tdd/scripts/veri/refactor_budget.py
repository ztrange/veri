"""refactor-budget.sh's comparison, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import tunables
from entry import whole_number, write

USAGE = "usage: refactor-budget.sh [--issue] <count>"


def _refused(name, value):
    if whole_number(value, 0) is not None:
        return False
    write(sys.stderr, f"refactor-budget: {name} must be a whole number >= 0: {value}", before=False)
    return True


def _arithmetic(value):
    number = int(value) % 2**64
    return number - 2**64 if number >= 2**63 else number


def main(argv):
    budget_var = "VERI_REFACTOR_BUDGET"
    if argv[:1] == ["--issue"]:
        argv = argv[1:]
        budget_var = "VERI_ISSUE_REFACTOR_BUDGET"
    budget = tunables.get(budget_var, unless_empty=True)
    count = argv[0] if argv else ""
    if _refused(budget_var, budget):
        return 2
    if _refused("<count>", count):
        write(sys.stderr, USAGE, before=False)
        return 2
    spent = int(count) >= _arithmetic(budget)
    write(sys.stdout, f"refactor {count}/{budget} — {'budget spent' if spent else 'another transform may run'}",
          before=False)
    return 3 if spent else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
