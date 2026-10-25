"""requirements.claims, called in-process."""
import importlib


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
    three.write_text("## u\n\n" + "".join("   " + l for l in table.splitlines(True)))
    four.write_text("## u\n\n" + "".join("    " + l for l in table.splitlines(True)))
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


def test_malformed_row_id_names_a_bare_next_row_and_none_for_a_well_formed_body_2373(tmp_path):
    requirements = importlib.import_module("veri.requirements")
    head = "## Requirements\n\n### skills/tdd/SKILL.md\n\n| | ID | Requirement | Why |\n|---|---|---|---|\n"
    good, bad = tmp_path / "good.md", tmp_path / "bad.md"
    good.write_text(head + "| | R1 | Says it. | because |\n| | R<next> | Says more. | because |\n")
    bad.write_text(head + "| | R1 | Says it. | because |\n| | <next> | Says more. | because |\n")
    assert requirements.malformed_row_id(str(good)) is None
    assert requirements.malformed_row_id(str(bad)) == "<next>"


def test_malformed_row_id_reads_every_unit_of_the_requirements_section_and_nothing_outside_it_2373(tmp_path):
    requirements = importlib.import_module("veri.requirements")
    table = "| | ID | Requirement | Why |\n|---|---|---|---|\n"
    two_units, elsewhere, absent = (tmp_path / n for n in ("two.md", "else.md", "absent.md"))
    two_units.write_text("## Requirements\n\n### a.md\n\n" + table + "| | R1 | One. | because |\n\n"
                         "### b.md\n\n" + table + "| | <next> | Two. | because |\n")
    elsewhere.write_text("## Notes\n\n" + table + "| | <next> | Two. | because |\n\n"
                         "## Requirements\n\n### a.md\n\n" + table + "| | R1 | One. | because |\n")
    absent.write_text("## Notes\n\n" + table + "| | <next> | Two. | because |\n")
    assert requirements.malformed_row_id(str(two_units)) == "<next>"
    assert requirements.malformed_row_id(str(elsewhere)) is None
    assert requirements.malformed_row_id(str(absent)) is None
