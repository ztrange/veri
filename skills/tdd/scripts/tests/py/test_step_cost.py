"""In-process cases for veri/step_cost.py, the module step-cost.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def step_cost():
    return importlib.import_module("veri.step_cost")


def test_the_module_docstring_says_it_reports_leaf_spend_only_and_the_conductors_spending_is_in_no_usage_event(step_cost):
    doc = " ".join((step_cost.__doc__ or "").split())
    missing = [part for part in ("leaf spend only", "conductor's own spending is in no `usage` event")
               if part not in doc]
    assert missing == []
