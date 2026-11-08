"""In-process cases for veri/dispatch.py, the module dispatch.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def dispatch():
    return importlib.import_module("veri.dispatch")


def test_main_with_no_target_prints_the_usage_line_on_stderr_and_exits_2(run_cli, dispatch):
    code, out, err = run_cli(dispatch, [])
    assert (code, out, err) == (2, "", "usage: dispatch.sh --target <N>\n")
