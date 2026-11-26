"""A reworded step keeps its metrics (PRD 035.4c, issue B, MS3 to MS5): the fold follows `step-reworded` lines, chained,
so a step's figures and its REJECT pairing stay one step's."""
import importlib
import json

import pytest
from test_metrics import write_log


@pytest.fixture
def metrics():
    return importlib.import_module("veri.metrics")


@pytest.fixture(autouse=True)
def no_records_on_origin(monkeypatch):
    monkeypatch.setattr(importlib.import_module("veri.run_records"), "read", lambda issue, name, cwd: None)


def mark(ts, event, phase="", step="", **fields):
    return {"ts": ts, "awake": ts, "issue": "108", "actor": "conductor", "phase": phase, "step": step, "event": event,
            "attempt": "", **fields}


def leaf(ts, step, dollars, attempt):
    return [mark(ts, "launch", "green", step, actor="developer", attempt=attempt, name="develop-green", cmd="c", model=""),
            mark(ts + 10, "exit", "green", step, actor="developer", attempt=attempt, status="0", secs="10"),
            mark(ts + 11, "usage", "green", step, actor="developer", attempt=attempt, total_cost_usd=dollars,
                 num_turns="1")]


def verdict(ts, step, word, tree):
    return mark(ts, "verdict", "green", step, actor="verifier", verdict=word, reason="", tree=tree)


def shaped(tmp_path, monkeypatch, capsys, metrics, lines):
    write_log(tmp_path, lines)
    monkeypatch.chdir(tmp_path)
    code = metrics.main(["108", "--json"])
    out, err = capsys.readouterr()
    assert code == 0, err
    return json.loads(out)


def test_4227_a_step_reworded_a_to_b_then_b_to_c_is_one_entry_with_text_c_former_a_b_and_all_its_figures(
        tmp_path, monkeypatch, capsys, metrics):
    steps = shaped(tmp_path, monkeypatch, capsys, metrics, [
        mark(90, "step-start", step="a"), *leaf(100, "a", "0.50", "1"), verdict(120, "a", "REJECT", "t1"),
        mark(130, "step-reworded", **{"from": "a", "to": "b"}),
        *leaf(200, "b", "0.25", "2"),
        mark(230, "step-reworded", **{"from": "b", "to": "c"}),
        *leaf(300, "c", "1.00", "3"), verdict(320, "c", "PASS", "t2"), mark(330, "step-done", step="c"),
        *leaf(400, "other", "2.00", "1")])["steps"]

    assert [(entry["text"], entry["former"]) for entry in steps] == [("c", ["a", "b"]), ("other", [])]
    (one, _other) = steps
    assert (one["attempts"], one["cost_usd"], one["wall_seconds"], one["reject"], one["pass"]) == (3, 1.75, 240, 1, 1)
    assert one["rejects"]["caught"] == 1


def test_4227_a_journal_with_no_step_reworded_line_folds_as_before_with_every_former_empty(
        tmp_path, monkeypatch, capsys, metrics):
    steps = shaped(tmp_path, monkeypatch, capsys, metrics, [
        *leaf(100, "a", "0.50", "1"), verdict(120, "a", "REJECT", "t1"),
        *leaf(200, "b", "0.25", "1"), verdict(220, "b", "PASS", "t2")])["steps"]

    assert [(entry["text"], entry["former"], entry["attempts"], entry["rejects"]["pending"]) for entry in steps] == [
        ("a", [], 1, 1), ("b", [], 1, 0)]


def test_4227_two_steps_reworded_to_one_text_keep_both_former_chains_and_both_figures(
        tmp_path, monkeypatch, capsys, metrics):
    steps = shaped(tmp_path, monkeypatch, capsys, metrics, [
        *leaf(100, "a", "0.50", "1"), *leaf(200, "x", "0.25", "1"),
        mark(300, "step-reworded", **{"from": "a", "to": "b"}), mark(310, "step-reworded", **{"from": "x", "to": "b"}),
        *leaf(400, "b", "1.00", "2")])["steps"]

    assert [(entry["text"], entry["former"], entry["attempts"], entry["cost_usd"]) for entry in steps] == [
        ("b", ["a", "x"], 3, 1.75)]
