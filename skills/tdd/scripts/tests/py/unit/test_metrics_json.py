"""`metrics.sh <n> --json`: the run's metrics as one JSON object, built from the same Fold as the markdown report
(PRD 035.1, MJ1 to MJ10)."""
import builtins
import dataclasses
import importlib
import io
import json
import os

import pytest

from test_metrics import table, write_log
from test_metrics_page import build_rich_root


@pytest.fixture
def metrics():
    return importlib.import_module("veri.metrics")


@pytest.fixture(autouse=True)
def no_records_on_origin(monkeypatch):
    """origin carries no refs/veri/runs/<n>: the fallback read answers None and starts no git."""
    monkeypatch.setattr(importlib.import_module("veri.run_records"), "read", lambda issue, name, cwd: None)


@pytest.fixture
def rich(tmp_path, monkeypatch):
    transcripts = build_rich_root(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_SESSION_TRANSCRIPTS", str(transcripts))
    monkeypatch.setenv("VERI_LABEL", "lane-x")
    return tmp_path


def as_json(metrics, capsys, argv=("108", "--json")):
    code = metrics.main(list(argv))
    out, err = capsys.readouterr()
    assert code == 0, err
    return json.loads(out)


def test_json_prints_one_object_with_the_five_top_level_keys_and_the_markdown_report_is_unchanged(
        rich, monkeypatch, capsys, metrics):
    markdown = metrics.report("108", ".tdd/events.jsonl", ".tdd/issue-108.md")

    printed = as_json(metrics, capsys)
    code = metrics.main(["108"])
    again, _ = capsys.readouterr()

    assert sorted(printed) == ["conductor", "phases", "run", "steps", "total"]
    assert (code, again) == (0, markdown)


PHASE_KEYS = {"attempts": "attempts", "pass": "PASS", "reject": "REJECT", "kills": "kills", "wall_seconds": "wall s",
              "api_seconds": "API s", "turns": "turns", "input_tokens": "input", "output_tokens": "output",
              "cache_read_input_tokens": "cache read", "cache_creation_input_tokens": "cache creation", "cost_usd": "$"}


def shown(value, column):
    """A JSON figure as the markdown report prints it in <column>."""
    return "unknown" if value is None else "%.2f" % value if column == "$" else "%d" % value


def markdown_rows(metrics, heading):
    return table(metrics.report("108", ".tdd/events.jsonl", ".tdd/issue-108.md"), heading)


def test_phases_hold_one_entry_per_phase_keyed_by_name_each_equal_to_its_by_phase_row(rich, capsys, metrics):
    phases = as_json(metrics, capsys)["phases"]
    rows = markdown_rows(metrics, "#### By phase")

    assert list(phases) == [row["phase"] for row in rows] == ["red", "green", "refactor", "pin", "cover"]
    assert [sorted(entry) for entry in phases.values()] == [sorted(PHASE_KEYS)] * len(rows)
    assert ({name: {key: shown(entry[key], column) for key, column in PHASE_KEYS.items()} for name, entry in phases.items()}
            == {row["phase"]: {key: row[column] for key, column in PHASE_KEYS.items()} for row in rows})


STEP_KEYS = dict(PHASE_KEYS, retries="retries", no_verdict="no-verdict")


def test_steps_hold_one_entry_per_step_in_the_by_step_order_with_its_text_and_its_start_to_done_wall(
        rich, capsys, metrics):
    steps = as_json(metrics, capsys)["steps"]
    rows = markdown_rows(metrics, "#### By step")

    assert [entry["text"] for entry in steps] == [row["step"] for row in rows] == ["one", "two", "three", "five"]
    assert [sorted(entry) for entry in steps] == [sorted(["text", *STEP_KEYS])] * len(rows)
    assert ([{key: shown(entry[key], column) for key, column in STEP_KEYS.items()} for entry in steps]
            == [{key: row[column] for key, column in STEP_KEYS.items()} for row in rows])
    assert [entry["wall_seconds"] for entry in steps] == [690, None, 30, 20]


@pytest.fixture
def folded(rich, metrics):
    return metrics.fold("108", ".tdd/events.jsonl", ".tdd/issue-108.md")


def test_conductor_holds_its_cost_turns_session_count_model_and_whether_it_is_estimated_and_priced(rich, capsys, metrics):
    conductor = as_json(metrics, capsys)["conductor"]

    assert sorted(conductor) == ["cost_usd", "estimated", "model", "priced", "sessions", "turns"]
    assert (round(conductor["cost_usd"], 2), conductor["turns"], conductor["sessions"]) == (2.68, 6, 2)
    assert (conductor["model"], conductor["estimated"], conductor["priced"]) == ("opus", True, True)


def test_the_object_is_built_from_the_fold_alone_opening_no_file_and_reading_no_mark(folded, metrics, monkeypatch):
    expected = metrics.as_json(folded)

    def refuse(*args, **kwargs):
        raise AssertionError("as_json opened %r" % (args[:1],))

    monkeypatch.setattr(builtins, "open", refuse)
    monkeypatch.setattr(io, "open", refuse)
    monkeypatch.setattr(os, "open", refuse)

    assert metrics.as_json(dataclasses.replace(folded, marks=[])) == expected


TEXT_KEYS = {"issue", "outcome", "text", "model", "cause", "classification", "phase", "step"}
FLAG_KEYS = {"estimated", "priced", "includes_conductor"}


def figures(value, path=""):
    """(dotted path, value) for every figure of the object: each leaf under a key that is neither text nor a flag."""
    if isinstance(value, dict):
        return [found for key, inner in value.items() if key not in TEXT_KEYS | FLAG_KEYS
                for found in figures(inner, path + "." + key)]
    if isinstance(value, list):
        return [found for at, inner in enumerate(value) for found in figures(inner, "%s[%d]" % (path, at))]
    return [(path, value)]


def test_every_figure_is_a_json_number_or_null_and_an_unknown_one_is_null_never_zero(
        rich, tmp_path, monkeypatch, capsys, metrics):
    whole = as_json(metrics, capsys)
    elsewhere = tmp_path / "bare"
    elsewhere.mkdir()
    write_log(elsewhere, [mark(100, "step-start", step="one"), usage("developer", "0.50")])
    monkeypatch.chdir(elsewhere)
    bare = as_json(metrics, capsys)

    found = figures(whole) + figures(bare)
    assert [(path, value) for path, value in found
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)))] == []
    assert len(found) > 100
    assert (bare["conductor"]["cost_usd"], bare["conductor"]["turns"], bare["steps"][0]["wall_seconds"],
            bare["run"]["wall_seconds"]) == (None, None, None, None)


@pytest.mark.parametrize("priced, some_priced, expected", [(True, True, True), (False, True, "partial"),
                                                            (False, False, False)])
def test_conductor_priced_is_true_when_every_session_carries_a_price_false_when_none_does_and_partial_otherwise(
        folded, metrics, priced, some_priced, expected):
    shaped = metrics.as_json(dataclasses.replace(folded, conductor_priced=priced, conductor_some_priced=some_priced))

    assert shaped["conductor"]["priced"] == expected


TOTAL_KEYS = {key: column for key, column in PHASE_KEYS.items() if column in
              ("turns", "input", "output", "cache read", "cache creation", "$")}


def test_total_holds_the_total_rows_figures_and_says_the_conductors_spend_is_in_them(rich, capsys, metrics):
    total = as_json(metrics, capsys)["total"]
    (row,) = markdown_rows(metrics, "#### Total")

    assert sorted(total) == sorted([*TOTAL_KEYS, "includes_conductor"])
    assert ({key: shown(total[key], column) for key, column in TOTAL_KEYS.items()}
            == {key: row[column].removesuffix(" (estimate)") for key, column in TOTAL_KEYS.items()})
    assert total["includes_conductor"] is True


def usage(actor, dollars):
    return {"ts": 10, "issue": "108", "actor": actor, "phase": "red" if actor != "conductor" else "", "step": "1",
            "event": "usage", "attempt": "1", "num_turns": "2", "total_cost_usd": dollars}


@pytest.mark.parametrize("conductor_log, events, expected", [
    (False, [usage("developer", "0.50")], False),
    (False, [usage("developer", "0.50"), usage("conductor", "1.25")], True),
    (True, [usage("developer", "0.50")], True),
], ids=["no conductor spend anywhere", "the conductor's usage event", "a priced conductor stream log"])
def test_total_includes_conductor_exactly_when_the_conductors_spend_is_added_into_it(
        tmp_path, monkeypatch, capsys, metrics, conductor_log, events, expected):
    write_log(tmp_path, events)
    if conductor_log:
        (tmp_path / ".tdd" / "conductor-108.log").write_text(json.dumps(
            {"type": "result", "total_cost_usd": 1.0, "num_turns": 3}) + "\n")
    monkeypatch.chdir(tmp_path)

    assert as_json(metrics, capsys)["total"]["includes_conductor"] is expected


def mark(ts, event, phase="", step="", **fields):
    return {"ts": ts, "awake": ts, "issue": "108", "actor": "conductor", "phase": phase, "step": step, "event": event,
            "attempt": "", **fields}


def test_run_holds_the_issue_the_outcome_the_done_marks_seconds_and_every_bail_in_order(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [mark(100, "step-start", step="one"),
                         mark(200, "bail", "green", "one", cause="revise-exhausted", classification="process"),
                         mark(300, "resume"),
                         mark(400, "bail", "", "two", cause="needs-user"),
                         mark(500, "resume"),
                         mark(900, "done", pr="https://github.com/o/r/pull/1", wall_seconds="600", awake_seconds="550")])
    monkeypatch.chdir(tmp_path)

    run = as_json(metrics, capsys)["run"]

    assert run == {"issue": "108", "outcome": "landed", "wall_seconds": 600, "awake_seconds": 550,
                   "bails": [{"cause": "revise-exhausted", "classification": "process", "phase": "green", "step": "one"},
                             {"cause": "needs-user", "classification": None, "phase": "", "step": "two"}]}


@pytest.mark.parametrize("ending, outcome", [
    ([mark(400, "bail", cause="uncovered", classification="process")], "bailed"),
    ([mark(400, "stop", mode="now", at="red")], "stopped"),
    ([mark(400, "done", pr="https://github.com/o/r/pull/1")], "landed"),
], ids=["bail", "stop", "done without its seconds, as an older log wrote it"])
def test_run_wall_and_awake_seconds_are_null_until_a_done_mark_carries_them(
        tmp_path, monkeypatch, capsys, metrics, ending, outcome):
    write_log(tmp_path, [mark(100, "step-start", step="one")] + ending)
    monkeypatch.chdir(tmp_path)

    run = as_json(metrics, capsys)["run"]

    assert (run["outcome"], run["wall_seconds"], run["awake_seconds"]) == (outcome, None, None)
