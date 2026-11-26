"""The launch-cost section of veri/metrics.py's report (PRD 024.3): what leaves wrote to and read from the cache
on their first turn, per role and model, in tokens."""
import importlib

import pytest
from test_metrics import render, table, write_log


@pytest.fixture
def metrics():
    return importlib.import_module("veri.metrics")


def usage(actor, model, first_turn=None):
    event = {"event": "usage", "actor": actor, "phase": "green", "step": "1", "attempt": "1", "model": model,
             "num_turns": "3", "total_cost_usd": "0.5"}
    if first_turn is not None:
        creation, read, fresh = first_turn
        event.update(first_turn_cache_creation_input_tokens=str(creation),
                     first_turn_cache_read_input_tokens=str(read), first_turn_input_tokens=str(fresh))
    return event


def test_the_launch_cost_table_has_a_row_per_role_and_model_with_its_leaves_and_first_turn_token_sums_conductor_excluded(
        tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [usage("developer", "claude-sonnet-5-5", (100, 10, 1)),
                         usage("verifier", "claude-sonnet-5-5", (50, 5, 1)),
                         usage("developer", "claude-sonnet-5-5", (200, 20, 2)),
                         usage("developer", "claude-opus-5-5", (7, 0, 1)),
                         usage("conductor", "claude-opus-5-5", (9000, 900, 90))])
    monkeypatch.chdir(tmp_path)

    rows = table(render(metrics, capsys), "#### Launch cost, by role")

    assert rows == [
        {"role": "developer", "model": "claude-sonnet-5-5", "leaves": "2", "first-turn cache creation": "300",
         "first-turn cache read": "30", "first-turn input": "3"},
        {"role": "verifier", "model": "claude-sonnet-5-5", "leaves": "1", "first-turn cache creation": "50",
         "first-turn cache read": "5", "first-turn input": "1"},
        {"role": "developer", "model": "claude-opus-5-5", "leaves": "1", "first-turn cache creation": "7",
         "first-turn cache read": "0", "first-turn input": "1"}]


def test_a_line_under_the_table_counts_the_leaf_usage_events_lacking_first_turn_fields_and_is_absent_when_none_lacks_them(
        tmp_path, monkeypatch, capsys, metrics):
    def report(name, events):
        root = tmp_path / name
        root.mkdir()
        write_log(root, events)
        monkeypatch.chdir(root)
        return render(metrics, capsys).split("\n")

    partial = report("partial", [usage("developer", "m-1", (1, 1, 1)), usage("developer", "m-1"),
                                 usage("verifier", "m-1"), usage("conductor", "m-1")])
    whole = report("whole", [usage("developer", "m-1", (1, 1, 1)), usage("conductor", "m-1")])

    line = "Leaf usage events without first-turn figures, not in the table: 2"
    assert (partial[-4:-1], line in whole) == (["| developer | m-1 | 1 | 1 | 1 | 1 |", "", line], False)


def test_with_no_usage_event_carrying_first_turn_fields_the_report_has_no_launch_cost_section(
        tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [usage("developer", "m-1"), usage("conductor", "m-1", (1, 1, 1))])
    monkeypatch.chdir(tmp_path)

    out = render(metrics, capsys)

    assert ("Launch cost" in out, "first-turn" in out) == (False, False)
