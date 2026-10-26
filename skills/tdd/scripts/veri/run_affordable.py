"""run-affordable.sh's projection, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import step_budget
import step_cost

USAGE = "usage: run-affordable.sh <steps-remaining> (a whole number)"


def _passed(status):
    return status if 0 <= status <= 3 else 2


def main(argv):
    remaining = argv[0] if argv else ""
    if not re.fullmatch(r"[0-9]+", remaining):
        sys.stderr.buffer.write(os.fsencode("run-affordable.sh: <steps-remaining> is not a whole number: '%s'\n%s\n"
                                            % (remaining, USAGE)))
        return 2
    status, _, run_budget = step_budget.budgets()
    if status:
        return _passed(status)
    ceiling = float(run_budget)
    status, steps = step_cost.step_costs("--steps", step_cost.logical_cwd())
    status = _passed(status)
    if status:
        return status if status == 3 else 2
    spent = 0.0
    full = []
    for line in sorted(steps.splitlines(), key=lambda line: (float(line.split()[0]), line)):
        dollars, leaves = line.split()
        spent += float(dollars)
        if int(leaves) > 2:
            full.append(float(dollars))
    if not full:
        return 3
    middle = len(full) // 2
    median = full[middle] if len(full) % 2 else (full[middle - 1] + full[middle]) / 2
    n = float(remaining)
    projection = spent + n * median
    if not projection > ceiling:
        return 0
    if sys.stdout is None:
        return 2
    count = int(n) if n < 2**63 else -2**63
    print("spent %.2f, steps remaining %d, median %.2f, projection %.2f" % (spent, count, median, projection))
    return 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
