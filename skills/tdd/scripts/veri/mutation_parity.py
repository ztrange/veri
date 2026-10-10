"""mutation-parity.sh's pairs check, run in-process."""
import os
import re
import subprocess
import sys

from run_suite import venv_python

USAGE = "usage: mutation-parity.sh <pairs-table>"
COUNT_LINE = re.compile(r"^(\d+) passed, (\d+) failed$")


def failed_cases(suite):
    run = subprocess.run([os.path.join(".", suite)], capture_output=True, text=True,
                         stdin=subprocess.DEVNULL)
    lines = run.stdout.splitlines()
    failed = {line[len("FAIL - "):] for line in lines if line.startswith("FAIL - ")}
    count = COUNT_LINE.match(lines[-1]) if lines else None
    if not count:
        raise RuntimeError(f"{suite} never reached its count line")
    return failed, int(count.group(1))


def pytest(*args):
    run = subprocess.run([venv_python(), "-m", "pytest", "-q", *args], capture_output=True,
                         text=True, stdin=subprocess.DEVNULL)
    if run.returncode not in (0, 1):
        raise RuntimeError(f"pytest could not run {' '.join(args)}: exit {run.returncode}")
    return run


def failed_nodes(suite):
    lines = pytest("-rA", suite).stdout.splitlines()
    failed = {line.split()[1] for line in lines if line.startswith(("FAILED ", "ERROR "))}
    passed = sum(1 for line in lines if line.startswith("PASSED "))
    return failed, passed


def node_fails(node):
    return pytest(node).returncode != 0


def check(row):
    suite, old, fate, kept, patch = row
    subprocess.run(["git", "apply", patch], check=True)
    try:
        failed, passed = failed_nodes(suite) if "::" in old else failed_cases(suite)
        caught = node_fails(kept) if fate == "replaced" else kept in failed
    finally:
        subprocess.run(["git", "apply", "-R", patch], check=True)
    if any(line == old or line.startswith(old + " (") for line in failed) and passed > 0:
        return "proven" if caught else "unproven"
    return "owed"


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    with open(argv[0], encoding="utf-8") as table:
        rows = [line.rstrip("\n").split("\t") for line in table if line.strip()]
    results = []
    for row in rows:
        result = check(row)
        results.append(result)
        print("\t".join([row[1], row[3], row[4], result]))
    return 0 if all(result == "proven" for result in results) else 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
