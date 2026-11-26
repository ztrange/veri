"""What each verifier REJECT led to (PRD 035.3a, issue B, MO2 to MO9): the fold pairs a REJECT with the first later PASS
of its step and phase and counts one of six outcomes per phase and per step."""
import importlib
import json

import pytest
from test_metrics import table, write_log


@pytest.fixture
def metrics():
    return importlib.import_module("veri.metrics")


@pytest.fixture(autouse=True)
def no_records_on_origin(monkeypatch):
    monkeypatch.setattr(importlib.import_module("veri.run_records"), "read", lambda issue, name, cwd: None)


OUTCOMES = ("caught", "flipped", "overturned", "unresolved", "pending", "untracked")


def mark(ts, event, phase="", step="", **fields):
    return {"ts": ts, "awake": ts, "issue": "108", "actor": "conductor", "phase": phase, "step": step, "event": event,
            "attempt": "", **fields}


def verdict(ts, word, tree=None, step="one", phase="green"):
    fields = {} if tree is None else {"tree": tree}
    return mark(ts, "verdict", phase, step, actor="verifier", verdict=word, reason="", **fields)


def bail(ts, cause, step="one"):
    return mark(ts, "bail", "green", step, cause=cause, classification="process")


def folded(tmp_path, monkeypatch, capsys, metrics, lines):
    write_log(tmp_path, lines)
    monkeypatch.chdir(tmp_path)
    code = metrics.main(["108", "--json"])
    out, err = capsys.readouterr()
    assert code == 0, err
    return json.loads(out)


def counts(**named):
    return dict(dict.fromkeys(OUTCOMES, 0), **named)


@pytest.mark.parametrize("lines, outcome", [
    ([verdict(100, "REJECT", "t1"), mark(110, "revise", "green", "one", budget="3"), verdict(120, "PASS", "t2")],
     "caught"),
    ([verdict(100, "REJECT", "t1"), verdict(120, "PASS", "t1")], "flipped"),
    ([verdict(100, "REJECT", "t1"), bail(110, "revise-impossible")], "overturned"),
    ([verdict(100, "REJECT", "t1"), bail(110, "revise-exhausted")], "unresolved"),
    ([verdict(100, "REJECT", "t1")], "pending"),
    ([verdict(100, "REJECT", "t1"), verdict(120, "PASS")], "untracked"),
    ([verdict(100, "REJECT"), verdict(120, "PASS", "t2")], "untracked"),
], ids=["caught", "flipped", "overturned", "unresolved", "pending", "untracked pass", "untracked reject"])
def test_4222_each_reject_gets_the_one_outcome_its_later_lines_decide(tmp_path, monkeypatch, capsys, metrics, lines, outcome):
    shaped = folded(tmp_path, monkeypatch, capsys, metrics, lines)

    assert shaped["phases"]["green"]["rejects"] == counts(**{outcome: 1})


def test_4222_a_reject_pairs_with_the_first_later_pass_of_its_own_step_and_phase_across_a_bail_and_a_resume(
        tmp_path, monkeypatch, capsys, metrics):
    shaped = folded(tmp_path, monkeypatch, capsys, metrics, [
        verdict(100, "REJECT", "t1"),
        verdict(105, "PASS", "t9", step="two"),
        verdict(106, "PASS", "t9", phase="red"),
        verdict(107, "malformed", "t9"),
        bail(110, "revise-exhausted"), mark(120, "resume"), mark(121, "conductor-start", pid="2", started="b"),
        verdict(130, "PASS", "t1"),
        verdict(140, "PASS", "t3")])

    assert shaped["phases"]["green"]["rejects"] == counts(flipped=1)


def test_4222_a_revise_impossible_bail_of_the_step_before_the_pass_overturns_and_one_of_another_step_does_not(
        tmp_path, monkeypatch, capsys, metrics):
    shaped = folded(tmp_path, monkeypatch, capsys, metrics, [
        verdict(100, "REJECT", "t1"), bail(110, "revise-impossible"), mark(120, "resume"), verdict(130, "PASS", "t2"),
        verdict(200, "REJECT", "t1", step="two"), bail(210, "revise-impossible"), mark(220, "resume")])

    assert shaped["phases"]["green"]["rejects"] == counts(overturned=1, unresolved=1)


def test_4222_a_journal_written_before_verdicts_carried_a_tree_folds_paired_rejects_untracked_and_the_rest_by_the_bails(
        tmp_path, monkeypatch, capsys, metrics):
    shaped = folded(tmp_path, monkeypatch, capsys, metrics, [
        verdict(100, "REJECT"), verdict(110, "PASS"),
        verdict(200, "REJECT", step="two"), bail(210, "revise-impossible", step="two"), mark(220, "resume"),
        verdict(300, "REJECT", step="three"), bail(310, "revise-exhausted", step="three"), mark(320, "resume"),
        verdict(400, "REJECT", step="four")])

    assert shaped["phases"]["green"]["rejects"] == counts(untracked=1, overturned=1, unresolved=1, pending=1)


def test_4222_every_phase_and_step_entry_holds_six_numbers_summing_to_its_reject_all_0_without_a_reject(
        tmp_path, monkeypatch, capsys, metrics):
    shaped = folded(tmp_path, monkeypatch, capsys, metrics, [
        mark(90, "launch", "red", "one", actor="developer", attempt="1", name="develop-red", cmd="c", model=""),
        verdict(100, "REJECT", "t1"), verdict(110, "REJECT", "t2"), verdict(120, "PASS", "t3"),
        verdict(130, "REJECT", "t3", phase="refactor"), verdict(140, "PASS", "t3", phase="refactor"),
        verdict(200, "REJECT", "t1", step="two")])

    phases, steps = shaped["phases"], {entry["text"]: entry for entry in shaped["steps"]}
    assert {phase: entry["rejects"] for phase, entry in phases.items()} == {
        "red": counts(), "green": counts(caught=2, pending=1), "refactor": counts(flipped=1)}
    assert {text: entry["rejects"] for text, entry in steps.items()} == {
        "one": counts(caught=2, flipped=1), "two": counts(pending=1)}
    assert [sum(entry["rejects"].values()) - entry["reject"] for entry in [*phases.values(), *steps.values()]] == [0] * 5


def reported(tmp_path, monkeypatch, capsys, metrics, lines):
    """The markdown report and the JSON object of one journal."""
    shaped = folded(tmp_path, monkeypatch, capsys, metrics, lines)
    code = metrics.main(["108"])
    out, err = capsys.readouterr()
    assert code == 0, err
    return out, shaped


def test_4236_the_report_prints_a_reject_outcomes_table_right_after_the_phase_table_one_row_per_phase_with_a_reject(
        tmp_path, monkeypatch, capsys, metrics):
    out, shaped = reported(tmp_path, monkeypatch, capsys, metrics, [
        mark(90, "launch", "red", "one", actor="developer", attempt="1", name="develop-red", cmd="c", model=""),
        verdict(100, "REJECT", "t1"), verdict(110, "REJECT", "t2"), verdict(120, "PASS", "t3"),
        verdict(130, "REJECT", "t3", phase="refactor"), verdict(140, "PASS", "t3", phase="refactor"),
        verdict(200, "REJECT", "t1", step="two"), bail(210, "revise-impossible", step="two")])

    headings = [line for line in out.split("\n") if line.startswith("#### ")]
    assert headings[headings.index("#### By phase") + 1] == "#### REJECT outcomes"
    rows = table(out, "#### REJECT outcomes")
    assert list(rows[0]) == ["phase", "REJECT", *OUTCOMES]
    assert {row["phase"]: {key: int(value) for key, value in row.items() if key != "phase"} for row in rows} == {
        phase: dict(REJECT=sum(entry["rejects"].values()), **entry["rejects"])
        for phase, entry in shaped["phases"].items() if any(entry["rejects"].values())}
    assert [row["phase"] for row in rows] == ["green", "refactor"]


def test_4236_a_run_with_no_reject_prints_no_reject_outcomes_table(tmp_path, monkeypatch, capsys, metrics):
    out, _shaped = reported(tmp_path, monkeypatch, capsys, metrics, [verdict(100, "PASS", "t1"), verdict(110, "malformed")])

    assert "#### By phase" in out
    assert "REJECT outcomes" not in out
