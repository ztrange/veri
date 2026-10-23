"""Cases for which suites still read SKILL.md's `#### Red — one failing test (developer leaf), then verify-red (blind)` subsection by its content."""
import pathlib
import re

import pytest

TESTS_PY = pathlib.Path(__file__).resolve().parent.parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
PREFIX = "#### Red"
HEADING = "#### Red — one failing test (developer leaf), then verify-red (blind)"

MARKERS = (
    HEADING, "red-prediction.md", "red-divergence.sh", "develop-replaces-report", "unreplaced-cases.sh",
)

ALLOWED = {
    "test_skill_leaf_launch.py": "runs the leaf-launch guard over the document's launch lines, Red's among them",
    "test_skill_leaf_env.py": "runs every launch line against a stub claude and checks what the leaf saw",
    "unit/test_skill_red_untestable.py::test_window_given_a_dotted_start_pattern_starts_at_the_dotted_line_not_at_the_wildcard_match":
        "tests heading_window on a scratch file; goes with the helper, not Red's prose",
    "unit/test_skill_event_files.py::test_every_line_sending_the_run_into_the_pin_points_at_pin_md_1852":
        "names the Red heading only to exclude it",
    "unit/test_skill_event_files.py::test_every_line_sending_the_run_into_the_revise_loop_points_at_revise_md_1855":
        "names the Red heading only to exclude it",
}


def _flat(text):
    return " ".join(text.split())


def _subsection_and_rest():
    text = SKILL_MD.read_text(encoding="utf-8")
    start = text.index(HEADING)
    following = re.search(r"^#{1,4} ", text[start + len(HEADING):], re.M)
    stop = start + len(HEADING) + following.start() if following else len(text)
    return _flat(text[start:stop]), _flat(text[:start] + "\n" + text[stop:])


def _names_the_heading(literal):
    """The subsection's heading, or a prefix of it from `#### Red` on: a case slicing SKILL.md by it
    reads the subsection whatever it asserts, however short."""
    return literal.startswith(PREFIX) and HEADING.startswith(literal)


def _only_in_subsection(literal, subsection, rest):
    """A phrase a case could only have copied from the Red subsection: three or more words no
    other part of SKILL.md carries.
    One or two words read as script vocabulary or a case's own message, so neither counts."""
    flat = _flat(literal)
    return len(flat.split(" ")) >= 3 and flat in subsection and flat not in rest


def _readers(entry, subsection, rest):
    text = entry.text
    if "SKILL" not in text:
        return []
    definitions = entry.walk.definitions
    segments = {d.name: d.segment for d in definitions}
    literals = {d.name: d.strings for d in definitions}
    reads = {d.name: set(d.names) for d in definitions}
    calls = {
        name: {o for o in segments if o != name and re.search(r"\b%s\b" % re.escape(o), src)}
        for name, src in segments.items()
    }

    def reach(name):
        seen, todo = {name}, [name]
        while todo:
            for other in calls[todo.pop()] - seen:
                seen.add(other)
                todo.append(other)
        return seen

    def reads_the_subsection(names):
        source = "\n".join(segments[n] for n in names)
        return any(m in source for m in MARKERS) or any(
            _names_the_heading(s) or _only_in_subsection(s, subsection, rest) for n in names for s in literals[n])

    return sorted(
        name for name in segments
        if name.startswith("test_")
        and reads_the_subsection(reach(name))
        and any(re.fullmatch(r"SKILL(?:_MD)?|skill_lines", i) for n in reach(name) for i in reads[n])
    )


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_red_subsection_by_its_content_is_on_the_mechanical_allow_list(tests_py_index):
    subsection, rest = _subsection_and_rest()
    stray = []
    for entry in tests_py_index:
        path = entry.path
        if path == pathlib.Path(__file__).resolve():
            continue
        rel = str(path.relative_to(TESTS_PY))
        if rel in ALLOWED:
            continue
        stray += [f"{rel}::{name}" for name in _readers(entry, subsection, rest) if f"{rel}::{name}" not in ALLOWED
                  and f"{path.name}::{name}" not in ALLOWED]
    assert stray == [], "cases read the Red subsection by content and are neither mechanical nor allow-listed:\n" + "\n".join(stray)
