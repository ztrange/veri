"""Cases for how skills/tdd/SKILL.md's Scope & plan section plans a step that changes pinned text."""
import importlib
import pathlib
import re

from skill_sections import plain_collapsed as _plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


def test_a_fixture_repair_steps_green_pass_is_ticked_without_refactor_pending_under_a_test_subject_1021():
    text = _plain(importlib.import_module("skill_sections").section(
        SKILL, "#### A `⟦diff-checked⟧` step — develop-diff, then verify-diff (blind)"))
    sentence = next((s for s in re.split(r"(?<=\.)\s", text)
                     if "⟦fixture-repair⟧" in s and "verify-green pass" in s), "")
    assert sentence, "SKILL.md never says how a ⟦fixture-repair⟧ step's verify-green PASS closes it"
    assert "without --refactor-pending" in sentence, "the PASS is never ticked without --refactor-pending"
    assert "--refactor-pending" not in sentence.replace("without --refactor-pending", ""), \
        "the sentence asks for --refactor-pending"
    assert "`test:` subject" in sentence or "test: subject" in sentence, "the PASS is never committed with a test: subject"
