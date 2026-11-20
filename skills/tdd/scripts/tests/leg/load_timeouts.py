"""The leg's load-timeout plugin (PRD 036.7): in the leg's controller, appends each case its per-case timeout fails to
VERI_TEST_TIMEOUTS_FILE and records it as a `case-timeout` event; a load timeout, one appended while the file holds a
line from another test file, lowers T by 2 through VERI_TEST_LOAD_FILE.

PYTEST_DONT_REWRITE: the leg imports this module before pytest loads it as a plugin."""
import os
import time

import event
import tunables
from ceiling_record import timed_out


# The leg's facts while its passes run, which the leg sets and restores: `workers`, the xdist workers it runs with,
# and `total`, the T it claimed them out of.
LEG = {}


def timeouts_path():
    return tunables.get("VERI_TEST_TIMEOUTS_FILE") or os.path.join(os.path.expanduser("~"), ".veri-test-timeouts")


def load_path():
    return tunables.get("VERI_TEST_LOAD_FILE") or os.path.join(os.path.expanduser("~"), ".veri-test-load")


def held():
    """The lowered T on line 1 of the load file when it is a whole number of at least 2, else None."""
    try:
        with open(load_path()) as f:
            first = f.readline().strip()
    except FileNotFoundError:
        return None
    return int(first) if first.isascii() and first.isdigit() and int(first) >= 2 else None


def window():
    """VERI_LOAD_WINDOW: the seconds a timeouts line counts toward a load timeout; 600 for anything but a whole number."""
    raw = tunables.get("VERI_LOAD_WINDOW", unless_empty=True)
    return int(raw) if raw.isascii() and raw.isdigit() else 600


def recent_other(line, test_file, since):
    """Whether timeouts <line> is another test file's, appended at or after <since>."""
    fields = line.split(" ")
    return len(fields) >= 3 and fields[0].isdigit() and int(fields[0]) >= since and fields[2] != test_file


def pytest_runtest_logreport(report):
    if not LEG or os.environ.get("PYTEST_XDIST_WORKER") or not report.failed or not timed_out(report):
        return
    workers = LEG["workers"]
    now = time.time()
    test_file = report.nodeid.split("::")[0]
    with open(timeouts_path(), "a+") as f:
        f.seek(0)
        since = now - window()
        others = [line for line in f.read().splitlines() if recent_other(line, test_file, since)]
        f.write("%d %d %s %s %d\n" % (now, os.getpid(), test_file, report.nodeid, workers))
    if others:
        lower(max(2, LEG["total"] - 2), now)
    event.mark("", event.context(tunables.environment()), "case-timeout", ["nodeid=" + report.nodeid, "workers=%d" % workers])


def lower(t, now):
    """Replaces the load file whole, through a temporary file beside it: <t> on line 1, <now> on line 2."""
    path = load_path()
    temporary = "%s.%d.tmp" % (path, os.getpid())
    with open(temporary, "w") as f:
        f.write("%d\n%d\n" % (t, now))
    os.replace(temporary, path)
