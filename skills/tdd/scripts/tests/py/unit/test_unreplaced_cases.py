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


THREE = "- [ ] x: replaces 'first case', 'second case', 'third case' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
THREE_TESTS = "def test_first():\n    pass\n\n\ndef test_second():\n    pass\n\n\ndef test_third():\n    pass\n"


def unreplaced_in(tmp_path, run_cli, unreplaced, step, lines, files):
    for name, source in files.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(source)
    report = tmp_path / "report.txt"
    report.write_text("".join(line + "\n" for line in lines))
    return run_cli(unreplaced, [step, str(report)], cwd=tmp_path)


def test_run_with_no_arguments_exits_2_with_its_usage_line_on_stderr_1521(run_cli, unreplaced):
    code, out, err = run_cli(unreplaced, [])

    assert code == 2
    assert err.startswith("usage:")


def test_run_with_no_arguments_leaves_stdout_empty_1521(run_cli, unreplaced):
    code, out, err = run_cli(unreplaced, [])

    assert out == ""


def test_step_naming_three_cases_and_a_report_replacing_two_prints_the_third_1521(tmp_path, run_cli, unreplaced):
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, THREE, [
        "REPLACES: first case => tests/py/test_x.py::test_first",
        "REPLACES: second case => tests/py/test_x.py::test_second",
    ], {"tests/py/test_x.py": THREE_TESTS})

    assert (code, out.strip()) == (1, "third case")


def test_step_naming_three_cases_and_a_report_replacing_all_three_prints_nothing_1521(tmp_path, run_cli, unreplaced):
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, THREE, [
        "REPLACES: first case => tests/py/test_x.py::test_first",
        "REPLACES: second case => tests/py/test_x.py::test_second",
        "REPLACES: third case => tests/py/test_x.py::test_third",
    ], {"tests/py/test_x.py": THREE_TESTS})

    assert (code, out) == (0, "")


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


def test_replaces_line_naming_a_test_absent_from_the_tree_stays_printed_1521(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces 'first case', 'second case' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: first case => tests/py/test_x.py::test_first",
        "REPLACES: second case => tests/py/test_x.py::test_second",
    ], {"tests/py/test_x.py": "def test_first():\n    pass\n"})

    assert (code, out.strip()) == (1, "second case")


def test_step_naming_three_cases_and_a_report_replacing_the_second_and_third_prints_the_first_1521(tmp_path, run_cli, unreplaced):
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, THREE, [
        "REPLACES: second case => tests/py/test_x.py::test_second",
        "REPLACES: third case => tests/py/test_x.py::test_third",
    ], {"tests/py/test_x.py": THREE_TESTS})

    assert (code, out.strip()) == (1, "first case")


def test_replaces_claim_written_in_the_working_tree_in_an_existing_file_counts_1521(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces 'first case', 'second case' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: first case => tests/py/test_x.py::test_first",
        "REPLACES: second case => tests/py/test_x.py::test_second",
    ], {"tests/py/test_x.py": "def test_first():\n    pass\n\n\ndef test_second():\n    pass\n"})

    assert (code, out) == (0, "")


def test_replaces_claim_naming_a_test_file_missing_from_the_working_tree_stays_printed_1521(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces 'first case' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: first case => tests/py/test_missing.py::test_first",
    ], {})

    assert (code, out.strip()) == (1, "first case")


def test_step_naming_the_mark_but_carrying_no_replaces_clause_prints_no_case_1603(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: the Red prompt for replaces-case steps ⟦replaces-case⟧ ⟦criterion 1⟧"
    code, out, err = unreplaced_in(tmp_path, run_cli, unreplaced, step, [], {})

    assert (code, out, err) == (0, "", "")


def test_replaces_line_wrapped_in_the_steps_backticks_counts_1600(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces `first case` in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: `first case` => tests/py/test_x.py::test_a",
    ], {"tests/py/test_x.py": "def test_a():\n    pass\n"})

    assert (code, out) == (0, "")


def test_replaces_line_wrapped_in_the_steps_double_quotes_counts_1600(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces \"it's a case\" in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: \"it's a case\" => tests/py/test_x.py::test_a",
    ], {"tests/py/test_x.py": "def test_a():\n    pass\n"})

    assert (code, out) == (0, "")
