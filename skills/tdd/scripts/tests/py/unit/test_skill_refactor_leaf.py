"""Cases for the shape of the refactor phase skills/tdd/SKILL.md prescribes, read as text."""
import pathlib
import re

from skill_sections import plain_bytes as plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

AMENDMENT = r"amend|ledger (step|line)|add-ledger-step|grow"


def either_order(first, second, between):
    return f"(({first}){between}({second})|({second}){between}({first}))"


def whole_document():
    return plain(SKILL.read_bytes()).replace(b"\n", b" ")


def test_skill_md_grows_the_plan_from_the_refactor_leaf_s_flags_classes_alone_reading_no_new_step_or_candidates_line_of_the_leaf_s_into_it():
    whole = whole_document()
    leaf_new_step = re.search(either_order("leaf's", "new_step", "[^.]{0,30}").encode(), whole)
    assert leaf_new_step is None, f"still reads a NEW_STEP: line from the refactor leaf: {leaf_new_step and leaf_new_step.group()!r}"
    candidate_growth = re.search(either_order("candidates:", f"({AMENDMENT})", "[^.]{0,80}").encode(), whole)
    assert candidate_growth is None, f"grows the plan from the leaf's CANDIDATES: lines: {candidate_growth and candidate_growth.group()!r}"
