"""`metrics.sh <n> --json`: the run's metrics as one JSON object, built from the same Fold as the markdown report
(PRD 035.1, MJ1 to MJ10)."""
import builtins
import dataclasses
import importlib
import io
import json
import os
import re

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

    assert sorted(printed) == ["conductor", "leaves", "phases", "run", "runs", "stages", "steps", "total"]
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
    assert [sorted(entry) for entry in phases.values()] == [sorted([*PHASE_KEYS, *FIRST_TRY_KEYS, "rejects"])] * len(rows)
    assert ({name: {key: shown(entry[key], column) for key, column in PHASE_KEYS.items()} for name, entry in phases.items()}
            == {row["phase"]: {key: row[column] for key, column in PHASE_KEYS.items()} for row in rows})


STEP_KEYS = dict(PHASE_KEYS, retries="retries", no_verdict="no-verdict")

FIRST_TRY_KEYS = ["verified_steps", "first_try_pass", "revise_cycles"]


def test_steps_hold_one_entry_per_step_in_the_by_step_order_with_its_text_and_its_start_to_done_wall(
        rich, capsys, metrics):
    steps = as_json(metrics, capsys)["steps"]
    rows = markdown_rows(metrics, "#### By step")

    assert [entry["text"] for entry in steps] == [row["step"] for row in rows] == ["one", "two", "three", "five"]
    assert [sorted(entry) for entry in steps] == [sorted(["text", "rejects", "former", *STEP_KEYS])] * len(rows)
    assert ([{key: shown(entry[key], column) for key, column in STEP_KEYS.items()} for entry in steps]
            == [{key: row[column] for key, column in STEP_KEYS.items()} for row in rows])
    assert [entry["wall_seconds"] for entry in steps] == [690, None, 30, 20]


@pytest.fixture
def folded(rich, metrics):
    return metrics.fold("108", ".tdd/events.jsonl", ".tdd/issue-108.md")


def test_conductor_holds_its_cost_turns_session_count_model_and_whether_it_is_estimated_and_priced(rich, capsys, metrics):
    conductor = as_json(metrics, capsys)["conductor"]

    assert sorted(conductor) == ["by_phase", "cost_usd", "estimated", "model", "priced", "sessions", "turns"]
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


TEXT_KEYS = {"issue", "outcome", "text", "model", "cause", "classification", "phase", "step", "ended", "former"}
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


def keys(value):
    if isinstance(value, dict):
        return set(value) | {key for inner in value.values() for key in keys(inner)}
    if isinstance(value, list):
        return {key for inner in value for key in keys(inner)}
    return set()


def test_no_key_at_any_depth_holds_a_rate_a_percentage_or_an_average(rich, capsys, metrics):
    named = keys(as_json(metrics, capsys))

    assert len(named) > 20
    assert sorted(key for key in named if re.search(r"rate|percent|pct|ratio|share|avg|average|mean|median|per_", key)) == []


USAGE = "usage: metrics.sh <issue-number> [--json]\n"


@pytest.mark.parametrize("argv", [["--json"], ["", "--json"], ["108", "extra"], ["108", "--json", "extra"],
                                  ["108", "extra", "--json"], ["108", "--JSON"]])
def test_a_missing_issue_or_any_argument_after_it_but_json_is_exit_2_with_the_usage_line_and_nothing_on_stdout(
        rich, run_cli, metrics, argv):
    assert run_cli(metrics, argv, cwd=rich) == (2, "", USAGE)


@pytest.mark.parametrize("log", ["missing", "a directory"])
def test_under_json_an_unreadable_event_log_is_exit_2_with_nothing_on_stdout(tmp_path, run_cli, metrics, log):
    (tmp_path / ".tdd").mkdir()
    if log == "a directory":
        (tmp_path / ".tdd" / "events.jsonl").mkdir()

    code, out, err = run_cli(metrics, ["108", "--json"], cwd=tmp_path)

    assert (code, out, len(err.splitlines())) == (2, "", 1), err
    assert "events.jsonl" in err


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


def verdict(ts, step, word, phase="green"):
    return mark(ts, "verdict", phase, step, verdict=word, reason="")


def test_4223_a_phase_entry_counts_its_verified_steps_those_passed_first_try_and_its_revise_cycles(
        tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [mark(100, "launch", "green", "one", name="develop-green", cmd="c", model=""),
                         verdict(110, "one", "PASS"),
                         mark(200, "launch", "green", "two", name="develop-green", cmd="c", model=""),
                         verdict(210, "two", "REJECT"), mark(220, "revise", "green", "two", budget="3"),
                         verdict(230, "two", "REJECT"), mark(240, "revise", "green", "two", budget="3"),
                         verdict(250, "two", "PASS")])
    monkeypatch.chdir(tmp_path)

    green = as_json(metrics, capsys)["phases"]["green"]

    assert (green["verified_steps"], green["first_try_pass"], green["revise_cycles"]) == (2, 1, 2)


def test_4223_a_journal_with_no_revise_event_folds_with_every_revise_cycles_0(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [mark(100, "launch", "red", "one", name="develop-red", cmd="c", model=""),
                         verdict(110, "one", "REJECT", phase="red"),
                         mark(200, "launch", "green", "one", name="develop-green", cmd="c", model=""),
                         verdict(210, "one", "PASS")])
    monkeypatch.chdir(tmp_path)

    phases = as_json(metrics, capsys)["phases"]

    assert {phase: entry["revise_cycles"] for phase, entry in phases.items()} == {"red": 0, "green": 0}


def leaf(ts, event, step, actor, attempt="1", **fields):
    return mark(ts, event, "green", step, actor=actor, attempt=attempt, **fields)


def test_4224_leaves_are_keyed_by_leaf_kind_a_named_line_under_its_name_an_unnamed_one_under_its_launch_else_unnamed(
        tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [leaf(100, "launch", "one", "developer", name="develop-green", cmd="c", model=""),
                         leaf(110, "exit", "one", "developer", status="0", secs="10"),
                         leaf(120, "launch", "one", "verifier", name="verify-green", cmd="c", model=""),
                         leaf(130, "verdict", "one", "verifier", verdict="PASS", reason="", name="verify-green"),
                         leaf(140, "usage", "one", "developer", attempt="2", name="revise-green-2", num_turns="2",
                              total_cost_usd="0.50"),
                         leaf(150, "exit", "two", "developer", status="2", secs="7")])
    monkeypatch.chdir(tmp_path)

    leaves = as_json(metrics, capsys)["leaves"]

    assert {kind: {key: entry[key] for key in ("attempts", "pass", "kills", "wall_seconds", "turns", "cost_usd")}
            for kind, entry in leaves.items()} == {
        "develop-green": {"attempts": 1, "pass": 0, "kills": 0, "wall_seconds": 10, "turns": 0, "cost_usd": 0},
        "verify-green": {"attempts": 1, "pass": 1, "kills": 0, "wall_seconds": 0, "turns": 0, "cost_usd": 0},
        "revise-green": {"attempts": 0, "pass": 0, "kills": 0, "wall_seconds": 0, "turns": 2, "cost_usd": 0.5},
        "unnamed": {"attempts": 0, "pass": 0, "kills": 1, "wall_seconds": 7, "turns": 0, "cost_usd": 0}}
    assert [sorted(entry) for entry in leaves.values()] == [sorted(PHASE_KEYS)] * 4


def test_4224_on_a_journal_mixing_named_and_unnamed_lines_leaves_and_phases_sum_to_the_same_attempts_wall_and_cost(
        tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [
        mark(100, "launch", "red", "one", actor="developer", attempt="1", name="develop-red", cmd="c", model=""),
        mark(130, "exit", "red", "one", actor="developer", attempt="1", status="0", secs="30"),
        mark(131, "usage", "red", "one", actor="developer", attempt="1", total_cost_usd="0.25", num_turns="3"),
        mark(140, "launch", "red", "one", actor="verifier", attempt="1", name="verify-red", cmd="c", model=""),
        mark(150, "exit", "red", "one", actor="verifier", attempt="1", status="0", secs="10", name="verify-red"),
        mark(151, "usage", "red", "one", actor="verifier", attempt="1", total_cost_usd="0.10", name="verify-red"),
        leaf(200, "launch", "one", "developer", attempt="2", name="revise-green-2", cmd="c", model=""),
        leaf(260, "exit", "one", "developer", attempt="2", status="0", secs="60", name="revise-green-2"),
        leaf(261, "usage", "one", "developer", attempt="2", total_cost_usd="1.50"),
        leaf(300, "exit", "two", "developer", attempt="9", status="2", secs="5"),
        leaf(301, "usage", "two", "developer", attempt="9", total_cost_usd="0.05")])
    monkeypatch.chdir(tmp_path)

    shaped = as_json(metrics, capsys)

    assert {view: {key: round(sum(entry[key] for entry in shaped[view].values()), 2)
                   for key in ("attempts", "wall_seconds", "cost_usd")} for view in ("leaves", "phases")} == {
        "leaves": {"attempts": 3, "wall_seconds": 105, "cost_usd": 1.9},
        "phases": {"attempts": 3, "wall_seconds": 105, "cost_usd": 1.9}}
    assert sorted(shaped["leaves"]) == ["develop-red", "revise-green", "unnamed", "verify-red"]


def two_runs_and_a_restart():
    """A first run that bails, then a resume whose conductor restarts (a second conductor-start, no ending line before
    it) and lands; leaves cost 0.50, 0.25 and 1.00, the conductor's own usage line 2.00."""
    return [mark(100, "conductor-start", pid="1", started="a"),
            mark(110, "launch", "red", "one", actor="developer", attempt="1", name="develop-red", cmd="c", model=""),
            mark(130, "usage", "red", "one", actor="developer", attempt="1", total_cost_usd="0.50", num_turns="2"),
            mark(200, "bail", "red", "one", cause="revise-exhausted", classification="process"),
            mark(300, "resume"),
            mark(301, "conductor-start", pid="2", started="b"),
            mark(310, "launch", "green", "one", actor="developer", attempt="1", name="develop-green", cmd="c", model=""),
            mark(320, "usage", "green", "one", actor="developer", attempt="1", total_cost_usd="0.25", num_turns="1"),
            mark(400, "conductor-start", pid="3", started="c"),
            mark(410, "launch", "refactor", "one", actor="developer", attempt="1", name="develop-refactor", cmd="c",
                 model=""),
            mark(420, "usage", "refactor", "one", actor="developer", attempt="1", total_cost_usd="1.00", num_turns="3"),
            mark(430, "usage", total_cost_usd="2.00", num_turns="9"),
            dict(mark(900, "done", pr="https://github.com/o/r/pull/1", wall_seconds="600", awake_seconds="550"),
                 awake=850)]


def test_4225_runs_split_the_journal_at_each_ending_line_and_a_restart_continues_its_run(
        tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, two_runs_and_a_restart())
    monkeypatch.chdir(tmp_path)

    runs = as_json(metrics, capsys)["runs"]

    assert runs == [
        {"index": 1, "ended": "bail", "cause": "revise-exhausted", "wall_seconds": 100, "awake_seconds": 100,
         "sessions": 1, "leaves": 1, "cost_usd": 0.5},
        {"index": 2, "ended": "done", "cause": None, "wall_seconds": 600, "awake_seconds": 550,
         "sessions": 2, "leaves": 2, "cost_usd": 1.25}]


def test_4225_the_runs_leaves_and_cost_sum_to_the_issues_leaf_totals_on_two_runs_and_a_restart(
        tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, two_runs_and_a_restart())
    monkeypatch.chdir(tmp_path)

    shaped = as_json(metrics, capsys)

    assert (sum(run["leaves"] for run in shaped["runs"]), round(sum(run["cost_usd"] for run in shaped["runs"]), 2)) == (
        sum(entry["attempts"] for entry in shaped["leaves"].values()),
        round(sum(entry["cost_usd"] for entry in shaped["leaves"].values()), 2)) == (3, 1.75)


def stage(ts, event, name, status=None, secs=None):
    fields = {} if status is None else {"status": status, "secs": secs}
    return mark(ts, event, stage=name, **fields)


def test_4228_stages_count_each_stages_starts_its_ends_by_exit_code_its_unended_starts_and_its_seconds(
        tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [stage(100, "stage-start", "preflight"), stage(101, "stage-start", "baseline"),
                         stage(131, "stage-end", "baseline", "0", "30"), stage(140, "stage-end", "preflight", "0", "40"),
                         stage(200, "stage-start", "baseline"),
                         stage(300, "stage-start", "baseline"), stage(310, "stage-end", "baseline", "1", "10"),
                         stage(400, "stage-start", "preflight"), stage(402, "stage-end", "preflight", "3", "2"),
                         stage(500, "stage-start", "preflight"), stage(505, "stage-end", "preflight", "2", "5"),
                         stage(600, "stage-start", "baseline")])
    monkeypatch.chdir(tmp_path)

    stages = as_json(metrics, capsys)["stages"]

    assert stages == {
        "preflight": {"runs": 3, "ok": 1, "failed": 0, "no_answer": 1, "nothing": 1, "unended": 0, "wall_seconds": 47},
        "baseline": {"runs": 4, "ok": 1, "failed": 1, "no_answer": 0, "nothing": 0, "unended": 2, "wall_seconds": 40}}


def test_4228_a_stage_end_whose_status_is_outside_0_to_3_counts_as_no_answer(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [stage(100, "stage-start", "preflight"), stage(104, "stage-end", "preflight", "4", "4"),
                         stage(200, "stage-start", "preflight"), stage(201, "stage-end", "preflight", "128", "1")])
    monkeypatch.chdir(tmp_path)

    assert as_json(metrics, capsys)["stages"]["preflight"] == {
        "runs": 2, "ok": 0, "failed": 0, "no_answer": 2, "nothing": 0, "unended": 0, "wall_seconds": 5}


def test_4228_a_journal_with_no_stage_event_folds_with_stages_empty_and_a_line_naming_no_stage_counts_under_none(
        tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, two_runs_and_a_restart() + [mark(950, "stage-end", status="0", secs="4")])
    monkeypatch.chdir(tmp_path)

    assert as_json(metrics, capsys)["stages"] == {}


def test_4225_a_launch_line_naming_no_phase_is_not_counted_among_a_runs_leaves(tmp_path, monkeypatch, capsys, metrics):
    first_run = two_runs_and_a_restart()[:4]
    write_log(tmp_path, first_run[:3] + [
        mark(150, "launch", actor="developer", attempt="1", name="develop-red", cmd="c", model="")] + first_run[3:])
    monkeypatch.chdir(tmp_path)

    shaped = as_json(metrics, capsys)

    assert ([run["leaves"] for run in shaped["runs"]], sum(entry["attempts"] for entry in shaped["leaves"].values())) == (
        [1], 1)


def test_4225_a_journal_with_no_done_bail_or_stop_line_folds_as_one_open_run(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [line for line in two_runs_and_a_restart() if line["event"] not in ("bail", "done")])
    monkeypatch.chdir(tmp_path)

    runs = as_json(metrics, capsys)["runs"]

    assert runs == [{"index": 1, "ended": None, "cause": None, "wall_seconds": None, "awake_seconds": None,
                     "sessions": 3, "leaves": 3, "cost_usd": 1.75}]


STAGE_CELLS = {"runs": "runs", "ok": "ok", "failed": "failed", "no answer": "no_answer", "nothing": "nothing",
               "unended": "unended", "wall s": "wall_seconds"}


def test_4237_the_report_prints_a_stages_table_one_row_per_marked_stage_its_figures_those_of_the_json(
        tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, [stage(100, "stage-start", "preflight"), stage(101, "stage-start", "baseline"),
                         stage(131, "stage-end", "baseline", "0", "30"), stage(140, "stage-end", "preflight", "0", "40"),
                         stage(200, "stage-start", "a-stage-no-list-names"),
                         stage(300, "stage-start", "baseline"), stage(310, "stage-end", "baseline", "1", "10"),
                         stage(400, "stage-start", "preflight"), stage(402, "stage-end", "preflight", "3", "2"),
                         stage(500, "stage-start", "a-stage-no-list-names"),
                         stage(505, "stage-end", "a-stage-no-list-names", "2", "5")])
    monkeypatch.chdir(tmp_path)

    stages = as_json(metrics, capsys)["stages"]
    code = metrics.main(["108"])
    out, err = capsys.readouterr()

    assert code == 0, err
    rows = table(out, "#### Stages")
    assert list(rows[0]) == ["stage", *STAGE_CELLS]
    assert [row["stage"] for row in rows] == list(stages) == ["preflight", "baseline", "a-stage-no-list-names"]
    assert {row["stage"]: {key: int(row[cell]) for cell, key in STAGE_CELLS.items()} for row in rows} == stages


def test_4237_a_run_with_no_stage_marked_prints_no_stages_table(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, two_runs_and_a_restart() + [mark(950, "stage-end", status="0", secs="4")])
    monkeypatch.chdir(tmp_path)

    code = metrics.main(["108"])
    out, err = capsys.readouterr()

    assert code == 0, err
    assert "#### By phase" in out
    assert "#### Stages" not in out
