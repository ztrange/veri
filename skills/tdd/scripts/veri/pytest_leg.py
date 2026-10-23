"""The pytest leg's launcher: refuses an interpreter below the Python floor, then runs pytest."""
# Usage:   pytest_leg.py [pytest-args...]
# Exit:    0 pytest passed, 1 any other pytest status
#          2 the interpreter is below the floor in lib/venv-python.sh, or cannot import pytest, pytest_timeout or xdist,
#            or VERI_PYTEST_WORKERS is not a whole number of at least 1
import fcntl
import importlib.util
import os
import platform
import re
import shutil
import signal
import sys
import tempfile

import launch_floor
import tunables


def worker_count(requested):
    if requested:
        return int(requested)
    if os.environ.get("PYTEST_XDIST_WORKER"):
        return 1
    cores = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count() or 1
    return max(1, cores - registered_workers(legs_dir()))


def legs_dir():
    return tunables.read("VERI_PYTEST_LEGS") or os.path.join(os.path.expanduser("~"), ".veri-pytest-legs")


def registered_workers(legs):
    if not legs or not os.path.isdir(legs):
        return 0
    total = 0
    for name in os.listdir(legs):
        try:
            if name.isdigit():
                try:
                    os.kill(int(name), 0)
                except PermissionError:
                    pass
            total += int(open(os.path.join(legs, name)).read())
        except (ValueError, OSError):
            continue
    return total


def claim():
    legs = legs_dir()
    os.makedirs(legs, exist_ok=True)
    with open(legs.rstrip("/") + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        count = worker_count(None)
        entry = os.path.join(legs, str(os.getpid()))
        with open(entry, "w") as f:
            f.write(str(count))
    return count, entry


def full_lock_path():
    return legs_dir().rstrip("/") + "-full.lock"


def under_full_lock_holder():
    holder = os.environ.get("PYTEST_LEG_FULL_LOCK_HOLDER", "")
    try:
        with open(full_lock_path()) as lock:
            recorded = lock.readline().split("\t")[0]
    except OSError:
        return False
    if not holder.isdigit() or recorded != "pid " + holder:
        return False
    try:
        os.kill(int(holder), 0)
    except PermissionError:
        pass
    except OSError:
        return False
    return True


def acquire_full_lock():
    lock = open(full_lock_path(), "a+")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lock.seek(0)
        sys.stderr.write("waiting for the full run holding the lock: %s\n" % " ".join(lock.read().split("\n")[0].split("\t")))
        sys.stderr.flush()
        fcntl.flock(lock, fcntl.LOCK_EX)
    lock.seek(0)
    lock.truncate()
    lock.write("pid %d\ttree %s\n" % (os.getpid(), os.path.realpath(os.getcwd())))
    lock.flush()
    return lock


def unregister(entry):
    try:
        os.remove(entry)
    except OSError:
        pass


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
            shutil.rmtree(folder, ignore_errors=True)
        except (ValueError, OSError):
            continue


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


def main(argv):
    floor = launch_floor.python_floor()
    version = tunables.read("VERI_PYTHON_VERSION") or platform.python_version()
    numbers = [int(part) for part in re.findall("[0-9]+", version)[:2]]
    if numbers < [int(part) for part in floor.split(".")[:2]]:
        sys.stderr.write("veri needs Python %s or newer for the suites under skills/tdd/scripts/tests/py/; %s is version %s.\n"
                         % (floor, sys.executable, version))
        return 2
    for package, module, tunable in (("pytest", "pytest", "VERI_PYTEST_IMPORTABLE"),
                                     ("pytest-timeout", "pytest_timeout", "VERI_PYTEST_TIMEOUT_IMPORTABLE"),
                                     ("pytest-xdist", "xdist", "VERI_PYTEST_XDIST_IMPORTABLE")):
        importable = tunables.read(tunable) or ("1" if importlib.util.find_spec(module) else "0")
        if importable != "1":
            sys.stderr.write("veri needs %s for the suites under skills/tdd/scripts/tests/py/; %s cannot import %s. "
                             "Install it with `make install-dev`.\n" % (package, sys.executable, module))
            return 2
    workers = tunables.read("VERI_PYTEST_WORKERS")
    if workers and not re.fullmatch("[1-9][0-9]*", workers):
        sys.stderr.write("VERI_PYTEST_WORKERS must be a whole number of at least 1; got %s.\n" % workers)
        return 2
    import pytest
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ["PYTEST_PLUGINS"] = ",".join(filter(None, [os.environ.get("PYTEST_PLUGINS"), "small_case_guard", "network_guard", "private_tmp_path", "serial_seen"]))
    def terminate(signum, frame):
        sys.exit(128 + signum)
    previous = signal.signal(signal.SIGTERM, terminate)
    previous_hup = signal.signal(signal.SIGHUP, terminate)
    conftest = sys.modules.get("conftest")
    entry = None
    full_lock = None
    holder = os.environ.get("PYTEST_LEG_FULL_LOCK_HOLDER")
    locking = tunables.read("VERI_TEST_LOCK") != "0"
    if "-m" not in argv and not os.environ.get("PYTEST_XDIST_WORKER") and locking and not under_full_lock_holder():
        full_lock = acquire_full_lock()
        os.environ["PYTEST_LEG_FULL_LOCK_HOLDER"] = str(os.getpid())
    serial_seen = os.environ.get("PYTEST_LEG_SERIAL_SEEN")
    try:
        sweep_dead_runs()
        with tempfile.TemporaryDirectory(prefix="veri-pytest-") as run:
            base = os.path.join(run, "base")
            os.mkdir(base)
            with open(os.path.join(run, "pid"), "w") as record:
                record.write("%d\n" % os.getpid())
            if workers:
                count = worker_count(workers)
            else:
                count, entry = claim()
            parallel = ["-n", str(count)] if count >= 2 else []
            rest, selected = split_marks(argv)
            seen = os.path.join(run, "serial-seen")
            os.environ["PYTEST_LEG_SERIAL_SEEN"] = seen
            statuses = [pytest.main(parallel + ["--basetemp=" + base, "-m", selected + "not serial"] + rest)]
            if not os.path.exists(seen) or "serial" in open(seen).read().split():
                statuses.append(pytest.main(["--basetemp=" + base, "-m", selected + "serial"] + rest))
    finally:
        if serial_seen is None:
            os.environ.pop("PYTEST_LEG_SERIAL_SEEN", None)
        else:
            os.environ["PYTEST_LEG_SERIAL_SEEN"] = serial_seen
        if entry:
            unregister(entry)
        if full_lock:
            if holder is None:
                os.environ.pop("PYTEST_LEG_FULL_LOCK_HOLDER", None)
            else:
                os.environ["PYTEST_LEG_FULL_LOCK_HOLDER"] = holder
            full_lock.close()
        signal.signal(signal.SIGTERM, previous)
        signal.signal(signal.SIGHUP, previous_hup)
        if conftest is None:
            sys.modules.pop("conftest", None)
        else:
            sys.modules["conftest"] = conftest
    passed = {pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED}
    return 0 if pytest.ExitCode.OK in statuses and set(statuses) <= passed else 1


if __name__ == "__main__":
    sys.path[0] = os.getcwd()
    sys.exit(main(sys.argv[1:]))
