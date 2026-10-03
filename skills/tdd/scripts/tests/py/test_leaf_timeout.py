"""In-process cases for veri/leaf_timeout.py, the module leaf-timeout.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: leaf-timeout.sh <baseline-seconds> [refactor | --full <full-seconds>]"


@pytest.fixture
def leaf_timeout():
    return importlib.import_module("veri.leaf_timeout")


def test_main_refuses_a_baseline_of_ten_with_its_diagnostic_and_usage_and_returns_2(monkeypatch, capsys, leaf_timeout):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    code = leaf_timeout.main(["ten"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (
        2, "", "leaf-timeout: <baseline-seconds> must be a whole number >= 0: ten\n" + USAGE + "\n")
