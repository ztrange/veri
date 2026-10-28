"""In-process cases for veri/mutation_probe.py, the module mutation-probe.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def mutation_probe():
    return importlib.import_module("veri.mutation_probe")


def test_main_with_no_argument_prints_the_usage_line_and_exits_2(run_cli, mutation_probe):
    code, out, err = run_cli(mutation_probe, [])
    assert code == 2
    assert out == ""
    assert "mutation-probe.sh <file> <old> <new> -- <command…>" in err
