"""In-process cases for veri/unreplaced_cases.py, the guard that names a replaces-case step's cases with no pytest replacement."""
import importlib

import pytest


@pytest.fixture
def unreplaced():
    return importlib.import_module("veri.unreplaced_cases")


def test_main_exits_2_with_one_stderr_line_naming_the_step_when_its_case_names_are_unquoted_1538(tmp_path, run_cli, unreplaced):
    step = (
        "- [x] tests/py/test_tick_ledger.py calls veri.tick_ledger.main(argv) for a ticked step, an unmatched matcher "
        "and `[]` and asserts return codes 0, 3 and 2 — every exit inside 0–3: replaces the tick-ledger.sh half of the "
        "foreign ledger-transform code case in skills/tdd/scripts/tests/tick-ledger.test.sh, the "
        "clear-refactor-pending.sh case staying with its assertion unmodified ⟦replaces-case⟧ ⟦criterion 3⟧"
    )
    report = tmp_path / "report.txt"
    report.write_text("")

    code, out, err = run_cli(unreplaced, [step, str(report)], cwd=tmp_path)

    assert code == 2
    assert out == ""
    assert len(err.splitlines()) == 1
    assert "tick-ledger.sh half of the foreign ledger-transform code case" in err
    assert "Traceback" not in err and "AttributeError" not in err
