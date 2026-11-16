"""The green REJECTs section of veri/metrics.py's report (PRD 024.1): each green REJECT, the route the
conductor took next and the verifier's reason, and the count per route."""
import contextlib
import dataclasses
import importlib
import io

import pytest

from test_metrics import render, table, write_log


@pytest.fixture
def metrics():
    return importlib.import_module("veri.metrics")


def test_layout_prints_a_green_rejects_row_for_each_row_a_hand_built_fold_carries(tmp_path, monkeypatch, metrics):
    write_log(tmp_path, [])
    monkeypatch.chdir(tmp_path)
    empty = metrics.fold("108", ".tdd/events.jsonl", ".tdd/issue-108.md")
    built = dataclasses.replace(empty, green_rejects=[("2", "1", "revise", "the test is skipped"),
                                                      ("4", "3", "bail", "no assertion")])

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        metrics.layout(built)

    assert table(out.getvalue(), "#### Green rejects") == [
        {"step": "2", "attempt": "1", "route": "revise", "reason": "the test is skipped"},
        {"step": "4", "attempt": "3", "route": "bail", "reason": "no assertion"}]


def verdict(step, phase, attempt, word, reason=None):
    event = {"event": "verdict", "step": step, "phase": phase, "attempt": attempt, "verdict": word}
    if reason is not None:
        event["reason"] = reason
    return event


def test_the_report_has_one_row_per_green_reject_in_log_order_and_none_for_other_phases_or_a_pass(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [verdict("2", "green", "1", "REJECT", "the test is skipped"),
                         verdict("1", "red", "1", "REJECT", "red reason"),
                         verdict("1", "refactor", "1", "REJECT", "refactor reason"),
                         verdict("2", "green", "2", "PASS", "fine"),
                         verdict("1", "green", "1", "REJECT", "no assertion")])
    monkeypatch.chdir(tmp_path)

    rows = table(render(metrics, capsys), "#### Green rejects")

    assert [(r["step"], r["attempt"], r["reason"]) for r in rows] == [
        ("2", "1", "the test is skipped"), ("1", "1", "no assertion")]
