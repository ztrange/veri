"""The pytest leg's record plugin: keeps the node id of each case that failed, in this process."""
NODEIDS = []
PASSED = []
REPORTED = set()


def pytest_runtest_logreport(report):
    REPORTED.add(report.nodeid)
    if report.failed:
        NODEIDS.append(report.nodeid)
    elif report.passed and report.when == "call":
        PASSED.append(report.nodeid)
