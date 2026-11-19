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
    appending each failing case to <record>; returns make's exit code and the failing cases' node ids."""
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
        return []
    return list(dict.fromkeys(json.loads(line)["nodeid"] for line in lines if line))


def bound(argv):
    """The ramp's top: `--max <n>` when given, else the logical cores; None for any other argument or an n below 2."""
    if not argv:
        return os.cpu_count() or 1
    if len(argv) == 2 and argv[0] == "--max" and argv[1].isascii() and argv[1].isdigit() and int(argv[1]) >= 2:
        return int(argv[1])
    return None


def main(argv):
    top = bound(argv)
    if top is None:
        sys.stderr.write(USAGE)
        return 2
    ceiling = None
    scratch = tempfile.mkdtemp(prefix="veri-ceiling-")
    for workers in range(2, top + 1, 2):
        _, timed_out = run_suite(workers, os.path.join(scratch, "record-%d" % workers))
        for nodeid in timed_out:
            _, alone = run_suite(1, os.path.join(scratch, "alone-%d" % workers), [nodeid])
            if nodeid in alone:
                sys.stderr.write("%s timed out at %d workers and again alone with 1 worker: a hung case, not load\n"
                                 % (nodeid, workers))
                return 2
        if timed_out:
            break
        ceiling = workers
    sys.stdout.write("ceiling: %d workers\n" % ceiling)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
