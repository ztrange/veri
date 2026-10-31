"""The pytest leg's record plugin: keeps the node id of each case that failed, in this process."""
NODEIDS = []


def pytest_runtest_logreport(report):
    if report.failed:
        NODEIDS.append(report.nodeid)
