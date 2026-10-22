"""requirements.claims, called in-process."""
import importlib


def test_claims_reads_a_cell_holding_a_backtick_code_span_with_pipes_whole_2026(tmp_path):
    requirements = importlib.import_module("veri.requirements")
    claim = "A cost is read from a report's `| total |` row, never by summing phase rows."
    path = tmp_path / "REQUIREMENTS.md"
    path.write_text("## operator/PRINCIPLES.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                    f"| P7 | {claim} | because |\n")
    assert requirements.claims(str(path), "operator/PRINCIPLES.md") == f"P7\t{claim}\n"


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
