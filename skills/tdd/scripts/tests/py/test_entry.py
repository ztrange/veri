"""In-process cases for veri/entry.py, the one __main__ entry point every ported module calls."""
import importlib

import pytest


@pytest.fixture
def entry():
    return importlib.import_module("veri.entry")


def test_run_exits_with_the_code_main_returns_and_lets_a_raised_system_exit_through_unchanged_1150(entry):
    for code in (0, 1, 2, 3):
        seen = []

        def returns(argv, _code=code):
            seen.append(argv)
            return _code

        with pytest.raises(SystemExit) as exited:
            entry.run(returns, ["--flag", "value"])
        assert (exited.value.code, seen) == (code, [["--flag", "value"]])

    def raises(argv):
        raise SystemExit(7)

    with pytest.raises(SystemExit) as exited:
        entry.run(raises, [])
    assert exited.value.code == 7
