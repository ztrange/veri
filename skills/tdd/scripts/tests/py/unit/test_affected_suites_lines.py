"""Cases for how veri/affected_suites.py reads the lines of a changed markdown file."""
import importlib

TEXT = "## One\n```\n## Fake\n```\nchanged\n"


def section_of(text, n):
    affected = importlib.import_module("veri.affected_suites")
    return tuple(line.rstrip("\r") for line in affected.enclosing(text.split("\n")[:n]))


def test_a_crlf_file_maps_a_changed_line_after_a_fence_holding_a_heading_to_the_same_section_as_the_lf_file_2181():
    assert section_of(TEXT.replace("\n", "\r\n"), 5) == section_of(TEXT, 5) == ("## One",)


def test_a_line_holding_a_form_feed_before_a_fence_holding_a_heading_maps_a_changed_line_to_the_same_section_as_the_file_without_it_2181():
    text = "## One\nbeforeafter\n```\n## Fake\n```\n## Two\nchanged\n"
    assert section_of(text.replace("before", "before\x0c"), 7) == section_of(text, 7) == ("## Two",)


def test_unfenced_yields_one_flag_decision_per_line_whatever_separator_characters_a_line_holds_2181():
    affected = importlib.import_module("veri.affected_suites")
    separators = ["\r", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85", " ", " "]
    before = ["a" + sep + "b" for sep in separators] + [sep for sep in separators]
    lines = before + ["```", "## Fake", "```", "## Real"]
    assert list(affected.unfenced(lines)) == before + ["## Real"]
