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
    counts = [COUNT_LINE.match(line) for line in lines]
    passed = next((int(m.group(1)) for m in reversed(counts) if m), 0)
    return failed, passed


def node_fails(node):
    run = subprocess.run([venv_python(), "-m", "pytest", "-q", node], capture_output=True,
                         stdin=subprocess.DEVNULL)
    return run.returncode != 0


def check(row):
    suite, old, fate, kept, patch = row
    subprocess.run(["git", "apply", patch], check=True)
    try:
        failed, passed = failed_cases(suite)
        caught = node_fails(kept) if fate == "replaced" else kept in failed
    finally:
        subprocess.run(["git", "apply", "-R", patch], check=True)
    if old in failed and passed > 0:
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
