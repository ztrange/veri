"""The pytest leg's record plugin: keeps, in this process, the cases each session collected and how each one reported."""
import pytest

NODEIDS = []
PASSED = []
REPORTED = set()
NAMED = []


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    NAMED[:] = [item.nodeid for item in items]


def pytest_runtest_logreport(report):
    REPORTED.add(report.nodeid)
    if report.failed:
        NODEIDS.append(report.nodeid)
    elif report.passed and report.when == "call":
        PASSED.append(report.nodeid)
