"""requirements.claims and requirements.main (through run_cli), called in-process."""
import importlib
import re

import pytest


def test_claims_splits_a_cell_at_an_unescaped_pipe_inside_a_code_span_2080(tmp_path):
    requirements = importlib.import_module("veri.requirements")
    path = tmp_path / "REQUIREMENTS.md"
    path.write_text("## operator/PRINCIPLES.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                    "| A1 | Says `a | b` here. | why |\n")
    assert requirements.claims(str(path), "operator/PRINCIPLES.md") == "A1\tSays `a\n"


def test_claims_ends_a_code_span_cell_at_the_pipe_after_it_2026(tmp_path):
    requirements = importlib.import_module("veri.requirements")
    claim = "A cost is read from a report's `| total |` row."
    path = tmp_path / "REQUIREMENTS.md"
    path.write_text("## operator/PRINCIPLES.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                    "| P7 | A cost is read from a report's `\\| total \\|` row. | because of the why |\n")
    assert requirements.claims(str(path), "operator/PRINCIPLES.md") == f"P7\t{claim}\n"


def test_claims_reads_an_escaped_pipe_outside_a_code_span_as_a_literal_pipe_2026(tmp_path):
    requirements = importlib.import_module("veri.requirements")
    path = tmp_path / "REQUIREMENTS.md"
    path.write_text("## operator/PRINCIPLES.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                    "| A1 | Says a \\| b in full. | because |\n")
    assert requirements.claims(str(path), "operator/PRINCIPLES.md") == "A1\tSays a | b in full.\n"


def test_claims_reads_an_escaped_pipe_inside_a_code_span_as_a_literal_pipe_2080(tmp_path):
    requirements = importlib.import_module("veri.requirements")
    path = tmp_path / "REQUIREMENTS.md"
    path.write_text("## operator/PRINCIPLES.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                    "| P7 | A cost is read from a report's `\\| total \\|` row. | because |\n")
    assert requirements.claims(str(path), "operator/PRINCIPLES.md") == \
        "P7\tA cost is read from a report's `| total |` row.\n"


def test_claims_reads_a_double_backtick_span_with_an_escaped_pipe_whole_2080(tmp_path):
    requirements = importlib.import_module("veri.requirements")
    path = tmp_path / "REQUIREMENTS.md"
    path.write_text("## operator/PRINCIPLES.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                    "| A1 | Says ``a\\|`b`` here. | because |\n")
    assert requirements.claims(str(path), "operator/PRINCIPLES.md") == "A1\tSays ``a|`b`` here.\n"


def test_claims_reads_a_table_indented_three_spaces_but_not_four_1991(tmp_path):
    requirements = importlib.import_module("veri.requirements")
    table = "| ID | Requirement | Why |\n|---|---|---|\n| A1 | Says it. | because |\n"
    three, four = tmp_path / "three.md", tmp_path / "four.md"
    three.write_text("## u\n\n" + "".join("   " + line for line in table.splitlines(True)))
    four.write_text("## u\n\n" + "".join("    " + line for line in table.splitlines(True)))
    assert requirements.claims(str(three), "u") == "A1\tSays it.\n"
    try:
        requirements.claims(str(four), "u")
    except ValueError as e:
        assert str(e).endswith("unit has no table")
    else:
        raise AssertionError("a four-space-indented table was read as the unit's table")


def test_claims_does_not_refuse_a_four_space_example_table_after_the_real_one_as_a_second_table_1991(tmp_path):
    requirements = importlib.import_module("veri.requirements")
    path = tmp_path / "REQUIREMENTS.md"
    path.write_text("## u\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | Says it. | because |\n\n"
                    "    | ID | Requirement | Why |\n    |---|---|---|\n    | B2 | Example. | none |\n")
    assert requirements.claims(str(path), "u") == "A1\tSays it.\n"


def test_well_formed_row_id_accepts_the_reword_suffix_after_a_numbered_id_3320():
    requirements = importlib.import_module("veri.requirements")
    assert requirements.well_formed_row_id("SC85<reword>")


@pytest.mark.parametrize("row_id", ["QU6b<reword><reword>", "<next><reword>", "QU6<next><reword>", "a b<reword>", "x<reword>"])
def test_well_formed_row_id_refuses_a_reword_suffix_on_anything_but_a_held_id_4541(row_id):
    requirements = importlib.import_module("veri.requirements")
    assert not requirements.well_formed_row_id(row_id)


def test_list_path_is_the_requirements_file_beside_the_unit():
    requirements = importlib.import_module("veri.requirements")
    assert requirements.list_path("skills/tdd/SKILL.md") == "skills/tdd/REQUIREMENTS.md"
    assert requirements.list_path("PRINCIPLES.md") == "REQUIREMENTS.md"


UNIT = "skills/tdd/SKILL.md"
H = "##"


@pytest.fixture
def run(run_cli):
    """requirements.main called through run_cli as `requirements.sh <argv>` with empty stdin: (code, stdout, stderr)."""
    requirements = importlib.import_module("veri.requirements")
    return lambda *argv: run_cli(requirements, list(argv))


def table(*rows, header="| ID | Requirement | Why |"):
    divider = "|" + "|".join("-" * (len(c) + 2) for c in header.strip("|").split("|")) + "|"
    return "\n".join([f"{H} {UNIT}", "", header, divider, *rows]) + "\n"


def claims_refused_naming_line(run, tmp_path, body, line):
    path = tmp_path / "r.md"
    path.write_text(body)
    code, out, err = run("claims", str(path), UNIT)
    assert code == 2
    assert out == ""
    assert re.search(rf"(^|[^0-9]){line}([^0-9]|$)", err.replace(str(tmp_path), ""))


def test_units_prints_each_declared_prose_unit_one_per_line_in_file_order(run, tmp_path):
    path = tmp_path / "REQUIREMENTS.md"
    path.write_text(
        "# Requirements\n\n"
        + "".join(f"{H} {unit}\n\n| ID | Requirement | Why |\n|----|-------------|-----|\n| A1 | Says. | Because. |\n\n"
                 for unit in ("skills/tdd/SKILL.md", "skills/tdd/SKILL.md#Phase two", "guide/unit.md")))
    assert run("units", str(path)) == (
        0, "skills/tdd/SKILL.md\nskills/tdd/SKILL.md#Phase two\nguide/unit.md\n", "")


def test_claims_prints_a_units_rows_as_id_tab_requirement_in_table_order_with_no_why_text(run, tmp_path):
    path = tmp_path / "two-rows.md"
    path.write_text(table("| A1 | Says one thing. | Because secret-one. |",
                          "| A2 | Says two things. | Since secret-two. |"))
    assert run("claims", str(path), UNIT) == (0, "A1\tSays one thing.\nA2\tSays two things.\n", "")


def test_claims_on_a_repeated_id_exits_2_prints_nothing_on_stdout_and_names_the_duplicate_rows_line_on_stderr(run, tmp_path):
    claims_refused_naming_line(run, tmp_path, table("| A1 | Says one thing. | Because. |",
                                               "| A1 | Says it again. | Since. |"), 6)


def test_claims_on_a_row_with_an_empty_requirement_exits_2_prints_nothing_on_stdout_and_names_that_rows_line_on_stderr(run, tmp_path):
    claims_refused_naming_line(run, tmp_path, table("| A1 | Says one thing. | Because. |",
                                               "| A2 |  | Since. |"), 6)


def test_claims_on_a_row_with_an_empty_id_exits_2_prints_nothing_on_stdout_and_names_that_rows_line_on_stderr(run, tmp_path):
    claims_refused_naming_line(run, tmp_path, table("| A1 | Says one thing. | Because. |",
                                               "|  | Says another. | Since. |"), 6)


def test_claims_on_a_table_header_lacking_a_column_exits_2_prints_nothing_on_stdout_and_names_the_headers_line_on_stderr(run, tmp_path):
    claims_refused_naming_line(run, tmp_path, table("| A1 | Says one thing. |", header="| ID | Requirement |"), 3)


def test_claims_on_a_table_header_lacking_the_id_column_exits_2_prints_nothing_on_stdout_and_names_the_headers_line_on_stderr(run, tmp_path):
    claims_refused_naming_line(run, tmp_path, table("| A1 | Says one thing. | Because. |",
                                               header="| Key | Requirement | Why |"), 3)


def test_claims_on_a_file_that_does_not_exist_exits_2_prints_nothing_on_stdout_and_says_on_stderr_the_file_is_missing_naming_it(run, tmp_path):
    absent = tmp_path / "absent.md"
    code, out, err = run("claims", str(absent), UNIT)
    assert (code, out) == (2, "")
    assert "missing" in err and str(absent) in err


def test_claims_on_a_unit_the_file_does_not_declare_exits_2_prints_nothing_on_stdout_and_says_on_stderr_the_unit_is_not_declared_naming_it(run, tmp_path):
    path = tmp_path / "two-rows.md"
    path.write_text(table("| A1 | Says one thing. | Because. |"))
    code, out, err = run("claims", str(path), "skills/tdd/NOPE.md")
    assert (code, out) == (2, "")
    assert "not declared" in err and "skills/tdd/NOPE.md" in err


def test_claims_on_a_table_header_lacking_the_requirement_column_exits_2_prints_nothing_on_stdout_and_names_the_headers_line_on_stderr(run, tmp_path):
    claims_refused_naming_line(run, tmp_path, table("| A1 | Because. |", header="| ID | Why |"), 3)


def test_claims_on_a_unit_whose_table_header_is_key_value_exits_2_prints_nothing_on_stdout_and_names_the_headers_line_on_stderr(run, tmp_path):
    claims_refused_naming_line(run, tmp_path, table("| A1 | Says one thing. |", header="| Key | Value |"), 3)


def test_claims_on_a_unit_whose_table_header_is_id_requirement_why_extra_exits_2_prints_nothing_on_stdout_and_names_the_headers_line_on_stderr(run, tmp_path):
    claims_refused_naming_line(run, tmp_path, table("| A1 | Says one thing. | Because. | More. |",
                                               header="| ID | Requirement | Why | Extra |"), 3)


ROW = "| A1 | Says one thing. | Because. |"
OWN_ROW = "A1\tSays one thing.\n"


def claims_accepted_printing_only_the_rows(run, tmp_path, body):
    path = tmp_path / "r.md"
    path.write_text(body)
    assert run("claims", str(path), UNIT) == (0, OWN_ROW, "")


def test_claims_on_a_unit_with_a_later_a_b_line_after_its_table_exits_2_prints_nothing_on_stdout_and_names_that_line_on_stderr(run, tmp_path):
    claims_refused_naming_line(run, tmp_path, table(ROW) + "Afterwards:\n| A | B |\n", 7)


def test_claims_on_a_unit_with_a_second_id_requirement_why_table_after_a_blank_line_exits_2_prints_nothing_on_stdout_and_names_the_second_headers_line_on_stderr(run, tmp_path):
    claims_refused_naming_line(run, tmp_path, table(ROW) + "\n" + "\n".join(
        ["| ID | Requirement | Why |", "|----|-------------|-----|", "| B1 | Says another. | Because. |"]) + "\n", 7)


def test_claims_on_a_unit_with_a_fenced_code_block_holding_ls_grep_x_after_its_table_exits_0_and_prints_only_the_tables_rows(run, tmp_path):
    claims_accepted_printing_only_the_rows(run, tmp_path, table(ROW) + "\n```\nls | grep x\n```\n")


def test_claims_on_a_unit_with_a_fenced_code_block_holding_a_a_b_line_after_its_table_exits_0_and_prints_only_the_tables_rows(run, tmp_path):
    claims_accepted_printing_only_the_rows(run, tmp_path, table(ROW) + "\n```\n| A | B |\n```\n")


def test_claims_on_a_unit_whose_table_rows_run_straight_into_a_fence_then_a_x_y_line_after_it_exits_2_prints_nothing_on_stdout_and_names_that_line_on_stderr(run, tmp_path):
    claims_refused_naming_line(run, tmp_path, table(ROW) + "```\ncode\n```\n| X | Y |\n", 9)


@pytest.mark.parametrize("fence", ["```", "~~~"])
def test_claims_on_a_unit_with_a_fenced_code_block_holding_a_heading_line_before_its_table_exits_0_and_prints_the_tables_rows_1978(run, tmp_path, fence):
    body = table(ROW)
    head, rest = body.split("\n", 1)
    claims_accepted_printing_only_the_rows(run, tmp_path, head + "\n\n" + fence + "\n" + H + " x\n" + fence + "\n" + rest)


def test_claims_on_a_unit_with_a_prose_a_b_line_after_its_table_exits_0_and_prints_only_the_tables_rows(run, tmp_path):
    claims_accepted_printing_only_the_rows(run, tmp_path, table(ROW) + "\na | b\n")


@pytest.mark.parametrize("sep", ["\x0c", "\x85", "\u2028"])
def test_claims_on_a_unit_with_a_line_holding_a_line_break_character_before_a_fenced_heading_line_exits_0_and_prints_the_tables_rows_1978(run, tmp_path, sep):
    body = table(ROW)
    head, rest = body.split("\n", 1)
    claims_accepted_printing_only_the_rows(run, tmp_path, head + "\n\nbefore" + sep + "after\n```\n" + H + " x\n```\n" + rest.lstrip("\n"))


def test_claims_on_a_heading_whose_only_table_is_key_value_without_leading_pipes_exits_2_prints_nothing_on_stdout_and_names_the_heading_line_on_stderr(run, tmp_path):
    claims_refused_naming_line(
        run, tmp_path, f"# Requirements\n\n{H} {UNIT}\n\nKey | Value\n----|------\nA1  | Says one thing.\n", 3)


def test_claims_on_a_requirement_holding_an_escaped_pipe_prints_the_whole_requirement_with_the_pipe(run, tmp_path):
    path = tmp_path / "r.md"
    path.write_text(table("| A1 | Says a \\| b in full. | Because. |"))
    assert run("claims", str(path), UNIT) == (0, "A1\tSays a | b in full.\n", "")


def test_units_on_a_missing_file_exits_2_prints_nothing_on_stdout_and_one_stderr_line_naming_the_file_with_no_traceback(run, tmp_path):
    absent = tmp_path / "absent.md"
    code, out, err = run("units", str(absent))
    assert (code, out) == (2, "")
    assert str(absent) in err and err.count("\n") <= 1 and "Traceback" not in err


def test_units_prints_exactly_the_headings_for_which_claims_exits_0_over_a_valid_unit_and_every_malformed_shape(run, tmp_path):
    std = ["| ID | Requirement | Why |", "|----|-------------|-----|", "| A1 | Says one thing. | Because. |"]
    shapes = {
        "valid": std,
        "no-why": ["| Requirement | ID |", "|---|---|", "| Says one thing. | A1 |"],
        "why-id": ["| Why | ID |", "|---|---|", "| Because. | A1 |"],
        "key-requirement": ["| Key | Requirement |", "|---|---|", "| A1 | Says one thing. |"],
        "key-value": ["| Key | Value |", "|---|---|", "| A1 | Says one thing. |"],
        "extra-column": ["| ID | Requirement | Why | Extra |", "|---|---|---|---|", "| A1 | Says one thing. | Because. | More. |"],
        "no-leading-pipes": ["Key | Value", "----|------", "A1  | Says one thing."],
        "prose-only": ["Only prose, no table here."],
        "later-line": [*std, "", "prose between", "", "| A | B |"],
        "second-table": [*std, "", "| ID | Requirement | Why |", "|---|---|---|", "| B1 | Says another. | Since. |"],
    }
    path = tmp_path / "one-parser.md"
    path.write_text("# Requirements\n\n" + "".join(f"{H} {h}\n\n" + "\n".join(b) + "\n\n" for h, b in shapes.items()))
    accepted = [h for h in shapes if run("claims", str(path), h)[0] == 0]
    assert run("units", str(path)) == (0, "".join(f"{h}\n" for h in accepted), "")
    assert accepted == ["valid"]


def test_requirements_sh_with_no_arguments_exits_2_prints_nothing_on_stdout_and_its_usage_line_on_stderr(run):
    code, out, err = run()
    assert (code, out) == (2, "")
    assert err.startswith("usage:") and "requirements.sh" in err


@pytest.mark.parametrize("fence", ["```", "~~~"])
def test_units_lists_a_unit_once_when_a_fenced_block_holds_its_heading_line_1978(run, tmp_path, fence):
    path = tmp_path / "r.md"
    path.write_text(table(ROW) + "\n" + fence + "\n" + H + " " + UNIT + "\n" + fence + "\n")
    assert run("units", str(path)) == (0, UNIT + "\n", "")


def test_4336_a_list_read_inside_parsed_once_is_read_once_there_and_fresh_after_the_block_ends(tmp_path, monkeypatch):
    requirements = importlib.import_module("veri.requirements")
    monkeypatch.setattr(requirements, "_parsed", None)
    path = tmp_path / "REQUIREMENTS.md"

    def listing(unit):
        path.write_text("## %s\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | Says blue. | because |\n" % unit)

    listing("a.md")
    with requirements.parsed_once():
        first = requirements.headings(str(path))
        listing("b.md")
        inside = requirements.headings(str(path))
    after = requirements.headings(str(path))
    assert (first, inside, after) == (["a.md"], ["a.md"], ["b.md"])


def test_4336_two_lists_read_inside_one_parsed_once_block_each_answer_their_own_headings_and_claims(tmp_path, monkeypatch):
    requirements = importlib.import_module("veri.requirements")
    monkeypatch.setattr(requirements, "_parsed", None)
    first, second = tmp_path / "REQUIREMENTS.md", tmp_path / "docs" / "REQUIREMENTS.md"
    second.parent.mkdir()
    first.write_text("## a.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | Says blue. | because |\n")
    second.write_text("## docs/b.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| B1 | Says red. | because |\n")
    with requirements.parsed_once():
        seen = [(requirements.headings(str(p)), requirements.claims(str(p), u))
                for p, u in [(first, "a.md"), (second, "docs/b.md"), (first, "a.md")]]
    assert seen == [(["a.md"], "A1\tSays blue.\n"), (["docs/b.md"], "B1\tSays red.\n"), (["a.md"], "A1\tSays blue.\n")]


def test_malformed_row_id_accepts_a_letter_suffixed_id_amended_with_reword_4541():
    requirements = importlib.import_module("veri.requirements")
    lines = ["## Requirements", "", "### skills/tdd/SKILL.md", "",
             "| ID | Requirement | Why |", "|---|---|---|",
             "| QU6b<reword> | A reworded claim. | because of the why |"]
    assert requirements.malformed_row_id(lines) is None
