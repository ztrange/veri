"""The folded value of veri/metrics.py: what the report says, as plain data, read without rendering a page."""
import importlib

import pytest

from test_metrics_page import build_rich_root


@pytest.fixture
def metrics():
    return importlib.import_module("veri.metrics")


@pytest.fixture
def folded(tmp_path, monkeypatch, metrics):
    transcripts = build_rich_root(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_SESSION_TRANSCRIPTS", str(transcripts))
    monkeypatch.setenv("VERI_MODEL", "opus")
    monkeypatch.setenv("VERI_MODEL_DEVELOPER", "sonnet")
    monkeypatch.setenv("VERI_LABEL", "lane-x")
    return metrics.fold("108", ".tdd/events.jsonl", ".tdd/issue-108.md")


def test_the_phase_table_is_one_row_of_counts_seconds_and_costs_per_phase(folded):
    red = folded.phases["red"]

    assert list(folded.phases) == ["red", "green", "refactor", "pin", "cover"]
    assert (red["attempts"], red["PASS"], red["REJECT"], red["kills"]) == (7, 1, 2, 1)
    assert (red["wall s"], red["API s"], red["turns"]) == (295, 206, 21)
    assert red["$"] == pytest.approx(1.55)


def test_the_rework_and_waste_of_a_phase_are_the_attempts_a_rejection_or_an_unfinished_step_lost(folded):
    red = folded.lost["red"]

    assert (red["rework wall s"], red["rework $"]) == (110, pytest.approx(0.50))
    assert (red["waste wall s"], red["waste $"]) == (45, pytest.approx(0.30))


def test_the_step_table_counts_retries_and_missing_verdicts_the_phase_table_does_not(folded):
    one = folded.steps["one"]

    assert (one["attempts"], one["retries"], one["no-verdict"]) == (11, 2, 1)
    assert list(folded.steps) == ["one", "two", "three", "five"]


def test_the_model_table_is_keyed_by_role_and_the_model_that_answered(folded):
    assert list(folded.by_model) == [("developer", "claude-sonnet-4"), ("verifier", "claude-sonnet-4"),
                                     ("developer", "claude-opus-5-5")]
    assert folded.by_model[("developer", "claude-opus-5-5")]["kills"] == 1


def test_test_command_seconds_are_kept_per_tier_in_run_order(folded):
    assert folded.tier_runs == {"fast": ["12", "13"], "full": ["140"], "unknown": ["7"]}


def test_adjudications_are_counted_per_outcome_and_switched_off_verifiers_apart(folded):
    assert folded.adjudications == {"retry": 1, "bail": 1}
    assert folded.switched_off == 1


def test_a_refactor_pass_carries_its_mark_its_verdict_its_revises_and_what_it_spent(folded):
    first, second = folded.passes

    assert (first["step"], first["pass"], first["verdict"], first["revise"], first["wall"]) == ("one", "1", "PASS", 1, 160)
    assert first["dollars"] == pytest.approx(1.39)
    assert (first["mark"]["transforms"], first["mark"]["budget"], first["mark"]["stopped"]) == ("2", "5", "candidates-done")
    assert (second["pass"], second["verdict"], second["revise"]) == ("2", "", 0)


def test_the_header_facts_are_numbers_and_text_not_sentences(folded):
    assert (folded.issue_wall, folded.asleep) == (4100, 0)
    assert (folded.steps_done, folded.planned) == (4, 4)
    assert folded.lane == "lane-x"
    assert folded.flaked == ["a_test.py", "b_test.py"]
    assert folded.pinned == "refactor,green"


def test_the_outcome_is_the_run_ends_answer_and_its_ending_mark(folded):
    assert folded.ended is True
    assert folded.cause == "done"
    assert folded.ending["event"] == "done"
    assert folded.ending["pr"] == "https://github.com/ztrange/veri/pull/999"


def test_the_requested_model_knobs_are_read_off_the_environment_in_report_order(folded):
    assert list(folded.model_knobs) == ["VERI_MODEL", "VERI_MODEL_DEVELOPER", "VERI_MODEL_VERIFIER", "VERI_MODEL_REVISE"]
    assert (folded.model_knobs["VERI_MODEL"], folded.model_knobs["VERI_MODEL_DEVELOPER"]) == ("opus", "sonnet")
    assert not folded.model_knobs["VERI_MODEL_VERIFIER"]
