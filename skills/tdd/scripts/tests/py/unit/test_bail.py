"""In-process cases for veri/bail.py, the module bail.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def bail():
    return importlib.import_module("veri.bail")


def test_no_argument_prints_a_usage_line_naming_bail_md_sub_step_1_on_stderr_and_exits_2_with_no_call(
        run_cli, fake_processes, bail):
    fake = fake_processes.answers({})

    code, out, err = run_cli(bail, [])

    assert (code, out, fake.calls) == (2, "", [])
    assert err.strip() != "" and "usage" in err.splitlines()[0]
    assert "BAIL.md sub-step 1" in err.splitlines()[-1]
