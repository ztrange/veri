"""Cases for veri/issue_body.py: the one reading of an issue body's sections, criteria and blockers."""
import importlib

import pytest


@pytest.fixture
def ib():
    return importlib.import_module("veri.issue_body")


FENCE = "`" * 3
AC = "## Acceptance criteria"


def test_section_returns_the_text_between_the_heading_and_the_next_h1_or_h2(ib):
    body = "# Title\n## Problem\nx\n### Sub\ny\n## Acceptance criteria\n- [ ] a\n# Next\nz\n"

    assert (ib.section(body, "## Problem"), ib.section(body, AC)) == ("x\n### Sub\ny", "- [ ] a")


def test_section_is_none_for_a_body_without_the_heading(ib):
    assert ib.section("## Problem\nx\n", AC) is None


def test_a_heading_inside_a_fenced_code_block_is_not_a_heading(ib):
    body = f"{FENCE}\n{AC}\n- [ ] fake\n{FENCE}\n"

    assert (ib.section(body, AC), ib.criteria(body)) == (None, [])


def test_a_fenced_fake_heading_does_not_end_the_section(ib):
    body = f"{AC}\n- [ ] a\n{FENCE}\n## Notes\n{FENCE}\n- [ ] b\n"

    assert ib.criteria(body) == [(1, "- [ ] a"), (5, "- [ ] b")]


def test_a_fenced_checkbox_is_not_a_criterion(ib):
    body = f"{AC}\n- [ ] a\n{FENCE}\n- [ ] fake\n{FENCE}\n- [x] b\n"

    assert ib.criteria(body) == [(1, "- [ ] a"), (5, "- [x] b")]


def test_two_matching_headings_the_last_wins_unless_first_or_all_is_asked(ib):
    body = f"{AC}\n- [ ] a\n## Mid\n{AC}\n- [ ] b\n- [ ] c\n"

    assert (
        ib.criteria(body),
        ib.criteria(body, occurrence="first"),
        ib.criteria(body, occurrence="all"),
        ib.section(body, AC, occurrence="all"),
    ) == ([(4, "- [ ] b"), (5, "- [ ] c")], [(1, "- [ ] a")],
          [(1, "- [ ] a"), (4, "- [ ] b"), (5, "- [ ] c")], "- [ ] a\n- [ ] b\n- [ ] c")


def test_a_heading_with_a_suffix_matches_only_when_prefix_is_asked(ib):
    body = "## Acceptance criteria (amended)\n- [ ] a\n"

    assert (ib.criteria(body), ib.criteria(body, prefix=True)) == ([], [(1, "- [ ] a")])


def test_crlf_line_ends_and_trailing_whitespace_do_not_hide_a_heading(ib):
    body = "## Acceptance criteria\r\n- [ ] a\r\n## Other  \r\n- [ ] no\r\n"

    assert (ib.criteria(body), ib.section("## Other  \n", "## Other")) == ([(1, "- [ ] a\r")], "")


def test_criteria_index_is_the_line_number_so_the_kth_can_be_ticked(ib):
    body = "intro\n## Acceptance criteria\n\n- [ ] one\n  - [x] two\n* [ ] not a step\n- [ ] three\n"
    found = ib.criteria(body)

    assert [i for i, _ in found] == [3, 4, 6] and body.split("\n")[found[1][0]] == "  - [x] two"


def test_criteria_of_a_body_without_the_section_is_empty(ib):
    assert ib.criteria("- [ ] stray\n") == []


def test_blockers_read_hash_numbers_and_urls_of_the_given_repository(ib):
    body = "## Blocked by\n\n- #1\n- https://github.com/acme/widgets/issues/2\n- https://github.com/other/x/issues/3\n"

    assert (ib.blockers(body, "acme/widgets"), ib.blockers(body, "")) == ([1, 2], [1, 2, 3])


def test_blockers_tolerate_trailing_whitespace_and_crlf_on_the_heading(ib):
    assert (ib.blockers("## Blocked by  \n- #4\n", "a/b"), ib.blockers("## Blocked by\r\n- #5\r\n", "a/b")) == ([4], [5])


def test_blockers_stop_at_the_next_heading_and_ignore_a_fenced_heading(ib):
    body = f"{FENCE}\n## Blocked by\n- #9\n{FENCE}\n## Blocked by\n- #3\n## Notes\n- #7\n"

    assert ib.blockers(body, "a/b") == [3]


def test_blockers_of_none_or_of_a_body_without_the_section_is_empty(ib):
    assert (ib.blockers("## Blocked by\n\nNone.\n", "a/b"), ib.blockers("see #3\n", "a/b")) == ([], [])


def test_add_blocker_replaces_a_none_line(ib):
    assert ib.add_blocker("## Blocked by\n\nNone.\n", "7") == "## Blocked by\n\n- #7\n"


def test_add_blocker_goes_after_the_last_blocker_line_else_under_the_heading(ib):
    assert (
        ib.add_blocker("## Blocked by\n\n- #1\n- #2\n\n## Notes\n", "7"),
        ib.add_blocker("## Blocked by\n\nsee later\n", "7"),
    ) == ("## Blocked by\n\n- #1\n- #2\n- #7\n\n## Notes\n", "## Blocked by\n- #7\n\nsee later\n")


def test_add_blocker_creates_the_section_when_the_body_has_none(ib):
    assert (ib.add_blocker("", "7"), ib.add_blocker("text", "7")) == (
        "## Blocked by\n\n- #7", "text\n\n## Blocked by\n\n- #7")


def test_add_blocker_finds_a_heading_with_trailing_whitespace_instead_of_adding_a_second(ib):
    assert ib.add_blocker("## Blocked by \n\n- #1\n", "7") == "## Blocked by \n\n- #1\n- #7\n"
