"""Cases for which suites still read SKILL.md's `#### The step's cost check` subsection by its content."""
import pathlib
import re

import pytest

TESTS_PY = pathlib.Path(__file__).resolve().parent.parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
HEADING = "#### The step's cost check"

MARKERS = (
    "The step's cost check", "cost check", "develop-over-budget", "step-over-budget",
    "over-budget-answer", "at=over-budget",
)

ALLOWED = {
    "test_skill_leaf_env.py": "runs the subsection's launch lines against a stub claude",
    "test_skill_event_marks.py::test_the_exit_3_case_still_names_a_mark_planted_in_the_exit_3_branch_by_its_line":
        "plants a mark in a copy of the subsection and checks the guard names it",
    "unit/test_skill_green_split.py::test_1281_skill_md_s_three_split_add_ledger_step_calls_pass_no_criterion_and_say_a_split_keeps_its_anchor_s_criterion_the_uncovered_spec_call_passes_criterion_k_read_from_the_issue_s_numbered_acceptance_criteria_one_call_per_criterion_bailing_on_exit_2":
        "reads the subsection's own instead-of add-ledger-step call, the one statement of the split, since REVISE.md no longer holds one",
    "unit/test_skill_green_split.py::test_1379_skill_md_s_every_add_ledger_step_sh_call_site_says_its_exit_2_bails_with_cause_step_add_refused":
        "carves the subsection out by its heading to read the other add-ledger-step call sites",
}


def _flat(text):
    return " ".join(text.split())


def _subsection_and_rest():
    text = SKILL_MD.read_text(encoding="utf-8")
    start = text.index(HEADING)
    following = re.search(r"^#{1,4} ", text[start + len(HEADING):], re.M)
    stop = start + len(HEADING) + following.start() if following else len(text)
    return _flat(text[start:stop]), _flat(text[:start] + "\n" + text[stop:])


def _only_in_subsection(literal, subsection, rest):
    """A phrase a case could only have copied from the cost-check subsection: three or more words no
    other part of SKILL.md carries (#2084's review: a fixed marker list missed `at most once per step`).
    A single word such as `instead-of` is script vocabulary, and a two-word label such as `neither
    answer` reads as a case's own message, so neither counts."""
    flat = _flat(literal)
    return len(flat.split(" ")) >= 3 and flat in subsection and flat not in rest


def _readers(entry, subsection, rest):
    text = entry.text
    if "SKILL" not in text:
        return []
    definitions = entry.walk.definitions
    segments = {d.name: d.segment for d in definitions}
    literals = {d.name: d.literals for d in definitions}
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
            _only_in_subsection(s, subsection, rest) for n in names for s in literals[n])

    return sorted(
        name for name in segments
        if name.startswith("test_")
        and reads_the_subsection(reach(name))
        and re.search(r"\bSKILL\b|skill_lines|skill_sections", "\n".join(segments[n] for n in reach(name)))
    )


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_cost_check_subsection_by_its_content_is_on_the_mechanical_allow_list(tests_py_index):
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
    assert stray == [], "cases read the cost-check subsection by content and are neither mechanical nor allow-listed:\n" + "\n".join(stray)
