"""The pytest leg's launcher: refuses an interpreter below the Python floor, then runs pytest."""
# Usage:   pytest_leg.py [pytest-args...]
# Exit:    0 pytest passed, 1 any other pytest status
#          2 the interpreter is below the floor in lib/venv-python.sh, or cannot import pytest, pytest_timeout or xdist,
#            or VERI_PYTEST_WORKERS is not a whole number of at least 1
import importlib.util
import os
import platform
import re
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
    return max(1, cores - registered_workers(tunables.read("VERI_PYTEST_LEGS") or default_legs()))


def default_legs():
    return os.path.join(tempfile.gettempdir(), "veri-pytest-legs-%d" % os.getuid())


def registered_workers(legs):
    if not legs or not os.path.isdir(legs):
        return 0
    total = 0
    for name in os.listdir(legs):
        try:
            total += int(open(os.path.join(legs, name)).read())
        except (ValueError, OSError):
            continue
    return total


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
    conftest = sys.modules.get("conftest")
    try:
        with tempfile.TemporaryDirectory(prefix="veri-pytest-") as run:
            base = os.path.join(run, "base")
            os.mkdir(base)
            count = worker_count(workers)
            parallel = ["-n", str(count)] if count >= 2 else []
            rest, selected = split_marks(argv)
            seen = os.path.join(run, "serial-seen")
            os.environ["PYTEST_LEG_SERIAL_SEEN"] = seen
            statuses = [pytest.main(["--basetemp=" + base] + parallel + ["-m", selected + "not serial"] + rest)]
            if not os.path.exists(seen) or "serial" in open(seen).read().split():
                statuses.append(pytest.main(["--basetemp=" + base, "-m", selected + "serial"] + rest))
    finally:
        signal.signal(signal.SIGTERM, previous)
        if conftest is None:
            sys.modules.pop("conftest", None)
        else:
            sys.modules["conftest"] = conftest
    passed = {pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED}
    return 0 if pytest.ExitCode.OK in statuses and set(statuses) <= passed else 1


if __name__ == "__main__":
    sys.path[0] = os.getcwd()
    sys.exit(main(sys.argv[1:]))
