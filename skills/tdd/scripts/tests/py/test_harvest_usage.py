"""In-process cases for veri/harvest_usage.py, the module harvest-usage.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def harvest_usage():
    return importlib.import_module("veri.harvest_usage")


def test_main_with_no_leaf_name_prints_usage_to_stderr_and_returns_2(capsys, harvest_usage):
    code = harvest_usage.main([])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (2, "", "usage: harvest-usage.sh <leaf-name>\n")
