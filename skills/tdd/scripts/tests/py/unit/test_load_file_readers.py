"""Which of veri's own files outside its tests name the load file a load timeout lowers T through (PRD 036.7 LO10):
no conductor script may read VERI_TEST_LOAD_FILE, so none acts on a lowered T beyond the leg's own budget, save
dispatch lowering N when T is at its floor (PRD 036.8)."""
import os

import pytest

SCRIPTS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# The leg and its plugin, which write and read it; veri/ceiling.py, whose exit 0 removes it; veri/dispatch_live.py,
# which reads it for the t-lowered notice and, from T's floor, dispatch's N lowering; and the tunable's own declaration and its README row.
NAMERS = {"tests/leg/load_timeouts.py", "tests/leg/pytest_leg.py", "veri/ceiling.py", "veri/dispatch_live.py",
          "veri/tunables.py", "veri/README.md", "veri/leg_budget.py"}


def names_the_load_file(path):
    with open(path, errors="replace") as f:
        text = f.read()
    return "VERI_TEST_LOAD_FILE" in text or "load_timeouts" in text


@pytest.mark.tree_audit("skills/tdd/scripts outside tests/py, for files naming VERI_TEST_LOAD_FILE or load_timeouts")
def test_only_the_leg_its_plugin_ceiling_and_dispatch_name_the_load_file():
    named = set()
    for top, dirs, files in os.walk(SCRIPTS):
        dirs[:] = [d for d in dirs if not (top == os.path.join(SCRIPTS, "tests") and d == "py") and d != "__pycache__"]
        for name in files:
            path = os.path.join(top, name)
            if names_the_load_file(path):
                named.add(os.path.relpath(path, SCRIPTS))

    assert named - NAMERS == set()
