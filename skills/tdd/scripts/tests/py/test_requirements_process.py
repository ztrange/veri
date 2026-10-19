"""Cases for requirements.sh's units and claims verbs, through the real entry point."""
import re
import subprocess

import pytest

from conftest import SCRIPTS

REQUIREMENTS = SCRIPTS / "requirements.sh"
UNIT = "skills/tdd/SKILL.md"
H = "##"


def table(*rows, header="| ID | Requirement | Why |"):
    divider = "|" + "|".join("-" * (len(c) + 2) for c in header.strip("|").split("|")) + "|"
    return "\n".join([f"{H} {UNIT}", "", header, divider, *rows]) + "\n"


def run(*argv):
    ran = subprocess.run([str(REQUIREMENTS), *argv], stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return ran.returncode, ran.stdout, ran.stderr


def claims_refused_naming_line(tmp_path, body, line):
    path = tmp_path / "r.md"
    path.write_text(body)
    code, out, err = run("claims", str(path), UNIT)
    assert code == 2
    assert out == ""
    assert re.search(rf"(^|[^0-9]){line}([^0-9]|$)", err.replace(str(tmp_path), ""))


@pytest.mark.process("requirements.sh units run as a script")
def test_units_prints_each_declared_prose_unit_one_per_line_in_file_order(tmp_path):
    path = tmp_path / "REQUIREMENTS.md"
    path.write_text(
        "# Requirements\n\n"
        + "".join(f"{H} {unit}\n\n| ID | Requirement | Why |\n|----|-------------|-----|\n| A1 | Says. | Because. |\n\n"
                 for unit in ("skills/tdd/SKILL.md", "skills/tdd/SKILL.md#Phase two", "guide/unit.md")))
    assert run("units", str(path)) == (
        0, "skills/tdd/SKILL.md\nskills/tdd/SKILL.md#Phase two\nguide/unit.md\n", "")


@pytest.mark.process("requirements.sh claims run as a script")
def test_claims_prints_a_units_rows_as_id_tab_requirement_in_table_order_with_no_why_text(tmp_path):
    path = tmp_path / "two-rows.md"
    path.write_text(table("| A1 | Says one thing. | Because secret-one. |",
                          "| A2 | Says two things. | Since secret-two. |"))
    assert run("claims", str(path), UNIT) == (0, "A1\tSays one thing.\nA2\tSays two things.\n", "")


@pytest.mark.process("requirements.sh claims run as a script")
def test_claims_on_a_repeated_id_exits_2_prints_nothing_on_stdout_and_names_the_duplicate_rows_line_on_stderr(tmp_path):
    claims_refused_naming_line(tmp_path, table("| A1 | Says one thing. | Because. |",
                                               "| A1 | Says it again. | Since. |"), 6)


@pytest.mark.process("requirements.sh claims run as a script")
def test_claims_on_a_row_with_an_empty_requirement_exits_2_prints_nothing_on_stdout_and_names_that_rows_line_on_stderr(tmp_path):
    claims_refused_naming_line(tmp_path, table("| A1 | Says one thing. | Because. |",
                                               "| A2 |  | Since. |"), 6)


@pytest.mark.process("requirements.sh claims run as a script")
def test_claims_on_a_row_with_an_empty_id_exits_2_prints_nothing_on_stdout_and_names_that_rows_line_on_stderr(tmp_path):
    claims_refused_naming_line(tmp_path, table("| A1 | Says one thing. | Because. |",
                                               "|  | Says another. | Since. |"), 6)


@pytest.mark.process("requirements.sh claims run as a script")
def test_claims_on_a_table_header_lacking_a_column_exits_2_prints_nothing_on_stdout_and_names_the_headers_line_on_stderr(tmp_path):
    claims_refused_naming_line(tmp_path, table("| A1 | Says one thing. |", header="| ID | Requirement |"), 3)


@pytest.mark.process("requirements.sh claims run as a script")
def test_claims_on_a_table_header_lacking_the_id_column_exits_2_prints_nothing_on_stdout_and_names_the_headers_line_on_stderr(tmp_path):
    claims_refused_naming_line(tmp_path, table("| A1 | Says one thing. | Because. |",
                                               header="| Key | Requirement | Why |"), 3)


@pytest.mark.process("requirements.sh claims run as a script")
def test_claims_on_a_file_that_does_not_exist_exits_2_prints_nothing_on_stdout_and_says_on_stderr_the_file_is_missing_naming_it(tmp_path):
    absent = tmp_path / "absent.md"
    code, out, err = run("claims", str(absent), UNIT)
    assert (code, out) == (2, "")
    assert "missing" in err and str(absent) in err


@pytest.mark.process("requirements.sh claims run as a script")
def test_claims_on_a_unit_the_file_does_not_declare_exits_2_prints_nothing_on_stdout_and_says_on_stderr_the_unit_is_not_declared_naming_it(tmp_path):
    path = tmp_path / "two-rows.md"
    path.write_text(table("| A1 | Says one thing. | Because. |"))
    code, out, err = run("claims", str(path), "skills/tdd/NOPE.md")
    assert (code, out) == (2, "")
    assert "not declared" in err and "skills/tdd/NOPE.md" in err


@pytest.mark.process("requirements.sh claims run as a script")
def test_claims_on_a_table_header_lacking_the_requirement_column_exits_2_prints_nothing_on_stdout_and_names_the_headers_line_on_stderr(tmp_path):
    claims_refused_naming_line(tmp_path, table("| A1 | Because. |", header="| ID | Why |"), 3)


@pytest.mark.process("requirements.sh claims run as a script")
def test_claims_on_a_unit_whose_table_header_is_key_value_exits_2_prints_nothing_on_stdout_and_names_the_headers_line_on_stderr(tmp_path):
    claims_refused_naming_line(tmp_path, table("| A1 | Says one thing. |", header="| Key | Value |"), 3)


@pytest.mark.process("requirements.sh claims run as a script")
def test_claims_on_a_unit_whose_table_header_is_id_requirement_why_extra_exits_2_prints_nothing_on_stdout_and_names_the_headers_line_on_stderr(tmp_path):
    claims_refused_naming_line(tmp_path, table("| A1 | Says one thing. | Because. | More. |",
                                               header="| ID | Requirement | Why | Extra |"), 3)
