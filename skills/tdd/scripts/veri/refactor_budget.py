"""refactor-budget.sh's comparison, run in-process."""

DEFAULT_BUDGET = 5


def main(argv):
    count = argv[0]
    budget = str(DEFAULT_BUDGET)
    if int(count) < int(budget):
        print(f"refactor {count}/{budget} — another transform may run")
        return 0
    print(f"refactor {count}/{budget} — budget spent")
    return 3
