"""The pytest leg's probe plugin: records in a file whether each collection held a case carrying the serial mark."""
import os

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    path = os.environ.get("PYTEST_LEG_SERIAL_SEEN")
    if path:
        with open(path, "a") as probe:
            probe.write("serial\n" if any(item.get_closest_marker("serial") for item in items) else "none\n")
