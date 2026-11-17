"""`metrics.sh <n> --json`: the run's metrics as one JSON object, built from the same Fold as the markdown report
(PRD 035.1, MJ1 to MJ10)."""
import dataclasses
import importlib
import json

import pytest

from test_metrics import table
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


@pytest.mark.parametrize("priced, some_priced, expected", [(True, True, True), (False, True, "partial"),
                                                            (False, False, False)])
def test_conductor_priced_is_true_when_every_session_carries_a_price_false_when_none_does_and_partial_otherwise(
        folded, metrics, priced, some_priced, expected):
    shaped = metrics.as_json(dataclasses.replace(folded, conductor_priced=priced, conductor_some_priced=some_priced))

    assert shaped["conductor"]["priced"] == expected
