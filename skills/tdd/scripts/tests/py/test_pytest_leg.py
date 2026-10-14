"""In-process cases for veri/pytest_leg.py, the launcher that makes the pytest leg's refusals and then runs pytest."""
import importlib
import sys

import pytest


@pytest.fixture
def pytest_leg():
    return importlib.import_module("veri.pytest_leg")


def test_an_interpreter_below_the_floor_exits_2_naming_the_floor_the_interpreter_and_its_version(pytest_leg, run_cli):
    code, out, err = run_cli(pytest_leg, [], env={"VERI_PYTHON_VERSION": "3.11.9"})
    assert (code, out, err) == (
        2,
        "",
        "veri needs Python 3.12 or newer for the suites under skills/tdd/scripts/tests/py/; %s is version 3.11.9.\n"
        % sys.executable,
    )


def test_an_interpreter_that_cannot_import_pytest_exits_2_naming_pytest_the_interpreter_and_make_install_dev(pytest_leg, run_cli):
    code, out, err = run_cli(pytest_leg, [], env={"VERI_PYTEST_IMPORTABLE": "0"})
    assert (code, out, err) == (
        2,
        "",
        "veri needs pytest for the suites under skills/tdd/scripts/tests/py/; %s cannot import pytest. "
        "Install it with `make install-dev`.\n" % sys.executable,
    )
