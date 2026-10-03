"""In-process cases for veri/tier_usual.py, the module tier-usual.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def tier_usual():
    return importlib.import_module("veri.tier_usual")


def test_main_with_no_argument_returns_2_with_nothing_on_stdout_and_the_usage_line_on_stderr(capsys, tier_usual):
    code = tier_usual.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (2, "", "usage: tier-usual.sh <tier>\n")
