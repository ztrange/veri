"""In-process cases for veri/update_veri.py, the module update-veri.sh is a shim over."""
import importlib

import pytest

USAGE = "usage: update-veri.sh [--consent yes|no]\n"


@pytest.fixture
def update_veri():
    return importlib.import_module("veri.update_veri")


def test_main_exits_2_with_the_usage_line_and_writes_no_record_for_a_consent_value_other_than_yes_or_no_a_missing_value_or_any_other_argument(
        tmp_path, run_cli, update_veri):
    record = tmp_path / "self-update"
    results = {}
    for argv in (["--consent", "maybe"], ["--consent"], ["--consent", ""], ["--bogus"], ["yes"],
                 ["--consent", "yes", "extra"]):
        results[tuple(argv)] = run_cli(update_veri, argv, env={"VERI_SELF_UPDATE_FILE": str(record)})

    assert results == {argv: (2, "", USAGE) for argv in results}
    assert not record.exists()
