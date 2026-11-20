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


def pytest_runtest_logreport(report):
    if not LEG or os.environ.get("PYTEST_XDIST_WORKER") or not report.failed or not timed_out(report):
        return
    workers = LEG["workers"]
    now = time.time()
    test_file = report.nodeid.split("::")[0]
    with open(timeouts_path(), "a+") as f:
        f.seek(0)
        others = [line for line in f.read().splitlines() if line.split(" ")[2:3] != [test_file]]
        f.write("%d %d %s %s %d\n" % (now, os.getpid(), test_file, report.nodeid, workers))
    if others:
        lower(LEG["total"] - 2, now)
    event.mark("", event.context(tunables.environment()), "case-timeout", ["nodeid=" + report.nodeid, "workers=%d" % workers])


def lower(t, now):
    """Replaces the load file whole, through a temporary file beside it: <t> on line 1, <now> on line 2."""
    path = load_path()
    temporary = "%s.%d.tmp" % (path, os.getpid())
    with open(temporary, "w") as f:
        f.write("%d\n%d\n" % (t, now))
    os.replace(temporary, path)
