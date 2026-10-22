"""Cases for the one markdown section reader under veri/."""
import importlib


def test_fenced_lines_marks_the_opening_body_and_closing_line_of_backtick_and_tilde_fences_only():
    markdown_sections = importlib.import_module("veri.markdown_sections")
    text = (
        "before\n"
        "```\n"
        "## in backticks\n"
        "```\n"
        "between\n"
        "~~~\n"
        "## in tildes\n"
        "~~~\n"
        "after\n"
    )

    assert markdown_sections.fenced_lines(text) == [
        False, True, True, True, False, True, True, True, False,
    ]
