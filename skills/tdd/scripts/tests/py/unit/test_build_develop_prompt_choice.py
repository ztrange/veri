"""build_develop_prompt.fragments answers the ordered prompt fragments of a phase, reading no file."""
import importlib

import pytest


@pytest.fixture
def bdp():
    return importlib.import_module("veri.build_develop_prompt")


def test_a_revise_of_diff_uses_the_revise_diff_template_and_any_other_phase_its_own(bdp):
    assert (bdp.fragments("revise", "diff", "s", False).template, bdp.fragments("red", "", "s", False).template) == (
        "develop-revise-diff.md", "develop-red.md")


def test_a_bug_section_brings_the_bug_reproduction_fragment_and_its_absence_none(bdp):
    assert (bdp.fragments("red", "", "s", True).bug, bdp.fragments("red", "", "s", False).bug) == (
        "_develop-red-bug.md", None)


def test_a_green_suite_repair_marks_its_paragraph_and_swaps_the_freeze_rule_for_the_repair_edit_rule(bdp):
    chosen = bdp.fragments("green", "", "s ⟦suite-repair⟧", False)

    assert (chosen.marked, chosen.freeze, chosen.repair) == (
        {"SUITE_REPAIR": "_develop-green-suite-repair.md"}, ["_develop-repair-test-edit.md"], True)


def test_a_revise_of_a_green_repair_has_no_freeze_rule_and_a_guard_subject_adds_its_grant_after_the_freeze_rule(bdp):
    revise = bdp.fragments("revise", "green", "s ⟦suite-repair⟧", False)
    guarded = bdp.fragments("green", "", "s ⟦guard-subject: x⟧", False)

    assert (revise.freeze, guarded.freeze) == (
        [], ["_develop-green-freeze-rule.md", "_develop-guard-subject-grant.md"])


def test_a_revise_of_contract_a_freezes_production_and_splices_the_test_move_fragment(bdp):
    chosen = bdp.fragments("revise", "contract-a", "s", False)

    assert (chosen.marked, chosen.inline["TEST_REWRITE"]) == (
        {"FREEZE_RULE": "_develop-revise-freeze-production.md"}, "_develop-test-move-contract-a.md")


def test_a_replaces_case_red_takes_the_replaces_case_lead_and_a_revise_of_red_alone_keeps_the_cases(bdp):
    red = bdp.fragments("red", "", "s ⟦replaces-case⟧", False)
    revised = bdp.fragments("revise", "red", "s ⟦replaces-case⟧", False)
    plain_revise = bdp.fragments("revise", "red", "s", False)

    assert ([red.inline["RED_LEAD"], red.inline["RED_CASES"], revised.replaces_red], "RED_CASES" in plain_revise.inline) == (
        ["_develop-red-lead-replaces-case.md", "_develop-red-cases-replaces-case.md", True], False)
