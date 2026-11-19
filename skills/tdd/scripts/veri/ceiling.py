"""test-ceiling.sh's ramp, run in-process: the highest test-worker count `make test` runs at with no case timeout."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import subprocess
import sys
import tempfile

USAGE = "usage: test-ceiling.sh [--max <n>]\n"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))


def commit():
    return subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def run_suite(workers, record, tests=()):
    """Runs `make test` at <workers> workers, over <tests> when named (else its full selection), the recorder plugin
    appending each failing case to <record>; returns make's exit code and the failing cases, each node id mapped to
    whether it failed by its per-case timeout."""
    env = dict(os.environ, VERI_PYTEST_WORKERS=str(workers), VERI_CEILING_RECORD=record,
               PYTEST_PLUGINS=",".join(filter(None, [os.environ.get("PYTEST_PLUGINS"), "ceiling_record"])))
    argv = ["make", "--no-print-directory", "-C", ROOT, "test"] + (["TESTS=" + " ".join(tests)] if tests else [])
    code = subprocess.run(argv, env=env, stdin=subprocess.DEVNULL).returncode
    return code, failures(record)


def failures(record):
    try:
        with open(record) as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return {}
    failed = {}
    for line in filter(None, lines):
        report = json.loads(line)
        failed[report["nodeid"]] = failed.get(report["nodeid"], False) or report["timeout"]
    return failed


def bound(argv):
    """The ramp's top: `--max <n>` when given, else the logical cores; None for any other argument or an n below 2."""
    if not argv:
        return os.cpu_count() or 1
    if len(argv) == 2 and argv[0] == "--max" and argv[1].isascii() and argv[1].isdigit() and int(argv[1]) >= 2:
        return int(argv[1])
    return None


class NoAnswer(Exception):
    """A step that says nothing about load: exit 2, the message naming why."""


def step(workers, scratch):
    """Runs the full selection at <workers>; returns how many cases timed out from load, each re-run alone with one
    worker and passing there. Raises NoAnswer for a case red any other way, a hung case, or a run with nothing recorded."""
    code, failed = run_suite(workers, os.path.join(scratch, "record-%d" % workers))
    if code and not failed:
        raise NoAnswer("make test exited %d at %d workers with no failed case recorded" % (code, workers))
    red = [nodeid for nodeid, timeout in failed.items() if not timeout]
    if red:
        raise NoAnswer("failing other than by its timeout at %d workers: %s" % (workers, " ".join(red)))
    for index, nodeid in enumerate(failed):
        code, alone = run_suite(1, os.path.join(scratch, "alone-%d-%d" % (workers, index)), [nodeid])
        if code and not alone:
            raise NoAnswer("make test exited %d running %s alone with no failed case recorded" % (code, nodeid))
        if alone.get(nodeid):
            raise NoAnswer("%s timed out at %d workers and again alone with 1 worker: a hung case, not load"
                           % (nodeid, workers))
        if nodeid in alone:
            raise NoAnswer("%s timed out at %d workers and failed alone with 1 worker other than by its timeout"
                           % (nodeid, workers))
    return len(failed)


def main(argv):
    top = bound(argv)
    if top is None:
        sys.stderr.write(USAGE)
        return 2
    ceiling = None
    scratch = tempfile.mkdtemp(prefix="veri-ceiling-")
    try:
        for workers in range(2, top + 1, 2):
            if step(workers, scratch):
                break
            ceiling = workers
    except NoAnswer as error:
        sys.stderr.write("%s\n" % error)
        return 2
    if ceiling is None:
        sys.stderr.write("no ceiling of at least 2: a case timed out under load at 2 workers and passed alone\n")
        return 1
    sys.stdout.write("ceiling: %d workers\n" % ceiling)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
