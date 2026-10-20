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


TEST_A = {"tests/py/test_x.py": "def test_a():\n    pass\n"}
TAIL = " in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"


def test_replaces_line_with_a_bare_name_holding_both_quote_characters_counts_1600(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces `it's a \"quoted\" case`" + TAIL
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: it's a \"quoted\" case => tests/py/test_x.py::test_a",
    ], TEST_A)

    assert (code, out) == (0, "")


def test_replaces_line_naming_a_different_case_in_the_steps_backticks_leaves_the_steps_case_printed_1600(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces `first case`" + TAIL
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: `other case` => tests/py/test_x.py::test_b",
    ], {"tests/py/test_x.py": "def test_b():\n    pass\n"})

    assert (code, out.strip()) == (1, "first case")


def test_replaces_lines_wrapping_the_name_in_single_or_double_quotes_leave_a_backtick_step_case_printed_1600(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces `a`" + TAIL
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: 'a' => tests/py/test_x.py::test_a",
        'REPLACES: "a" => tests/py/test_x.py::test_a',
    ], TEST_A)

    assert (code, out.strip()) == (1, "a")


def test_single_quoted_replaces_line_answers_only_the_bare_name_of_a_backtick_step_1600(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces `'a'`, `a`" + TAIL
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: 'a' => tests/py/test_x.py::test_a",
    ], TEST_A)

    assert (code, out.strip()) == (1, "a")


def test_replaces_line_wrapped_in_one_pair_of_single_quotes_the_steps_delimiter_counts_1600(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces 'a'" + TAIL
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: 'a' => tests/py/test_x.py::test_a",
    ], TEST_A)

    assert (code, out) == (0, "")


def test_replaces_line_with_the_steps_name_unescaped_counts_1617(tmp_path, run_cli, unreplaced):
    step = r"- [ ] x: replaces '\`### 🔴 Red\`'" + TAIL
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: `### 🔴 Red` => tests/py/test_x.py::test_a",
    ], TEST_A)

    assert (code, out) == (0, "")


def test_replaces_line_keeping_the_steps_backslash_escapes_counts_1617(tmp_path, run_cli, unreplaced):
    step = r"- [ ] x: replaces '\`### 🔴 Red\`'" + TAIL
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        r"REPLACES: \`### 🔴 Red\` => tests/py/test_x.py::test_a",
    ], TEST_A)

    assert (code, out) == (0, "")


def test_replaces_line_differing_once_escapes_are_removed_leaves_the_steps_case_printed_1617(tmp_path, run_cli, unreplaced):
    step = r"- [ ] x: replaces '\`### 🔴 Red\`'" + TAIL
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: `### 🔴 Green` => tests/py/test_x.py::test_a",
    ], TEST_A)

    assert (code, out.strip()) == (1, r"\`### 🔴 Red\`")


def test_each_of_the_escapes_quote_dollar_and_backslash_counts_on_its_own_1617(tmp_path, run_cli, unreplaced):
    step = r"- [ ] x: replaces 'say \"hi\"', 'cost \$5', 'path a\\b'" + TAIL
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        'REPLACES: say "hi" => tests/py/test_x.py::test_a',
        "REPLACES: cost $5 => tests/py/test_x.py::test_a",
        r"REPLACES: path a\b => tests/py/test_x.py::test_a",
    ], TEST_A)

    assert (code, out) == (0, "")


def test_only_the_steps_name_is_unescaped_not_the_replaces_name_1617(tmp_path, run_cli, unreplaced):
    step = r"- [ ] x: replaces 'a\\$b'" + TAIL
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        r"REPLACES: a\$b => tests/py/test_x.py::test_a",
    ], TEST_A)

    assert (code, out) == (0, "")


def test_two_reports_each_replacing_one_case_count_both_as_replaced_1625(tmp_path, run_cli, unreplaced):
    (tmp_path / "tests/py").mkdir(parents=True)
    (tmp_path / "tests/py/test_x.py").write_text("def test_a():\n    pass\n\n\ndef test_b():\n    pass\n")
    first, second = tmp_path / "r1.txt", tmp_path / "r2.txt"
    first.write_text("REPLACES: case a => tests/py/test_x.py::test_a\n")
    second.write_text("REPLACES: case b => tests/py/test_x.py::test_b\n")
    step = "- [ ] x: replaces 'case a', 'case b'" + TAIL

    code, out, _ = run_cli(unreplaced, [step, str(first), str(second)], cwd=tmp_path)

    assert (code, out) == (0, "")


PY_UNIT = "skills/tdd/scripts/tests/py/unit"
BARE_TAIL = " in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 3⟧"


def test_replaces_line_with_a_markdown_bullet_in_front_counts_like_the_same_line_without_it_1660(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces 'case a', 'case b'" + TAIL
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "- REPLACES: case a => tests/py/test_x.py::test_a",
        "* REPLACES: case b => tests/py/test_x.py::test_b",
    ], {"tests/py/test_x.py": "def test_a():\n    pass\n\n\ndef test_b():\n    pass\n"})

    assert (code, out) == (0, "")


def test_replaces_line_with_a_star_bullet_in_front_counts_like_the_same_line_without_it_1660(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces 'case a'" + TAIL
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "* REPLACES: case a => tests/py/test_x.py::test_a",
    ], TEST_A)

    assert (code, out) == (0, "")


def test_bare_name_replaces_line_counts_when_exactly_one_test_function_of_that_name_exists_1660(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces 'case a'" + BARE_TAIL
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: case a => test_a",
    ], {PY_UNIT + "/test_x.py": "def test_a():\n    pass\n"})

    assert (code, out) == (0, "")


def test_bare_name_replaces_line_is_unreplaced_when_no_test_function_of_that_name_exists_1660(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces 'case a'" + BARE_TAIL
    code, out, err = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: case a => test_a",
    ], {PY_UNIT + "/test_x.py": "def test_other():\n    pass\n"})

    assert code == 1
    assert "case a" in out
    assert "no test of that name was found" in out + err


def test_bare_name_replaces_line_is_unreplaced_when_several_test_functions_of_that_name_exist_1660(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces 'case a'" + BARE_TAIL
    code, out, err = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: case a => test_a",
    ], {PY_UNIT + "/test_x.py": "def test_a():\n    pass\n", PY_UNIT + "/test_y.py": "def test_a():\n    pass\n"})

    assert code == 1
    assert "case a" in out
    assert "ambiguous" in out + err


def test_unreplaced_bare_name_case_goes_to_stdout_as_the_step_spells_it_and_the_reason_to_stderr_1660(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces 'case a'" + BARE_TAIL
    code, out, err = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: case a => test_a",
    ], {PY_UNIT + "/test_x.py": "def test_other():\n    pass\n"})

    assert (code, out.strip()) == (1, "case a")
    assert "no test of that name was found" in err


def test_bare_name_replaces_line_is_unreplaced_when_the_only_function_of_that_name_is_a_helper_1660(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces 'case a'" + BARE_TAIL
    code, out, _ = unreplaced_in(tmp_path, run_cli, unreplaced, step, [
        "REPLACES: case a => make_a",
    ], {PY_UNIT + "/test_x.py": "def make_a():\n    pass\n"})

    assert (code, out.strip()) == (1, "case a")


def refuses_with_one_line_naming(tmp_path, run_cli, step, fragment):
    survivors = importlib.import_module("veri.replaces_case_survivors")
    unreplaced = importlib.import_module("veri.unreplaced_cases")
    report = tmp_path / "report.txt"
    report.write_text("")
    for module, argv in ((unreplaced, [step, str(report)]), (survivors, [step])):
        code, out, err = run_cli(module, argv, cwd=tmp_path)

        assert code == 2
        assert len(err.splitlines()) == 1
        assert fragment in err
        assert "Traceback" not in err


def test_both_scripts_exit_2_naming_the_step_when_an_unquoted_name_follows_a_quoted_one_1538(tmp_path, run_cli):
    refuses_with_one_line_naming(
        tmp_path, run_cli,
        "- [ ] x: replaces 'a', b in t/x.test.sh ⟦replaces-case⟧ ⟦criterion 5⟧",
        "replaces 'a', b in t/x",
    )


def test_both_scripts_exit_2_naming_the_step_when_a_quoted_name_is_followed_by_a_parenthetical_1538(tmp_path, run_cli):
    refuses_with_one_line_naming(
        tmp_path, run_cli,
        "- [ ] x: replaces 'a' (from #12) in t/x.test.sh ⟦replaces-case⟧ ⟦criterion 5⟧",
        "replaces 'a' (from #12) in t/x",
    )


def test_unreplaced_cases_exits_2_naming_the_step_and_the_suite_when_the_suite_is_not_a_test_sh_file_1538(tmp_path, run_cli, unreplaced):
    step = "- [ ] x: replaces 'a' in t/x.py ⟦replaces-case⟧ ⟦criterion 6⟧"
    report = tmp_path / "report.txt"
    report.write_text("")

    code, out, err = run_cli(unreplaced, [step, str(report)], cwd=tmp_path)

    assert code == 2
    assert len(err.splitlines()) == 1
    assert "replaces 'a' in t/x.py" in err
    assert "t/x.py" in err
