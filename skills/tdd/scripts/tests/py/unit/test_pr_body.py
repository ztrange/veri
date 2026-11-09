"""In-process cases for veri/pr_body.py, the module pr-body.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def pr_body():
    return importlib.import_module("veri.pr_body")


def test_main_with_no_argument_exits_2_with_a_usage_line_naming_pr_number_and_body_file_3453(run_cli, pr_body):
    code, out, err = run_cli(pr_body, [])

    assert (code, out) == (2, "")
    assert "pr-body.sh <pr-number> <body-file>" in err
