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
