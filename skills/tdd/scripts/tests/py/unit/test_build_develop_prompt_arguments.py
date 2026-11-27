"""build_develop_prompt.arguments answers the checked arguments or a refusal, writing nothing."""
import importlib

import pytest


@pytest.fixture
def bdp():
    return importlib.import_module("veri.build_develop_prompt")


def test_no_argument_is_refused_with_no_message_so_that_only_the_usage_line_prints(bdp):
    refusal = bdp.arguments([])

    assert (refusal.message, refusal.code) == (None, 2)


def test_a_short_argument_count_is_refused_naming_the_phase_and_the_count_it_needs(bdp):
    refusal = bdp.arguments(["green", "spec", "step", "cmd"])

    assert (refusal.message, refusal.code) == ("build-develop-prompt: green needs 7 arguments, got 4", 2)


def test_the_first_empty_required_argument_is_refused_by_its_name(bdp):
    refusal = bdp.arguments(["revise", "diff", "spec", "step", "cmd", "reason.md"])

    assert refusal.message == "build-develop-prompt: missing <fast-cmd>"


def test_a_non_decimal_budget_is_refused_after_the_spent_that_passed(bdp):
    refusal = bdp.arguments(["over-budget", "spec", "step", "cmd", "3", "1.5.2"])

    assert refusal.message == "build-develop-prompt: <budget> '1.5.2' is not a non-negative decimal number"


def test_a_decimal_spent_and_budget_are_accepted(bdp):
    parsed = bdp.arguments(["over-budget", "spec", "step", "cmd", "3", "1.5"])

    assert parsed.args == ["spec", "step", "cmd", "3", "1.5"]


def test_a_revise_answers_the_phase_being_revised_the_names_and_the_arguments_without_it(bdp):
    parsed = bdp.arguments(["revise", "diff", "spec", "step", "cmd", "reason.md", "fast"])

    assert (parsed.phase, parsed.revised_phase, parsed.names, parsed.args) == (
        "revise", "diff", ["<issue-spec-file>", "<step-text>", "<test-cmd>", "<reason-file>", "<fast-cmd>"],
        ["spec", "step", "cmd", "reason.md", "fast"])
