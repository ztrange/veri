"""mutation-parity.sh's pairs check, run in-process."""
import os
import re
import subprocess
import sys

from run_suite import venv_python

USAGE = "usage: mutation-parity.sh <pairs-table>"
COUNT_LINE = re.compile(r"^(\d+) passed, (\d+) failed$")


class SuiteDied(RuntimeError):
    pass


def failed_cases(suite):
    run = subprocess.run([os.path.join(".", suite)], capture_output=True, text=True,
                         stdin=subprocess.DEVNULL,
                         env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    lines = run.stdout.splitlines()
    failed = {line[len("FAIL - "):] for line in lines if line.startswith("FAIL - ")}
    count = COUNT_LINE.match(lines[-1]) if lines else None
    if not count:
        raise SuiteDied(f"{suite} never reached its count line")
    return failed, int(count.group(1)), int(count.group(1)) + int(count.group(2))


def pytest(*args):
    run = subprocess.run([venv_python(), "-m", "pytest", "-q", "-p", "no:cacheprovider", *args], capture_output=True,
                         text=True, stdin=subprocess.DEVNULL,
                         env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    if run.returncode not in (0, 1):
        raise RuntimeError(f"pytest could not run {' '.join(args)}: exit {run.returncode}")
    return run


def failed_nodes(suite):
    lines = pytest("-rA", suite).stdout.splitlines()
    failed = {line.split()[1] for line in lines if line.startswith(("FAILED ", "ERROR "))}
    passed = sum(1 for line in lines if line.startswith("PASSED "))
    return failed, passed, passed + len(failed)


def node_fails(node):
    return pytest(node).returncode != 0


def named(name, failed):
    return any(line == name or line.startswith(name + " (") for line in failed)


def suite_results(suite, old):
    return failed_nodes(suite) if "::" in old else failed_cases(suite)


def replacement_fails(fate, kept, failed):
    return node_fails(kept) if fate == "replaced" else named(kept, failed)


def unmutated_failures(suite, old, fate, kept):
    try:
        failed = suite_results(suite, old)[0]
    except SuiteDied:
        return [f"suite {suite} did not run to completion"]
    bad = []
    if named(old, failed):
        bad.append(f"old case {old}")
    if replacement_fails(fate, kept, failed):
        bad.append(f"replacement {kept}")
    return bad


def check(row):
    suite, old, fate, kept, patch = row
    bad = unmutated_failures(suite, old, fate, kept)
    if bad:
        print(f"already failing unmutated: {', '.join(bad)}", file=sys.stderr)
        return "unproven"
    subprocess.run(["git", "apply", patch], check=True)
    try:
        died = None
        try:
            failed, passed, total = suite_results(suite, old)
        except SuiteDied as error:
            died = error
        else:
            caught = replacement_fails(fate, kept, failed)
    finally:
        subprocess.run(["git", "apply", "-R", patch], check=True)
    if died:
        if failed_cases(suite)[2] != 1:
            raise died
        return "owed"
    if named(old, failed) and (passed > 0 or total == 1):
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
