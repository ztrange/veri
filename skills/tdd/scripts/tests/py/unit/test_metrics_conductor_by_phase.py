"""The conductor's spend per phase (PRD 035.6, MP1 to MP5): each timed turn of the conductor's stream log goes to the
innermost leaf or stage window holding its time, else `between`; an untimed one to `untimed`."""
import datetime
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


T = 1_700_000_000


def mark(at, event, phase="", step="", **fields):
    return {"ts": T + at, "awake": T + at, "issue": "108", "actor": "conductor", "phase": phase, "step": step,
            "event": event, "attempt": "", **fields}


def leaf(at, event, name=None, **fields):
    named = {} if name is None else {"name": name}
    return mark(at, event, "green", "one", actor="developer", attempt="1", **named, **fields)


def stage(at, event, name, **fields):
    return mark(at, event, stage=name, **fields)


def turn(number, at=None, model="claude-opus-4", output=7):
    record = {"type": "assistant", "message": {"id": "m%d" % number, "model": model, "content": [],
                                               "usage": {"input_tokens": 1000, "output_tokens": output}}}
    if at is not None:
        record["timestamp"] = datetime.datetime.fromtimestamp(T + at, datetime.timezone.utc).isoformat().replace(
            "+00:00", "Z")
    return record


def result(cost, turns, output):
    return {"type": "result", "total_cost_usd": cost, "num_turns": turns, "usage": {"output_tokens": output}}


def conductor(tmp_path, monkeypatch, capsys, metrics, lines, records):
    write_log(tmp_path, lines)
    if records is not None:
        (tmp_path / ".tdd" / "conductor-108.log").write_text("".join(json.dumps(r) + "\n" for r in records))
    monkeypatch.chdir(tmp_path)
    code = metrics.main(["108", "--json"])
    out, err = capsys.readouterr()
    assert code == 0, err
    return json.loads(out)["conductor"]


WINDOWS = [leaf(100, "launch", "develop-green", cmd="c", model=""), leaf(200, "exit", "develop-green", status="0", secs="100"),
           stage(300, "stage-start", "preflight"), stage(350, "stage-start", "baseline"),
           stage(400, "stage-end", "baseline", status="0", secs="50"), stage(500, "stage-end", "preflight", status="0", secs="200")]


def test_4235_each_turn_goes_to_the_innermost_window_holding_its_time_else_between_or_untimed_and_the_turns_sum(
        tmp_path, monkeypatch, capsys, metrics):
    shaped = conductor(tmp_path, monkeypatch, capsys, metrics, WINDOWS, [
        turn(1, 150), turn(2, 320), turn(3, 370), result(3.0, 3, 300),
        turn(4, 600, model="mystery-1"), turn(5, None, model="mystery-1"), result(None, 2, 50)])

    by_phase = shaped["by_phase"]
    assert {key: (entry["turns"], entry["output_tokens"]) for key, entry in by_phase.items()} == {
        "develop-green": (1, 100), "preflight": (1, 100), "baseline": (1, 100), "between": (1, 25), "untimed": (1, 25)}
    assert [by_phase[key]["cost_usd"] for key in ("between", "untimed")] == [None, None]
    assert round(sum(by_phase[key]["cost_usd"] for key in ("develop-green", "preflight", "baseline")), 6) == 3.0
    assert all(by_phase[key]["cost_usd"] > 0 for key in ("develop-green", "preflight", "baseline"))
    assert sum(entry["turns"] for entry in by_phase.values()) == shaped["turns"] == 5


def test_4235_a_leaf_window_pairs_an_exit_without_a_name_by_its_launch_and_an_unended_window_holds_no_turn(
        tmp_path, monkeypatch, capsys, metrics):
    shaped = conductor(tmp_path, monkeypatch, capsys, metrics, [
        leaf(100, "launch", "verify-green", cmd="c", model=""), leaf(200, "exit", status="0", secs="100"),
        leaf(300, "launch", "develop-green-2", cmd="c", model="")], [
        turn(1, 150), turn(2, 250), turn(3, 350), result(1.0, 3, 30)])

    assert {key: entry["turns"] for key, entry in shaped["by_phase"].items()} == {"verify-green": 1, "between": 2}


def test_4235_a_turn_the_result_counts_but_no_record_shows_is_untimed_so_the_turns_still_sum(
        tmp_path, monkeypatch, capsys, metrics):
    shaped = conductor(tmp_path, monkeypatch, capsys, metrics, WINDOWS, [turn(1, 150), turn(2, 600), result(2.0, 4, 40)])

    assert {key: entry["turns"] for key, entry in shaped["by_phase"].items()} == {
        "develop-green": 1, "between": 1, "untimed": 2}
    assert sum(entry["turns"] for entry in shaped["by_phase"].values()) == shaped["turns"] == 4


def test_4235_with_no_stream_log_beside_the_journal_by_phase_is_null(tmp_path, monkeypatch, capsys, metrics):
    assert conductor(tmp_path, monkeypatch, capsys, metrics, WINDOWS, None)["by_phase"] is None


INIT = {"type": "system", "subtype": "init"}


def test_4235_a_session_killed_before_its_result_then_a_resumed_one_counts_each_sessions_turns_and_the_turns_sum(
        tmp_path, monkeypatch, capsys, metrics):
    shaped = conductor(tmp_path, monkeypatch, capsys, metrics, WINDOWS, [
        INIT, turn(1, 150), turn(2, 600), INIT, turn(3, 320), turn(4, 370), turn(5, 610), result(3.0, 3, 300)])

    assert (shaped["turns"], shaped["sessions"]) == (5, 2)
    assert sum(entry["turns"] for entry in shaped["by_phase"].values()) == 5
    assert round(shaped["by_phase"]["preflight"]["cost_usd"] + shaped["by_phase"]["baseline"]["cost_usd"], 6) < 3.0


def test_4235_a_result_without_num_turns_counts_the_turns_its_session_showed(tmp_path, monkeypatch, capsys, metrics):
    closing = {key: value for key, value in result(2.0, 0, 20).items() if key != "num_turns"}
    shaped = conductor(tmp_path, monkeypatch, capsys, metrics, WINDOWS, [INIT, turn(1, 150), turn(2, 600), closing])

    assert shaped["turns"] == sum(entry["turns"] for entry in shaped["by_phase"].values()) == 2


def test_4235_a_session_showing_more_turns_than_its_result_counts_counts_the_turns_it_showed(
        tmp_path, monkeypatch, capsys, metrics):
    shaped = conductor(tmp_path, monkeypatch, capsys, metrics, WINDOWS,
                       [INIT, turn(1, 150), turn(2, 320), turn(3, 600), result(1.0, 2, 30)])

    assert shaped["turns"] == sum(entry["turns"] for entry in shaped["by_phase"].values()) == 3


def test_4235_a_sessions_output_tokens_split_over_its_turns_lose_no_remainder(tmp_path, monkeypatch, capsys, metrics):
    shaped = conductor(tmp_path, monkeypatch, capsys, metrics, WINDOWS,
                       [turn(1, 150), turn(2, 320), turn(3, 600), result(1.0, 3, 101)])

    assert {key: entry["output_tokens"] for key, entry in shaped["by_phase"].items()} == {
        "develop-green": 33, "preflight": 33, "between": 35}


def markdown(metrics, capsys):
    code = metrics.main(["108"])
    out, err = capsys.readouterr()
    assert code == 0, err
    return out


def test_4238_the_report_prints_an_estimated_conductor_by_phase_table_its_turns_and_cost_those_of_the_json(
        tmp_path, monkeypatch, capsys, metrics):
    by_phase = conductor(tmp_path, monkeypatch, capsys, metrics, WINDOWS, [
        turn(1, 150), turn(2, 320), turn(3, 370), result(3.0, 3, 300),
        turn(4, 600, model="mystery-1"), turn(5, None, model="mystery-1"), result(None, 2, 50)])["by_phase"]
    out = markdown(metrics, capsys)

    heading = next(line for line in out.split("\n") if line.startswith("#### Conductor by phase"))
    assert "estimated" in heading
    rows = table(out, heading)
    assert list(rows[0]) == ["phase", "turns", "$"]
    assert {row["phase"]: (int(row["turns"]), row["$"]) for row in rows} == {
        key: (entry["turns"], "unknown" if entry["cost_usd"] is None else "%.2f" % entry["cost_usd"])
        for key, entry in by_phase.items()}
    assert [row["$"] for row in rows if row["phase"] in ("between", "untimed")] == ["unknown", "unknown"]


def test_4238_with_by_phase_null_the_report_prints_no_conductor_by_phase_table(tmp_path, monkeypatch, capsys, metrics):
    assert conductor(tmp_path, monkeypatch, capsys, metrics, WINDOWS, None)["by_phase"] is None

    out = markdown(metrics, capsys)

    assert "#### By phase" in out
    assert "Conductor by phase" not in out
