"""Cases for how veri/affected_suites.py reads the lines of a changed markdown file."""
import importlib

TEXT = "## One\n```\n## Fake\n```\nchanged\n"


def section_of(text, n):
    affected = importlib.import_module("veri.affected_suites")
    return tuple(line.rstrip("\r") for line in affected.enclosing(text.split("\n")[:n]))


def test_a_crlf_file_maps_a_changed_line_after_a_fence_holding_a_heading_to_the_same_section_as_the_lf_file_2181():
    assert section_of(TEXT.replace("\n", "\r\n"), 5) == section_of(TEXT, 5) == ("## One",)
