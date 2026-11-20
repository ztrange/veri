"""The leg's load-timeout plugin (PRD 036.7): in the leg's controller, appends each case its per-case timeout fails to
VERI_TEST_TIMEOUTS_FILE and records it as a `case-timeout` event.

PYTEST_DONT_REWRITE: the leg imports this module before pytest loads it as a plugin."""
import os
import time

import event
import tunables
from ceiling_record import timed_out


# The leg's facts while its passes run, which the leg sets and restores: `workers`, the xdist workers it runs with.
LEG = {}


def timeouts_path():
    return tunables.get("VERI_TEST_TIMEOUTS_FILE") or os.path.join(os.path.expanduser("~"), ".veri-test-timeouts")


def pytest_runtest_logreport(report):
    if not LEG or os.environ.get("PYTEST_XDIST_WORKER") or not report.failed or not timed_out(report):
        return
    workers = LEG["workers"]
    with open(timeouts_path(), "a") as f:
        f.write("%d %d %s %s %d\n" % (time.time(), os.getpid(), report.nodeid.split("::")[0], report.nodeid, workers))
    event.mark("", event.context(tunables.environment()), "case-timeout", ["nodeid=" + report.nodeid, "workers=%d" % workers])
