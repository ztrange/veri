"""In-process cases for veri/branch_suite.py, the module branch-suite.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def branch_suite():
    return importlib.import_module("veri.branch_suite")


def test_main_prints_an_explicit_ci_or_local_as_given(tmp_path, run_cli, branch_suite):
    ci = run_cli(branch_suite, [], env={"VERI_BRANCH_SUITE": "ci"}, cwd=tmp_path)
    local = run_cli(branch_suite, [], env={"VERI_BRANCH_SUITE": "local"}, cwd=tmp_path)

    assert ci[:2] == (0, "ci\n")
    assert local[:2] == (0, "local\n")
