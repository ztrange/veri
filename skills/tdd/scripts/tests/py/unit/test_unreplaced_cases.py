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


def test_main_exits_0_with_nothing_on_stdout_when_the_mark_is_only_in_the_prose_1538(tmp_path, run_cli, unreplaced):
    step = (
        "- [ ] a guard that reads ⟦replaces-case⟧ only among a step's trailing marks and "
        "replaces 'first case', 'second case' in skills/tdd/scripts/tests/some.test.sh ⟦criterion 2⟧"
    )
    report = tmp_path / "report.txt"
    report.write_text("")

    code, out, err = run_cli(unreplaced, [step, str(report)], cwd=tmp_path)

    assert code == 0
    assert out == ""


def test_main_exits_0_with_nothing_on_stdout_when_the_replacement_is_a_parametrized_case_1826(tmp_path, run_cli, unreplaced):
    step = (
        "- [x] a port replaces 'first case' in skills/tdd/scripts/tests/some.test.sh "
        "⟦replaces-case⟧ ⟦criterion 1⟧"
    )
    (tmp_path / "test_x.py").write_text("def test_x(case):\n    assert case\n")
    report = tmp_path / "report.txt"
    report.write_text("REPLACES: first case => test_x.py::test_x[a ticked step to move]\n")

    code, out, err = run_cli(unreplaced, [step, str(report)], cwd=tmp_path)

    assert (code, out) == (0, "")


def test_main_exits_1_printing_the_case_when_a_parametrized_replacement_names_a_def_absent_from_its_file_1826(tmp_path, run_cli, unreplaced):
    step = (
        "- [x] a port replaces 'first case' in skills/tdd/scripts/tests/some.test.sh "
        "⟦replaces-case⟧ ⟦criterion 2⟧"
    )
    (tmp_path / "test_x.py").write_text("def test_other(case):\n    assert case\n")
    report = tmp_path / "report.txt"
    report.write_text("REPLACES: first case => test_x.py::test_x[a ticked step to move]\n")

    code, out, err = run_cli(unreplaced, [step, str(report)], cwd=tmp_path)

    assert (code, out) == (1, "first case\n")


def test_main_exits_1_printing_the_case_when_an_unparametrized_replacement_names_a_def_absent_from_its_file_1826(tmp_path, run_cli, unreplaced):
    step = (
        "- [x] a port replaces 'first case' in skills/tdd/scripts/tests/some.test.sh "
        "⟦replaces-case⟧ ⟦criterion 2⟧"
    )
    (tmp_path / "test_x.py").write_text("def test_other(case):\n    assert case\n")
    report = tmp_path / "report.txt"
    report.write_text("REPLACES: first case => test_x.py::test_x\n")

    code, out, err = run_cli(unreplaced, [step, str(report)], cwd=tmp_path)

    assert (code, out) == (1, "first case\n")
