"""In-process cases for veri/parse_adjudication.py, the module parse-adjudication.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def parse_adjudication():
    return importlib.import_module("veri.parse_adjudication")


def test_main_with_no_argument_exits_2_printing_the_usage_line_on_stderr(run_cli, parse_adjudication):
    code, out, err = run_cli(parse_adjudication, [])
    assert (code, out, err) == (2, "", "usage: parse-adjudication.sh <leaf-output>\n")
