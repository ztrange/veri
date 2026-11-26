"""test-ceiling.sh's recorder plugin: in the leg's controller, appends each failing case to VERI_CEILING_RECORD."""
import json
import os
import re

import tunables

# pytest-timeout's own failure text (PYTEST_FAILURE_MESSAGE, "Timeout (>%ss) from pytest-timeout."), raised in the case
# by its signal method, the default on POSIX.
TIMEOUT_TEXT = re.compile(r"\bTimeout \(>[0-9.]+s\) from pytest-timeout\.")


def timed_out(report):
    """Whether <report> failed by its per-case timeout, not by any other failure."""
    return bool(TIMEOUT_TEXT.search(report.longreprtext))


def pytest_runtest_logreport(report):
    record = tunables.read("VERI_CEILING_RECORD")
    if not record or not report.failed or os.environ.get("PYTEST_XDIST_WORKER"):
        return
    with open(record, "a") as f:
        f.write(json.dumps({"nodeid": report.nodeid, "timeout": timed_out(report)}) + "\n")
