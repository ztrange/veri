"""In-process cases for veri/build_adjudicate_prompt.py, the module build-adjudicate-prompt.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def build_adjudicate_prompt():
    return importlib.import_module("veri.build_adjudicate_prompt")


def test_main_with_no_argument_exits_2_printing_the_usage_line_on_stderr(run_cli, build_adjudicate_prompt):
    code, out, err = run_cli(build_adjudicate_prompt, [])
    assert (code, out, err) == (
        2,
        "",
        "usage: build-adjudicate-prompt.sh <n> <cause> <exit-code> <stderr-file> <command…>\n",
    )
