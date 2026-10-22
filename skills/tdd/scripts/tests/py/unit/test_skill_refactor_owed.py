"""Cases for how skills/tdd/SKILL.md carries a step's structural leftovers out of its refactor loop, read as text."""
import importlib
import pathlib

from skill_sections import plain_folded as plain, window

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

DRAFT_PR = "### 4. Draft PR"


def section(heading):
    text = importlib.import_module("skill_sections").section(SKILL, heading)
    body = text.split("\n", 1)[1] if "\n" in text else ""
    return plain(body.encode())


def test_756_skill_md_s_draft_pr_structural_pass_never_lists_an_all_test_file_step_s_test_only_candidate_and_so_launches_no_predicate_or_transform_leaf_for():
    draft_pr = section(DRAFT_PR)
    assert b"one structural pass" in draft_pr, "the Draft PR step has no 'one structural pass'"
    pass_text = draft_pr.split(b"one structural pass", 1)[1]
    test_only = window(pass_text, r"test-only")
    assert test_only, "the structural pass never says a test-only candidate is not listed"
    for word in (b"never listed", b"predicate", b"transform leaf"):
        assert word in test_only, f"{word!r} is missing near test-only in the structural pass"
