"""build_develop_prompt.render fills the placeholders of the checked arguments and answers the text or a refusal."""
import importlib

import pytest


@pytest.fixture
def bdp():
    return importlib.import_module("veri.build_develop_prompt")


def rendered(bdp, argv):
    parsed = bdp.arguments(argv)
    assert isinstance(parsed, bdp.Arguments), parsed.message
    return bdp.render(parsed, bdp.fragments(parsed.phase, parsed.revised_phase, parsed.args[1], False))


@pytest.fixture
def spec(tmp_path):
    path = tmp_path / "spec.md"
    path.write_bytes(b"# spec\nthe issue body\nTest command: make test\n")
    return str(path)


def test_the_step_the_spent_and_the_budget_replace_their_placeholders(bdp, spec):
    text = rendered(bdp, ["over-budget", spec, "the step text", "make test", "7.25", "3"])

    assert (b"Spent: 7.25" in text, b"Budget: 3" in text, b"the step text" in text, b"{{" in text) == (
        True, True, True, False)


def test_the_spec_is_rendered_without_its_test_command_line(bdp, spec):
    text = rendered(bdp, ["over-budget", spec, "s", "make test", "1", "2"])

    assert (b"the issue body" in text, b"Test command:" in text) == (True, False)


def test_the_refactor_budget_is_the_tunable_and_five_when_unset(bdp, spec, monkeypatch):
    unset = rendered(bdp, ["refactor", spec, "s", "make test", "a.py"])
    monkeypatch.setenv("VERI_REFACTOR_BUDGET", "9")
    set_to_nine = rendered(bdp, ["refactor", spec, "s", "make test", "a.py"])

    assert (b"budget of 5 transforms" in unset, b"budget of 9 transforms" in set_to_nine) == (True, True)


def test_4577_a_refactor_prompt_without_a_pairs_file_reads_none_under_near_duplicates(bdp, spec):
    text = rendered(bdp, ["refactor", spec, "s", "make test", "a.py"])

    section = text.partition(b"### Near-duplicate pairs this cycle added")[2].split(b"\n###", 1)[0]
    assert section.strip() == b"none"


def test_4577_a_refactor_prompt_given_a_pairs_file_prints_each_of_its_lines_under_near_duplicates(bdp, spec, tmp_path):
    pairs = tmp_path / "pairs.txt"
    pairs.write_bytes(b"src/a.py:10-14 src/b.py:3-7\nsrc/c.py:1-5 src/d.py:20-24\n")

    text = rendered(bdp, ["refactor", spec, "s", "make test", "a.py", str(pairs)])

    section = text.partition(b"### Near-duplicate pairs this cycle added")[2].split(b"\n###", 1)[0]
    assert section.strip() == b"src/a.py:10-14 src/b.py:3-7\nsrc/c.py:1-5 src/d.py:20-24"


def test_a_missing_spec_is_refused_naming_it_with_no_usage_line(bdp, tmp_path):
    missing = str(tmp_path / "gone.md")

    refusal = rendered(bdp, ["over-budget", missing, "s", "make test", "1", "2"])

    assert (refusal.message, refusal.code, refusal.usage) == (f"build-develop-prompt: cannot read '{missing}'", 2, False)


def test_a_revise_prompt_without_the_issue_number_is_refused(bdp, spec, tmp_path):
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")

    refusal = rendered(bdp, ["revise", "red", spec, "s", "make test", str(reason)])

    assert refusal.message == "build-develop-prompt: a revise prompt needs VERI_ISSUE, the run's issue number"


def test_a_revise_prompt_with_the_issue_number_quotes_the_step_into_its_step_argument(bdp, spec, tmp_path, monkeypatch):
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")
    monkeypatch.setenv("VERI_ISSUE", "42")

    text = rendered(bdp, ["revise", "red", spec, "two words", "make test", str(reason)])

    assert (b"'two words'" in text, b"42" in text) == (True, True)
