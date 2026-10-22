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


def test_fenced_lines_keeps_a_fence_open_past_a_line_of_the_other_fence_character():
    markdown_sections = importlib.import_module("veri.markdown_sections")
    text = (
        "~~~\n"
        "```\n"
        "## still tilde body\n"
        "~~~\n"
        "between\n"
        "```\n"
        "~~~\n"
        "## still backtick body\n"
        "```\n"
        "after\n"
    )

    assert markdown_sections.fenced_lines(text) == [
        True, True, True, True, False, True, True, True, True, False,
    ]


def test_fenced_lines_treats_a_line_indented_four_spaces_as_no_fence_line():
    markdown_sections = importlib.import_module("veri.markdown_sections")
    text = (
        "    ```\n"
        "## not in a fence\n"
        "```\n"
        "body\n"
        "    ```\n"
        "still body\n"
        "```\n"
        "after\n"
    )

    assert markdown_sections.fenced_lines(text) == [
        False, False, True, True, True, True, True, False,
    ]


def test_fenced_lines_keeps_a_fence_opened_by_a_longer_run_open_past_a_shorter_run():
    markdown_sections = importlib.import_module("veri.markdown_sections")
    text = (
        "````\n"
        "```\n"
        "## inside the long fence\n"
        "```\n"
        "````\n"
        "after\n"
    )

    assert markdown_sections.fenced_lines(text) == [
        True, True, True, True, True, False,
    ]
