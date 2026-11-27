"""The pytest leg's launcher: refuses an interpreter below the Python floor, then runs pytest."""
import contextlib
import fcntl
import hashlib
import importlib.util
import io
import json
import marshal
import os
import os.path as _path
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

VERI = _path.join(_path.dirname(_path.dirname(_path.dirname(_path.realpath(__file__)))), "veri")
if __name__ == "__main__":
    # Run directly, the leg's directory leads sys.path; it holds only the leg and its plugins, so veri/ takes its place
    # before pycache_prefix.py runs (it compiles sys.path[0]'s modules) and before any veri import (PRD 025.16).
    __import__("sys").path[0] = VERI
    __import__("runpy").run_path(VERI + "/pycache_prefix.py")
# Usage:   pytest_leg.py [--subset] [--cap=<n>] [pytest-args...]
#          With VERI_PYTEST_WORKERS unset, the leg's workers come out of T, the budget every registered leg on the machine
#            shares: line 1 of ~/.veri-test-ceiling (VERI_TEST_CEILING_FILE, `make ceiling`'s record) when it is a whole
#            number of at least 2, else the physical cores (the affinity count off macOS), never below 2, said in one
#            stderr line naming the file and `make ceiling`; lowered to the cap on line 1 of ~/.veri-test-cap
#            (VERI_TEST_CAP_FILE, PRD 036.11) when that is a whole number of at least 2 below it (any other content, or
#            an unreadable file, is one stderr line and no cap; the wait line then names the cap file); narrowed, while any
#            lane entry under ~/.veri-test-budget (VERI_TEST_BUDGET_DIR) is unexpired, to the sum of their needs, never
#            below 2 (PRD 036.5; the wait line then names each lane and its need beside C). It starts only once 2 of T are free, waiting meanwhile
#            (PRD 036.4), takes every free worker, and registers what it takes
#          --subset: the caller named the suites to run (`make test TESTS=…`), so no full-run lock is taken, and the leg
#            takes at most 4 of the free workers
#          --cap=<n>: take at most <n> of the free workers (`make unit` passes 4); it wins over --subset's 4
#          Cases run in two pytest passes, non-`serial` then `serial`; when both run, the output ends with one line
#          `<named> named, <run> run, <passed> passed, <failed> failed across both passes`.
# Exit:    0 pytest passed, 1 any other pytest status, or a --subset run handed -m left a named target (file, directory
#            or node id) with cases its -k keeps of which neither pass ran one: it prints
#            `<n> unselected: named cases that neither pass ran (<targets>)`; cases the run's own -m/-k deselects from a
#            target that ran never count
#          2 the interpreter is below the floor in lib/venv-python.sh, or cannot import pytest, pytest_timeout or xdist,
#            or VERI_PYTEST_WORKERS, VERI_PYTEST_IDLE or --cap is not a whole number of at least 1, or any other exception escaped the leg (registering
#            it, taking the full-run lock, checking or recording the bytecode cache), one stderr line naming it in
#            entry.refusal's form (#3985); a record that fails after failing suites leaves their 1
#            or no case started or reported for VERI_PYTEST_IDLE seconds (default 1200): the leg ends the workers it
#            started (TERM, KILL by pid after 5 s), removes its registry entry, releases the full-run lock and prints
#            `pytest leg idle for <s> s with no case running (last case seen: <node id>|none); workers <pid>… ended`
#            (idle_watch.py, #4254), whatever its cases' outcomes
#          128 + the signal's number on TERM or HUP: the leg ends its workers, entry and lock the same way, without
#            waiting on xdist's worker teardown, and prints `pytest leg ended by signal <n>; workers <pid>… ended`
import budget_entries
import entry
import event
import full_run_lock
import launch_floor
import leg_tmpdir
import pid_file
import tunables
from ceiling import cap_path, read_cap, record_path
from full_run_lock import legs_dir, waiters_dir
from leg_registry import registered_legs, registered_workers, registration, unregister

MANIFEST = "veri-manifest.json"
# Whether the last main()'s passes ran and were red, set before its teardown, so launch keeps their 1 when the
# teardown raises (#3985).
PASSES_RED = [False]


def pyc_files(prefix):
    for directory, _, names in os.walk(prefix):
        for name in names:
            if name.endswith(".pyc"):
                yield os.path.join(directory, name)


REWRITTEN_TAIL = re.compile(r"-pytest-[^/]*\.pyc$")


def never_recorded(pyc):
    return ".opt-" in os.path.basename(pyc)


def source_path(pyc):
    return importlib.util.source_from_cache(REWRITTEN_TAIL.sub(".pyc", pyc))


def stat_or_none(path):
    try:
        return os.stat(path)
    except FileNotFoundError:
        return None


def source_text(pyc):
    with open(source_path(pyc), "rb") as source:
        return source.read()


def source_digest(pyc):
    try:
        return hashlib.sha256(source_text(pyc)).hexdigest()
    except (OSError, ValueError, NotImplementedError):
        return None


def stamped_with_source_stat(pyc):
    try:
        with open(pyc, "rb") as f:
            header = f.read(16)
        stat = os.stat(source_path(pyc))
    except (OSError, ValueError, NotImplementedError):
        return False
    stamp = (int(stat.st_mtime) & 0xFFFFFFFF).to_bytes(4, "little") + (stat.st_size & 0xFFFFFFFF).to_bytes(4, "little")
    return header[:4] == importlib.util.MAGIC_NUMBER and header[8:16] == stamp


def compiled_from_current_source(pyc):
    if REWRITTEN_TAIL.search(pyc):
        return stamped_with_source_stat(pyc)
    try:
        with open(pyc, "rb") as f:
            cached = marshal.loads(f.read()[16:])
        source = importlib.util.source_from_cache(pyc)
        return cached == compile(source_text(pyc), source, "exec", dont_inherit=True)
    except (OSError, ValueError, NotImplementedError, SyntaxError, EOFError, TypeError):
        return False


def read_manifest(prefix):
    try:
        with open(os.path.join(prefix, MANIFEST)) as f:
            manifest = json.load(f)
    except (OSError, ValueError):
        return {}
    return manifest if isinstance(manifest, dict) else {}


def check_bytecode_cache(prefix):
    start = time.time_ns()
    snapshot = {}
    manifest = read_manifest(prefix)
    for pyc in pyc_files(prefix):
        if never_recorded(pyc) or pyc not in manifest or source_digest(pyc) != manifest[pyc]:
            try:
                os.remove(pyc)
            except FileNotFoundError:
                pass
            continue
        stat = stat_or_none(pyc)
        if stat is None:
            continue
        snapshot[pyc] = (stat.st_mtime_ns, stat.st_size)
    return {"start": start, "snapshot": snapshot}


def record_bytecode_cache(prefix, run):
    recorded = {}
    for pyc in pyc_files(prefix):
        if never_recorded(pyc):
            continue
        stat = stat_or_none(pyc)
        if stat is None:
            continue
        if run["snapshot"].get(pyc) == (stat.st_mtime_ns, stat.st_size) or stat.st_mtime_ns < run["start"]:
            continue
        try:
            if os.stat(source_path(pyc)).st_mtime_ns > run["start"]:
                continue
        except (OSError, ValueError, NotImplementedError):
            continue
        digest = source_digest(pyc)
        if digest and compiled_from_current_source(pyc):
            recorded[pyc] = digest
    with open(os.path.join(prefix, MANIFEST + ".lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        manifest = read_manifest(prefix)
        manifest.update(recorded)
        manifest = {pyc: digest for pyc, digest in manifest.items() if os.path.exists(pyc)}
        temporary = os.path.join(prefix, MANIFEST + ".%d" % os.getpid())
        with open(temporary, "w") as f:
            json.dump(manifest, f)
        os.replace(temporary, os.path.join(prefix, MANIFEST))


def worker_count(requested):
    if requested:
        return int(requested)
    if os.environ.get("PYTEST_XDIST_WORKER"):
        return 1
    return budget()[0] - registered_workers(legs_dir())


def budget(say=True):
    """(T, its source, for the wait line): T, the workers every live leg on the machine shares, is C0 (c0()), lowered
    to the cap the human set (ceiling.read_cap) when that is below it, the source then naming the cap file beside C0 and
    C0's source (PRD 036.11), and lowered again to a load timeout's T in the load file (load_timeouts.held) when that
    is below what remains, never below 2 (PRD 036.7); that C narrowed to max(2, min(C, S)), S the needs summed over the
    unexpired lane entries (budget_entries.unexpired, PRD 036.5), while there is one, the source then naming each entry's lane and need
    beside C and its source when that narrows it. C0 from the core fallback is one stderr line naming the record and `make ceiling`; a cap
    file it cannot use is one more; with <say> false, neither is written (a wait re-reading T has said them once)."""
    total, source = capacity(say)
    needs = budget_entries.unexpired()
    narrowed = max(2, min(total, sum(need for _, need in needs)))
    if needs and narrowed < total:
        return narrowed, "the lane entries %s, below C=%d from %s" % (
            ", ".join("%s=%d" % entry for entry in needs), total, source)
    return total, source


def capacity(say=True):
    """(C, its source): C0 lowered to the cap and the load file's T, as budget() describes, before any lane entry narrows it."""
    total, source = c0()
    if source is None and say:
        sys.stderr.write("no test-worker ceiling in %s, so the budget is the %d cores; `make ceiling` measures one\n" % (
            record_path(), total))
    if source is None:
        source = "the core fallback"
    cap, complaint = read_cap()
    if complaint and say:
        sys.stderr.write(complaint)
    sys.stderr.flush()
    if cap and cap < total:
        total, source = cap, "the cap file %s, below C0=%d from %s" % (cap_path(), total, source)
    import load_timeouts
    held = load_timeouts.held()
    if held and held < total:
        total, source = max(2, held), "the load file %s, below %d from %s" % (load_timeouts.load_path(), total, source)
    return total, source


def c0():
    """(C0, its source): line 1 of the ceiling record (ceiling.record_path) when it is a whole number of at least 2, its
    source naming the record; else the cores, never below 2, its source None. A record that is missing, unreadable or
    malformed only falls back, never raises."""
    path = record_path()
    try:
        with open(path) as f:
            first = f.readline().strip()
    except (OSError, ValueError):
        first = ""
    if first.isascii() and first.isdigit() and int(first) >= 2:
        return int(first), "the ceiling record " + path
    return max(2, cores()), None


def cores():
    """The physical cores on macOS (the affinity count when sysctl cannot say), the CPU-affinity count elsewhere."""
    affinity = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count() or 1
    if sys.platform == "darwin":
        try:
            cores = int(subprocess.run(["sysctl", "-n", "hw.physicalcpu"], capture_output=True, text=True).stdout)
        except (OSError, ValueError):
            cores = affinity
    else:
        cores = affinity
    return cores


def unmark(waitfile):
    """Removes the core wait's marker; one already gone (a leg sharing it finished first) or unremovable is left be."""
    try:
        os.remove(waitfile)
    except OSError:
        pass


# No test run gets fewer workers than this (PRD 036 D18): a leg starts only when this many of T are free.
FLOOR = 2
# A `make test TESTS=…` subset takes at most this many of the free workers, as `make unit` does through --cap=4, so the
# first leg no longer takes every free worker; only the one full run does (D18).
SUBSET_CAP = 4


def claim(cleanups=None, cap=None):
    """Registers this leg once a core is free, waiting for one meanwhile: returns (workers, its entry's path, T), the
    workers the free cores, at most <cap> when given, and T the budget they came out of.

    While it waits, the PYTEST_LEG_LOCK_WAIT_MARKER file names it, and `cleanups` (the idle watch's) holds the marker's
    removal, so a leg ended by TERM or HUP mid-wait leaves no marker; one it cannot write is one stderr line, and the
    wait goes on unmarked."""
    legs = legs_dir()
    os.makedirs(legs, exist_ok=True)
    said = False
    waitfile = ""
    waiter = ""
    cleanups = [] if cleanups is None else cleanups
    def removal():
        return unmark(waitfile)
    def withdrawal():
        return unregister(waiter)
    nested = os.environ.get("PYTEST_XDIST_WORKER")
    passes = 0
    try:
        while True:
            total, source = budget(say=not passes)
            passes += 1
            with open(legs.rstrip("/") + ".lock", "w") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                count = 1 if nested else total - registered_workers(legs)
                if count >= (1 if nested else FLOOR):
                    count = min(count, cap) if cap else count
                    entry = os.path.join(legs, str(os.getpid()))
                    with open(entry, "w") as f:
                        f.write(registration(count))
                    if said:
                        event.mark("", event.context(tunables.environment()), "core-wait",
                                   ["seconds=%d" % round(time.monotonic() - began)])  # noqa: F821 -- set on an earlier pass of the loop
                    return count, entry, total
                if not said:
                    holders = registered_legs(legs)
                    sys.stderr.write("waiting for %d free test workers of T=%d (%s): %d in use by the registered legs with pids %s\n" % (
                        FLOOR, total, source, sum(count for _, count in holders),
                        ", ".join(name for name, _ in holders)))
                    sys.stderr.flush()
                    said = True
                    began = time.monotonic()  # noqa: F841 -- read on a later pass of the loop, which pyflakes misreads
                    waiters = waiters_dir()
                    waiter = os.path.join(waiters, str(os.getpid()))
                    try:
                        os.makedirs(waiters, exist_ok=True)
                        with open(waiter, "w") as f:
                            f.write(registration(FLOOR))
                        cleanups.append(withdrawal)
                    except OSError as error:
                        sys.stderr.write("cannot register the wait, so dispatch.sh does not count it: %s\n" % error)
                        sys.stderr.flush()
                    waitfile = os.environ.get("PYTEST_LEG_LOCK_WAIT_MARKER", "")
                    if waitfile:
                        try:
                            pid_file.record(waitfile, os.getpid(), atomic=True)
                            cleanups.append(removal)
                        except OSError as error:
                            sys.stderr.write("cannot mark the core wait, so it counts toward the leaf's timeout: %s\n" % error)
                            sys.stderr.flush()
                            waitfile = ""
            time.sleep(1)
    finally:
        if removal in cleanups:
            cleanups.remove(removal)
        if withdrawal in cleanups:
            cleanups.remove(withdrawal)
        if waitfile:
            unmark(waitfile)
        if waiter:
            unregister(waiter)


def sweep_dead_runs():
    root = tempfile.gettempdir()
    try:
        names = os.listdir(root)
    except OSError:
        return
    for name in names:
        if not name.startswith("veri-pytest-"):
            continue
        folder = os.path.join(root, name)
        try:
            with open(os.path.join(folder, "pid")) as record:
                pid = int(record.read())
            os.kill(pid, 0)
        except ProcessLookupError:
            remove_scratch_mirror(sys.pycache_prefix, folder)
            shutil.rmtree(folder, ignore_errors=True)
        except (ValueError, OSError):
            continue


def remove_scratch_mirror(prefix, folder):
    """Removes the trees under the bytecode prefix that mirror `folder`, a scratch directory this leg made or proved dead.

    CPython writes a source's .pyc under <prefix>/<the source's absolute directory>, so a source a case creates under the
    run's directory leaves a tree there that nothing reads again. Fails closed: a tree goes only when it resolves to
    exactly the mirror of `folder` (as spelled, or resolved) inside the prefix, so a symlink in the way, or a prefix that
    is not a directory, leaves everything alone; a tree it cannot remove is reported, never skipped silently."""
    if not prefix or not os.path.isdir(prefix):
        return
    real_prefix = os.path.realpath(prefix)
    spellings = {folder, os.path.realpath(folder)}
    expected = {os.path.join(real_prefix, spelling.lstrip(os.sep)) for spelling in spellings}
    for spelling in sorted(spellings):
        mirror = os.path.join(prefix, spelling.lstrip(os.sep))
        resolved = os.path.realpath(mirror)
        if resolved not in expected or os.path.islink(mirror) or not os.path.isdir(resolved):
            continue
        try:
            shutil.rmtree(resolved)
        except FileNotFoundError:
            pass
        except OSError as error:
            sys.stderr.write("cannot remove the bytecode cache tree %s: %s\n" % (resolved, error))


CLEAR_THREADS = 8


def clear_case_directories(base):
    """Removes what is under `base` from several threads, since a run leaves thousands of case directories and a serial
    rmtree after the last case was 3-5 s of the run. Never follows a symlink; what it cannot remove it leaves for the
    caller's own removal of the run directory, which stays the one that reports a failure."""
    try:
        children = list(os.scandir(base))
    except OSError:
        return

    def remove(entry):
        try:
            if entry.is_dir(follow_symlinks=False):
                shutil.rmtree(entry.path, ignore_errors=True)
            else:
                os.unlink(entry.path)
        except OSError:
            pass

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(CLEAR_THREADS) as pool:
        list(pool.map(remove, children))


@contextlib.contextmanager
def run_directory():
    with tempfile.TemporaryDirectory(prefix="veri-pytest-") as run:
        try:
            yield run
        finally:
            remove_scratch_mirror(sys.pycache_prefix, run)
            clear_case_directories(os.path.join(run, "base"))


def serial_pass_plan(rest, probe):
    """What the serial pass may be handed in place of `rest`'s targets: (its argv, the cases pass 1 collected), or None.

    None, which keeps the pass collecting `rest` whole, whenever the probe's record cannot show that the files it names
    hold every case the targets select: no record of the targets or of the files, workers that disagree, a target that
    names a case (`::`), or a target `rest` does not carry as given."""
    lines = probe.splitlines()
    named = {line[len("named "):] for line in lines if line.startswith("named ")}
    records = {line[len("args "):] for line in lines if line.startswith("args ")}
    files = list(dict.fromkeys(line[len("file "):] for line in lines if line.startswith("file ")))
    if len(named) != 1 or len(records) != 1 or not files:
        return None
    record = json.loads(records.pop())
    targets = record["targets"]
    if not targets or any("::" in target for target in targets):
        return None
    options = list(rest)
    for target in reversed(targets):
        if target not in options:
            return None
        del options[len(options) - 1 - options[::-1].index(target)]
    argv = options + ["--rootdir=" + record["root"]] + (["-c", record["ini"]] if record["ini"] else []) + files
    return argv, int(named.pop())


def split_marks(argv):
    rest, expressions = [], []
    args = iter(argv)
    for arg in args:
        if arg == "-m":
            expressions.append(next(args, ""))
        else:
            rest.append(arg)
    selected = "(%s) and " % " and ".join("(%s)" % e for e in expressions) if expressions else ""
    return rest, selected


def names(arg, root, nodeid, path):
    target, *parts = arg.split("::")
    where = os.path.realpath(os.path.join(root, target))
    here = os.path.realpath(path)
    if here != where and not here.startswith(where.rstrip(os.sep) + os.sep):
        return False
    held = nodeid.split("::")[1:]
    return len(held) >= len(parts) and all(
        own == part or (index == len(parts) - 1 and own.startswith(part + "["))
        for index, (own, part) in enumerate(zip(held, parts, strict=False)))


class Collected:
    """Records, per collect-only session, the cases left after the run's own -k selection and the targets named."""
    def __init__(self):
        self.cases, self.args, self.root = [], [], ""

    def pytest_collection_finish(self, session):
        self.cases = [(item.nodeid, str(item.path)) for item in session.items]
        self.args = list(session.config.args)
        self.root = str(session.config.invocation_params.dir)


def unrun_targets(collected, reported):
    unrun, targets = [], []
    for arg in collected.args:
        cases = [nodeid for nodeid, path in collected.cases if names(arg, collected.root, nodeid, path)]
        if cases and not any(nodeid in reported for nodeid in cases):
            targets.append(arg)
            unrun.extend(nodeid for nodeid in cases if nodeid not in unrun)
    return unrun, targets


def refuse_below_floor(floor, numbers, subject, version):
    if numbers >= [int(part) for part in floor.split(".")[:2]]:
        return False
    sys.stderr.write("veri needs Python %s or newer for the suites under skills/tdd/scripts/tests/py/; %s is version %s.\n"
                     % (floor, subject, version))
    return True


def main(argv):
    saved_path = list(sys.path)
    try:
        return _main(argv)
    finally:
        sys.path[:] = saved_path


def _main(argv):
    PASSES_RED[0] = False
    floor = launch_floor.python_floor()
    version = tunables.read("VERI_PYTHON_VERSION") or platform.python_version()
    numbers = [int(part) for part in re.findall("[0-9]+", version)[:2]]
    if refuse_below_floor(floor, numbers, sys.executable, version):
        return 2
    path_python = shutil.which("python3")
    try:
        probe = subprocess.run([path_python, "--version"], capture_output=True, text=True)
        found = re.search(r"Python ([0-9]+)\.([0-9]+)[0-9.]*", probe.stdout + probe.stderr)
    except Exception:
        found = None
    if found and refuse_below_floor(floor, [int(found.group(1)), int(found.group(2))], "PATH's python3 " + path_python, found.group(0)[len("Python "):]):
        return 2
    for package, module, tunable in (("pytest", "pytest", "VERI_PYTEST_IMPORTABLE"),
                                     ("pytest-timeout", "pytest_timeout", "VERI_PYTEST_TIMEOUT_IMPORTABLE"),
                                     ("pytest-xdist", "xdist", "VERI_PYTEST_XDIST_IMPORTABLE")):
        importable = tunables.read(tunable) or ("1" if importlib.util.find_spec(module) else "0")
        if importable != "1":
            sys.stderr.write("veri needs %s for the suites under skills/tdd/scripts/tests/py/; %s cannot import %s. "
                             "Install it with `make install-dev`.\n" % (package, sys.executable, module))
            return 2
    workers = tunables.get("VERI_PYTEST_WORKERS")
    if workers and not re.fullmatch("[1-9][0-9]*", workers):
        sys.stderr.write("VERI_PYTEST_WORKERS must be a whole number of at least 1; got %s.\n" % workers)
        return 2
    caps = [arg for arg in argv if arg.startswith("--cap=")]
    if caps and not re.fullmatch("--cap=[1-9][0-9]*", caps[-1]):
        sys.stderr.write("--cap must be a whole number of at least 1; got %s.\n" % caps[-1])
        return 2
    idle = tunables.get("VERI_PYTEST_IDLE")
    if not re.fullmatch("[1-9][0-9]*", idle):
        sys.stderr.write("VERI_PYTEST_IDLE must be a whole number of seconds of at least 1; got %s.\n" % (idle or "it set but empty"))
        return 2
    import pytest
    os.environ["TMPDIR"] = leg_tmpdir.PINNED_TMPDIR
    # The plugins load by name from the leg's directory; failed_cases from veri/; the plugins' `veri.x` from scripts/.
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(1, VERI)
    sys.path.insert(2, os.path.dirname(VERI))
    import idle_watch
    import load_timeouts
    leg_facts = dict(load_timeouts.LEG)
    outer = sys.modules.get("failed_cases")
    records = (outer.NODEIDS, outer.PASSED, outer.REPORTED, outer.NAMED) if outer else ()
    saved = [list(record) for record in records]
    for record in records:
        record.clear()
    os.environ["PYTEST_PLUGINS"] = ",".join(filter(None, [os.environ.get("PYTEST_PLUGINS"), "small_case_guard", "network_guard", "private_tmp_path", "serial_seen", "failed_cases", "idle_watch", "load_timeouts"]))
    def terminate(signum, frame):
        # Ends the leg here, not by raising into pytest.main: pytest would run the session-finish hooks, xdist's worker
        # teardown among them, and a hung worker held that teardown up to its own timeout (#4254).
        if not watch.end(128 + signum, lambda workers: "pytest leg ended by signal %d; workers %s ended\n" % (signum, workers)):
            signalled.append(signum)  # the leg's return owns its teardown: the leg exits 128 + signum once it is done
    conftest = sys.modules.get("conftest")
    entry = None
    full_lock = None
    subset = "--subset" in argv
    argv = [arg for arg in argv if arg != "--subset"]
    cap = int(caps[-1][len("--cap="):]) if caps else SUBSET_CAP if subset else None
    argv = [arg for arg in argv if not arg.startswith("--cap=")]
    serial_seen = os.environ.get("PYTEST_LEG_SERIAL_SEEN")
    held_run = None
    signalled = []

    def leg_cleanup():
        nonlocal entry, full_lock
        if entry:
            unregister(entry)
            entry = None
        if full_lock:
            full_lock.release()
            full_lock = None
        if held_run:
            remove_scratch_mirror(sys.pycache_prefix, held_run)
            shutil.rmtree(held_run, ignore_errors=True)

    watch = idle_watch.Watch(int(idle), os.dup(2))
    watch.cleanups.append(leg_cleanup)
    outer_watch = idle_watch.CURRENT[0]
    previous = signal.signal(signal.SIGTERM, terminate)
    previous_hup = signal.signal(signal.SIGHUP, terminate)
    try:
        if not subset and "-m" not in argv and not os.environ.get("PYTEST_XDIST_WORKER") and full_run_lock.enabled() and not full_run_lock.held_by_ancestor():
            full_lock = full_run_lock.acquire()
        sweep_dead_runs()
        with run_directory() as run:
            held_run = run
            base = os.path.join(run, "base")
            os.mkdir(base)
            with open(os.path.join(run, "pid"), "w") as record:
                record.write("%d\n" % os.getpid())
            if workers:
                count = worker_count(workers)
            else:
                count, entry, total = claim(watch.cleanups, cap)
                load_timeouts.LEG.update(workers=count, total=total)
            parallel = ["-n", str(count), "--dist", "worksteal"] if count >= 2 else []
            idle_watch.CURRENT[0] = watch
            watch.start()
            rest, selected = split_marks(argv)
            seen = os.path.join(run, "serial-seen")
            os.environ["PYTEST_LEG_SERIAL_SEEN"] = seen
            statuses = [pytest.main(parallel + ["--basetemp=" + base, "-m", selected + "not serial"] + rest)]
            import failed_cases
            combined = None
            probe = open(seen).read() if os.path.exists(seen) else None
            if probe is None or "serial" in probe.splitlines():
                plan = serial_pass_plan(rest, probe) if probe else None
                serial_args, collected_by_pass_1 = plan if plan else (rest, None)
                statuses.append(pytest.main(["--basetemp=" + base, "-m", selected + "serial"] + serial_args))
                if failed_cases.NAMED or failed_cases.REPORTED:
                    named = len(failed_cases.NAMED) if collected_by_pass_1 is None else collected_by_pass_1
                    combined = "%d named, %d run, %d passed, %d failed across both passes\n" % (
                        named, len(failed_cases.REPORTED), len(set(failed_cases.PASSED)), len(set(failed_cases.NODEIDS)))
            if subset and selected:
                collected = Collected()
                with contextlib.redirect_stdout(io.StringIO()):
                    pytest.main(["--collect-only", "-p", "no:cacheprovider", "--basetemp=" + base] + rest, plugins=[collected])
                unrun, targets = unrun_targets(collected, failed_cases.REPORTED)
                if unrun:
                    sys.stdout.write("%d unselected: named cases that neither pass ran (%s)\n" % (len(unrun), " ".join(targets)))
                    statuses.append(pytest.ExitCode.TESTS_FAILED)
            PASSES_RED[0] = not (pytest.ExitCode.OK in statuses and set(statuses) <= {pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED})
            if combined:
                sys.stdout.write(combined)
            if pytest.ExitCode.INTERNAL_ERROR in statuses:
                sys.stderr.write("the leg was cut short by an internal error; cases that had failed by then:\n")
                for nodeid in failed_cases.NODEIDS:
                    sys.stderr.write(nodeid + "\n")
    finally:
        returned = watch.stop()
        if not returned:
            watch.finished.wait()  # an end claimed the leg first: it runs the cleanups and exits, never this teardown
        idle_watch.CURRENT[0] = outer_watch
        load_timeouts.LEG.clear()
        load_timeouts.LEG.update(leg_facts)
        os.close(watch.out)
        for record, kept in zip(records, saved, strict=True):
            record.clear()
            record.update(kept) if isinstance(record, set) else record.extend(kept)
        if serial_seen is None:
            os.environ.pop("PYTEST_LEG_SERIAL_SEEN", None)
        else:
            os.environ["PYTEST_LEG_SERIAL_SEEN"] = serial_seen
        if returned:
            leg_cleanup()
        signal.signal(signal.SIGTERM, previous)
        signal.signal(signal.SIGHUP, previous_hup)
        if conftest is None:
            sys.modules.pop("conftest", None)
        else:
            sys.modules["conftest"] = conftest
    if signalled:
        sys.exit(128 + signalled[0])
    passed = {pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED}
    return 0 if pytest.ExitCode.OK in statuses and set(statuses) <= passed else 1


def launch(argv):
    """The leg as `make test` runs it: main's code, an exception escaping it exit 2 in entry.refusal's form, between the
    bytecode cache's check and its record. A check that raises is exit 2 before any pass; a record that raises is one
    such line too, and turns a green leg's 0 into 2 while leaving a failing leg's 1 as it is; so does an exception main's
    teardown raises after its passes ran (the run directory's removal, the lock's release, the registry entry's)."""
    prefix = sys.pycache_prefix
    try:
        cache_run = check_bytecode_cache(prefix) if prefix and os.path.isdir(prefix) else None
    except Exception as exc:
        sys.stderr.write(entry.refusal(main, exc))
        return 2
    code = None
    try:
        code = entry.exit_code(main, argv)
        if code == 2 and PASSES_RED[0]:
            code = 1  # the passes ran red; what failed after them is the one line exit_code wrote, not the answer
    finally:
        if cache_run:
            try:
                record_bytecode_cache(prefix, cache_run)
            except Exception as exc:
                sys.stderr.write(entry.refusal(main, exc))
                code = 2 if code == 0 else code
    return code


if __name__ == "__main__":
    sys.path[0] = os.getcwd()
    sys.exit(launch(sys.argv[1:]))
