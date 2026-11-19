"""test-ceiling.sh's recorder plugin: in the leg's controller, appends each failing case to VERI_CEILING_RECORD."""
import json
import os

import tunables


def pytest_runtest_logreport(report):
    record = tunables.read("VERI_CEILING_RECORD")
    if not record or not report.failed or os.environ.get("PYTEST_XDIST_WORKER"):
        return
    with open(record, "a") as f:
        f.write(json.dumps({"nodeid": report.nodeid}) + "\n")
