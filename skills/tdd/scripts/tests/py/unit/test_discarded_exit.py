"""discarded-exit.sh prints each added .py line of `git diff HEAD` whose exit code is discarded."""
import importlib

import pytest


@pytest.fixture
def discarded_exit():
    return importlib.import_module("veri.discarded_exit")


def test_any_argument_prints_the_usage_line_on_stderr_and_exits_2(run_cli, discarded_exit):
    code, out, err = run_cli(discarded_exit, ["x"])

    assert (code, out) == (2, "")
    assert err.splitlines()[-1] == "usage: discarded-exit.sh"
