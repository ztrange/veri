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
    built = dataclasses.replace(empty, green_rejects=[("2", "1", "revise", "4", "the test is skipped"),
                                                      ("4", "3", "bail", "", "no assertion")])

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        metrics.layout(built)

    assert table(out.getvalue(), "#### Green rejects") == [
        {"step": "2", "attempt": "1", "route": "revise", "check": "4", "reason": "the test is skipped"},
        {"step": "4", "attempt": "3", "route": "bail", "check": "", "reason": "no assertion"}]


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


def test_a_rows_route_is_the_first_later_reroute_kind_revise_or_bail_of_its_step_and_none_without_one(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [verdict("1", "green", "1", "REJECT", "a"),
                         verdict("2", "green", "1", "REJECT", "b"),
                         {"event": "reroute", "step": "2", "phase": "green", "kind": "wrong-test"},
                         {"event": "revise", "step": "1", "phase": "green", "budget": "3"},
                         {"event": "reroute", "step": "1", "phase": "green", "kind": "later"},
                         verdict("1", "green", "2", "REJECT", "c"),
                         verdict("3", "green", "1", "REJECT", "d"),
                         {"event": "bail", "step": "9", "cause": "budget"},
                         verdict("3", "green", "2", "REJECT", "e")])
    monkeypatch.chdir(tmp_path)

    rows = table(render(metrics, capsys), "#### Green rejects")

    assert [(r["reason"], r["route"]) for r in rows] == [
        ("a", "revise"), ("b", "wrong-test"), ("c", "bail"), ("d", "bail"), ("e", "none")]


def test_a_reason_cell_escapes_each_pipe_with_a_backslash_and_reads_unknown_without_a_reason(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [verdict("1", "green", "1", "REJECT", "a | b|c"),
                         verdict("2", "green", "1", "REJECT")])
    monkeypatch.chdir(tmp_path)

    lines = render(metrics, capsys).split("\n")

    assert ("| 1 | 1 | none |  | a \\| b\\|c |" in lines, "| 2 | 1 | none |  | unknown |" in lines) == (True, True)


def test_below_the_table_one_line_counts_green_rejects_by_route_by_count_descending_then_route_name(tmp_path, monkeypatch, capsys, metrics):
    def reroute(step, kind):
        return {"event": "reroute", "step": step, "phase": "green", "kind": kind}
    write_log(tmp_path, [verdict("1", "green", "1", "REJECT", "a"), {"event": "revise", "step": "1", "phase": "green"},
                         verdict("1", "green", "2", "REJECT", "b"), reroute("1", "later"),
                         verdict("2", "green", "1", "REJECT", "c"), reroute("2", "wrong-test"),
                         verdict("2", "green", "2", "REJECT", "d"), reroute("2", "wrong-test"),
                         verdict("3", "green", "1", "REJECT", "e"), verdict("3", "green", "2", "REJECT", "f")])
    monkeypatch.chdir(tmp_path)

    out = render(metrics, capsys)
    lines = out.split("\n")
    below = lines[lines.index("#### Green rejects") + 2 + 2 + 6:]

    assert below[:2] == ["", "Green rejects by route: none 2, wrong-test 2, later 1, revise 1"]


def test_a_log_with_no_green_reject_prints_by_route_none_and_no_table(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [verdict("1", "green", "1", "PASS", "fine"), verdict("1", "red", "1", "REJECT", "no")])
    monkeypatch.chdir(tmp_path)

    lines = render(metrics, capsys).split("\n")

    assert ("Green rejects by route: none" in lines, "#### Green rejects" in lines) == (True, False)


def test_a_rows_check_cell_is_the_verdict_events_check_and_empty_for_an_event_without_one(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [dict(verdict("1", "green", "1", "REJECT", "a"), check="3"),
                         verdict("2", "green", "1", "REJECT", "b"),
                         dict(verdict("3", "green", "1", "REJECT", "c"), check="1")])
    monkeypatch.chdir(tmp_path)

    rows = table(render(metrics, capsys), "#### Green rejects")

    assert [(r["reason"], r.get("check")) for r in rows] == [("a", "3"), ("b", ""), ("c", "1")]


@pytest.mark.parametrize("checks, line", [
    (["3", None, "1", "3", None, "5"], "Green rejects by check: 1 1, 3 2, 5 1, unnamed 2"),
    (["2", "2"], "Green rejects by check: 2 2, unnamed 0"),
    ([None], "Green rejects by check: unnamed 1"),
])
def test_under_the_route_line_one_line_counts_green_rejects_by_check_ascending_then_unnamed(
        checks, line, tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [dict(verdict(str(at), "green", "1", "REJECT", "r"), **({"check": check} if check else {}))
                         for at, check in enumerate(checks, 1)])
    monkeypatch.chdir(tmp_path)

    lines = render(metrics, capsys).split("\n")
    by_route = next(at for at, text in enumerate(lines) if text.startswith("Green rejects by route: "))

    assert lines[by_route + 1] == line


def test_a_log_with_no_green_reject_prints_no_by_check_line(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [verdict("1", "green", "1", "PASS", "fine")])
    monkeypatch.chdir(tmp_path)

    assert [text for text in render(metrics, capsys).split("\n") if text.startswith("Green rejects by check")] == []
