"""test-ceiling.sh's ramp, run in-process: the highest test-worker count `make test` runs at with no case timeout."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import fcntl
import json
import os
import subprocess
import sys
import tempfile
import time

import git
import leg_registry
import tunables
from full_run_lock import legs_dir

LEG = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "tests", "leg")

USAGE = "usage: test-ceiling.sh [--max <n>]\n"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))


def commit():
    """The commit measured at; git.GitFailed (exit 2 before any suite runs) when it cannot be read."""
    return git.out("rev-parse", "HEAD", cwd=ROOT)


def run_suite(workers, record, tests=()):
    """Runs `make test` at <workers> workers, over <tests> when named (else its full selection), the recorder plugin
    appending each failing case to <record>; returns make's exit code and the failing cases, each node id mapped to
    whether it failed by its per-case timeout."""
    # PYTEST_PLUGINS names the recorder alone (the leg appends its own plugins): a caller's extra plugins would run in
    # every step and skew what the ramp measures.
    env = tunables.with_values(VERI_PYTEST_WORKERS=str(workers), VERI_CEILING_RECORD=record,
                               PYTEST_PLUGINS="ceiling_record")
    argv = ["make", "--no-print-directory", "-C", ROOT, "test"] + (["TESTS=" + " ".join(tests)] if tests else [])
    code = subprocess.run(argv, env=env, stdin=subprocess.DEVNULL).returncode
    return code, failures(record)


def run_unit(workers):
    """Runs `make unit` at <workers> workers; returns make's exit code."""
    env = tunables.with_values(VERI_PYTEST_WORKERS=str(workers))
    return subprocess.run(["make", "--no-print-directory", "-C", ROOT, "unit"], env=env, stdin=subprocess.DEVNULL).returncode


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


sleep = time.sleep
clock = time.monotonic


def record_path():
    return tunables.get("VERI_TEST_CEILING_FILE") or os.path.join(os.path.expanduser("~"), ".veri-test-ceiling")


def read_idle(tier):
    """The seconds of the record's `idle <tier> <seconds>` line, the tier's idle duration (PRD 036.10); None when the
    record has no such line, there is no record, or it cannot be read: the warning it feeds changes nothing (RW6)."""
    try:
        with open(record_path()) as f:
            lines = f.read().splitlines()
    except (OSError, ValueError):
        return None
    for line in lines:
        words = line.split()
        if len(words) == 3 and words[:2] == ["idle", tier] and words[2].isascii() and words[2].isdigit():
            return int(words[2])
    return None


def cap_path():
    return tunables.get("VERI_TEST_CAP_FILE") or os.path.join(os.path.expanduser("~"), ".veri-test-cap")


def read_cap():
    """(cap, complaint): the cap the human set on line 1 of the cap file (cap_path) when it is a whole number of at
    least 2. No file is no cap and no complaint; one that cannot be read, or whose line 1 is anything else, is no cap and
    a one-line complaint naming the file, for the caller's stderr. Nothing in veri writes or removes the file (D30)."""
    path = cap_path()
    try:
        with open(path) as f:
            first = f.readline().strip()
    except FileNotFoundError:
        return None, None
    except (OSError, ValueError) as error:
        return None, "cannot read the test-worker cap file %s, so there is no cap: %s\n" % (path, error)
    if first.isascii() and first.isdigit() and int(first) >= 2:
        return int(first), None
    return None, "the test-worker cap file %s holds %r on line 1, not a whole number of at least 2, so there is no cap\n" % (
        path, first)


def write_record(lines):
    """Replaces the record whole through a temporary file beside it, so a reader never sees it half-written."""
    path = record_path()
    fd, temporary = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)), prefix=os.path.basename(path) + ".")
    try:
        with os.fdopen(fd, "w") as f:
            f.write("".join(line + "\n" for line in lines))
        os.replace(temporary, path)
    except BaseException:
        os.unlink(temporary)
        raise
    return path


def register(workers):
    """Registers <workers> under this process's pid in the legs registry, as a leg would, once no other live leg is
    registered, waiting meanwhile with one stderr line naming them; returns the entry's path."""
    legs = legs_dir()
    os.makedirs(legs, exist_ok=True)
    said = False
    while True:
        with open(legs.rstrip("/") + ".lock", "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            others = leg_registry.registered_legs(legs)
            if not others:
                entry = os.path.join(legs, str(os.getpid()))
                with open(entry, "w") as f:
                    f.write(leg_registry.registration(workers))
                return entry
            if not said:
                sys.stderr.write("waiting to measure %d workers until no other leg is registered: %s\n" % (
                    workers, ", ".join("pid %s with %d workers" % holder for holder in others)))
                sys.stderr.flush()
                said = True
        sleep(1)


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


def ramp(top, scratch, odd_top=False):
    """Steps w = 2, 4, … up to <top>, <top> itself last when it is odd and <odd_top> is set (a cap is), stopping at the
    first with a load timeout; returns the ceiling (None when that was the first step), one
    `<workers> <seconds> <timeouts>` line per step run, and the ceiling step's seconds, the full suite's idle duration."""
    ceiling, steps, idle = None, [], None
    for workers in list(range(2, top + 1, 2)) + ([top] if odd_top and top % 2 else []):
        entry = register(workers)
        began = clock()
        try:
            timeouts = step(workers, scratch)
        finally:
            leg_registry.unregister(entry)
        seconds = round(clock() - began)
        steps.append("%d %d %d" % (workers, seconds, timeouts))
        if timeouts:
            break
        ceiling, idle = workers, seconds
    return ceiling, steps, idle


def idle_fast(ceiling):
    """The fast tier's idle duration: one `make unit` at the workers it would take on an idle machine, min(4, the
    ceiling), registered as a step is; returns its seconds. Raises NoAnswer when it is red: a red fast tier measures
    nothing about idle time."""
    workers = min(4, ceiling)
    entry = register(workers)
    began = clock()
    try:
        code = run_unit(workers)
    finally:
        leg_registry.unregister(entry)
    if code:
        raise NoAnswer("make unit exited %d at %d workers after the ramp: a red fast tier measures no idle time"
                       % (code, workers))
    return round(clock() - began)


def forget_lowering():
    """Removes VERI_TEST_LOAD_FILE, the T a load timeout lowered (PRD 036.7 LO6): a fresh measurement is the only thing
    in veri that raises it back. One it cannot remove is one stderr line naming it."""
    import load_timeouts
    try:
        os.remove(load_timeouts.load_path())
    except FileNotFoundError:
        pass
    except OSError as error:
        sys.stderr.write("cannot remove the load file %s (%s), so T stays lowered until it is removed\n" % (
            load_timeouts.load_path(), error.strerror or error))


def main(argv):
    if LEG not in sys.path:
        sys.path.append(LEG)
    top = bound(argv)
    if top is None:
        sys.stderr.write(USAGE)
        return 2
    cap, complaint = read_cap()
    if complaint:
        sys.stderr.write(complaint)
    # With a cap (PRD 036.11 CAP5), the ramp's top is the least of the cores, --max and the cap, the first named winning
    # a tie, and exit 0 names it, so a ramp its bound stopped does not read as a measured limit.
    bounds = [(cap, "the cap file " + cap_path())] if cap else []
    bounds.append((top, "--max %d" % top if argv else "the logical cores"))
    top, stopper = min(bounds, key=lambda pair: pair[0])
    header = [time.strftime("%Y-%m-%d %H:%M:%S %z"), commit(), "%.2f %.2f %.2f" % os.getloadavg()]
    try:
        with tempfile.TemporaryDirectory(prefix="veri-ceiling-") as scratch:
            ceiling, steps, idle_all = ramp(top, scratch, odd_top=bool(cap))
        if ceiling is None:
            sys.stderr.write("no ceiling of at least 2: a case timed out under load at 2 workers and passed alone\n")
            return 1
        idle = ["idle all %d" % idle_all, "idle fast %d" % idle_fast(ceiling)]
    except NoAnswer as error:
        sys.stderr.write("%s\n" % error)
        return 2
    path = write_record([str(ceiling)] + header + steps + idle)
    forget_lowering()
    stopped = "; the ramp stopped at its bound, %s" % stopper if cap and ceiling == top else ""
    sys.stdout.write("ceiling: %d workers (recorded in %s)%s\n" % (ceiling, path, stopped))
    return 0

if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
