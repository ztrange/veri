"""The pytest leg's launcher: refuses an interpreter below the Python floor, then runs pytest."""
# Usage:   pytest_leg.py [pytest-args...]
# Exit:    0 pytest passed, 1 any other pytest status
#          2 the interpreter is below the floor in lib/venv-python.sh, or cannot import pytest, pytest_timeout or xdist,
#            or VERI_PYTEST_WORKERS is not a whole number of at least 1
import hashlib
import importlib.util
import json
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
    if hasattr(os, "sched_getaffinity"):
        return len(os.sched_getaffinity(0))
    return os.cpu_count() or 1


def drop_stale_bytecode(after_run=False):
    prefix = sys.pycache_prefix
    if not prefix:
        return
    manifest = os.path.join(prefix, "sources.json")
    known = {}
    try:
        with open(manifest) as handle:
            loaded = json.load(handle)
        if isinstance(loaded, dict):
            known = loaded
    except (OSError, ValueError):
        pass
    current = {}
    for folder, _, files in os.walk(prefix):
        source_dir = os.sep + os.path.relpath(folder, prefix)
        for name in files:
            if not name.endswith(".pyc"):
                continue
            if "-pytest-" in name or ".opt-" in name:
                if not after_run:
                    try:
                        os.remove(os.path.join(folder, name))
                    except FileNotFoundError:
                        pass
                continue
            path = os.path.join(source_dir, name.split(".cpython")[0] + ".py")
            if path not in current:
                try:
                    with open(path, "rb") as source:
                        current[path] = hashlib.sha256(source.read()).hexdigest()
                except OSError:
                    continue
            if (path in known or not after_run) and known.get(path) != current[path]:
                try:
                    os.remove(os.path.join(folder, name))
                except FileNotFoundError:
                    pass
    with open(manifest, "w") as handle:
        json.dump(current, handle)


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
    drop_stale_bytecode()
    import pytest
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    os.environ["PYTEST_PLUGINS"] = ",".join(filter(None, [os.environ.get("PYTEST_PLUGINS"), "small_case_guard", "network_guard", "private_tmp_path"]))
    def terminate(signum, frame):
        sys.exit(128 + signum)
    previous = signal.signal(signal.SIGTERM, terminate)
    try:
        with tempfile.TemporaryDirectory(prefix="veri-pytest-") as base:
            count = worker_count(workers)
            parallel = ["-n", str(count)] if count >= 2 else []
            status = pytest.main(["--basetemp=" + base] + parallel + argv)
            drop_stale_bytecode(after_run=True)
    finally:
        signal.signal(signal.SIGTERM, previous)
    return 0 if status == pytest.ExitCode.OK else 1


if __name__ == "__main__":
    sys.path[0] = os.getcwd()
    sys.exit(main(sys.argv[1:]))
