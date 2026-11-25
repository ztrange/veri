"""In-process cases for veri/adjudicate.py, the module adjudicate.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def adjudicate():
    return importlib.import_module("veri.adjudicate")


def test_main_with_no_argument_exits_2_printing_the_usage_line_on_stderr(run_cli, adjudicate):
    code, out, err = run_cli(adjudicate, [])
    assert (code, out, err) == (
        2,
        "",
        "usage: adjudicate.sh --check-budget | left <n> | deviation-left <n> | record <n> <cause> <leaf-output>\n",
    )


def test_check_budget_exits_0_silently_when_the_budget_is_unset(run_cli, adjudicate, monkeypatch):
    monkeypatch.delenv("VERI_ADJUDICATE_BUDGET", raising=False)
    code, out, err = run_cli(adjudicate, ["--check-budget"])
    assert (code, out, err) == (0, "", "")


def test_check_budget_exits_2_naming_the_variable_for_a_budget_that_is_not_a_whole_number(
    run_cli, adjudicate, monkeypatch
):
    for bad in ("-1", "two", "1.5", "\u00b2"):
        monkeypatch.setenv("VERI_ADJUDICATE_BUDGET", bad)
        code, out, err = run_cli(adjudicate, ["--check-budget"])
        assert (code, out, "VERI_ADJUDICATE_BUDGET" in err) == (2, "", True), bad


def test_left_exits_0_when_the_adjudications_since_the_last_conductor_start_are_fewer_than_the_budget(
    run_cli, adjudicate, monkeypatch, tmp_path
):
    import json

    monkeypatch.delenv("VERI_ADJUDICATE_BUDGET", raising=False)
    adjudicated = {"issue": "7", "event": "adjudicated", "cause": "ci-timeout", "outcome": "retry"}
    events = [
        {"issue": "7", "event": "conductor-start"},
        adjudicated,
        adjudicated,
        {"issue": "7", "event": "conductor-start"},
        adjudicated,
        {**adjudicated, "issue": "8"},
    ]
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    code, out, err = run_cli(adjudicate, ["left", "7"], cwd=tmp_path)
    assert (code, out, err) == (0, "", "")


def test_record_on_a_retry_answer_writes_one_adjudicated_event_prints_retry_and_exits_0(
    run_cli, adjudicate, tmp_path
):
    import json

    (tmp_path / ".tdd").mkdir()
    leaf = tmp_path / "leaf.out"
    leaf.write_text("thinking\nADJUDICATION: retry — CI is queued behind a busy runner\n")
    code, out, err = run_cli(adjudicate, ["record", "7", "ci-timeout", str(leaf)], cwd=tmp_path)
    assert (code, out) == (0, "retry\n")
    events = [json.loads(l) for l in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    adjudicated = [e for e in events if e.get("event") == "adjudicated"]
    assert len(adjudicated) == 1
    assert {k: adjudicated[0].get(k) for k in ("issue", "cause", "outcome", "reason")} == {
        "issue": "7",
        "cause": "ci-timeout",
        "outcome": "retry",
        "reason": "CI is queued behind a busy runner",
    }


def test_left_exits_3_when_the_adjudications_since_the_last_conductor_start_reach_the_budget(
    run_cli, adjudicate, monkeypatch, tmp_path
):
    import json

    monkeypatch.delenv("VERI_ADJUDICATE_BUDGET", raising=False)
    adjudicated = {"issue": "7", "event": "adjudicated", "cause": "ci-timeout", "outcome": "retry"}
    events = [
        {"issue": "7", "event": "conductor-start"},
        adjudicated,
        adjudicated,
    ]
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    code, out, err = run_cli(adjudicate, ["left", "7"], cwd=tmp_path)
    assert (code, out, err) == (3, "", "")


def test_record_on_a_bail_answer_writes_one_adjudicated_event_prints_bail_and_exits_1(
    run_cli, adjudicate, tmp_path
):
    import json

    (tmp_path / ".tdd").mkdir()
    leaf = tmp_path / "leaf.out"
    leaf.write_text("thinking\nADJUDICATION: bail — the check has been pending for hours\n")
    code, out, err = run_cli(adjudicate, ["record", "7", "ci-timeout", str(leaf)], cwd=tmp_path)
    assert (code, out) == (1, "bail\n")
    events = [json.loads(l) for l in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    adjudicated = [e for e in events if e.get("event") == "adjudicated"]
    assert len(adjudicated) == 1
    assert {k: adjudicated[0].get(k) for k in ("issue", "cause", "outcome", "reason")} == {
        "issue": "7",
        "cause": "ci-timeout",
        "outcome": "bail",
        "reason": "the check has been pending for hours",
    }


def test_record_on_a_route_answer_writes_one_adjudicated_event_prints_the_route_and_exits_1(
    run_cli, adjudicate, monkeypatch, tmp_path
):
    import json

    monkeypatch.setattr(adjudicate.parse_adjudication, "parse", lambda path, cause=None: ("route some-token", "the route fits"))
    (tmp_path / ".tdd").mkdir()
    code, out, err = run_cli(adjudicate, ["record", "7", "ci-timeout", str(tmp_path / "leaf.out")], cwd=tmp_path)
    assert (code, out) == (1, "route some-token\n")
    events = [json.loads(l) for l in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    adjudicated = [e for e in events if e.get("event") == "adjudicated"]
    assert len(adjudicated) == 1
    assert {k: adjudicated[0].get(k) for k in ("issue", "cause", "outcome", "reason")} == {
        "issue": "7",
        "cause": "ci-timeout",
        "outcome": "route",
        "reason": "the route fits",
    }


def test_record_on_a_leaf_output_with_no_adjudication_line_writes_an_unparsed_event_prints_unparsed_and_exits_2(
    run_cli, adjudicate, tmp_path
):
    import json

    (tmp_path / ".tdd").mkdir()
    leaf = tmp_path / "leaf.out"
    leaf.write_text("thinking, but no answer line\n")
    code, out, err = run_cli(adjudicate, ["record", "7", "ci-timeout", str(leaf)], cwd=tmp_path)
    assert (code, out) == (2, "unparsed\n")
    events = [json.loads(l) for l in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    adjudicated = [e for e in events if e.get("event") == "adjudicated"]
    assert len(adjudicated) == 1
    assert {k: adjudicated[0].get(k) for k in ("issue", "cause", "outcome")} == {
        "issue": "7",
        "cause": "ci-timeout",
        "outcome": "unparsed",
    }
    assert adjudicated[0].get("reason")


def test_record_on_a_missing_leaf_output_file_writes_an_unparsed_event_prints_unparsed_and_exits_2(
    run_cli, adjudicate, tmp_path
):
    import json

    (tmp_path / ".tdd").mkdir()
    code, out, err = run_cli(
        adjudicate, ["record", "7", "ci-timeout", str(tmp_path / "absent.out")], cwd=tmp_path
    )
    assert (code, out) == (2, "unparsed\n")
    events = [json.loads(l) for l in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    adjudicated = [e for e in events if e.get("event") == "adjudicated"]
    assert len(adjudicated) == 1
    assert {k: adjudicated[0].get(k) for k in ("issue", "cause", "outcome")} == {
        "issue": "7",
        "cause": "ci-timeout",
        "outcome": "unparsed",
    }
    assert adjudicated[0].get("reason")


def test_left_exits_3_with_a_budget_of_0_though_the_log_holds_no_adjudicated_event(
    run_cli, adjudicate, monkeypatch, tmp_path
):
    import json

    monkeypatch.setenv("VERI_ADJUDICATE_BUDGET", "0")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(json.dumps({"issue": "7", "event": "conductor-start"}) + "\n")
    code, out, err = run_cli(adjudicate, ["left", "7"], cwd=tmp_path)
    assert (code, out, err) == (3, "", "")


def test_record_under_ci_timeout_on_route_rebase_which_adjudicate_md_lists_only_for_ci_conflict_writes_unparsed_and_exits_2(
    run_cli, adjudicate, tmp_path
):
    import json

    (tmp_path / ".tdd").mkdir()
    leaf = tmp_path / "leaf.out"
    leaf.write_text("ADJUDICATION: route rebase — the base moved again\n")
    code, out, err = run_cli(adjudicate, ["record", "7", "ci-timeout", str(leaf)], cwd=tmp_path)
    assert (code, out) == (2, "unparsed\n")
    events = [json.loads(l) for l in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e.get("cause"), e.get("outcome")) for e in events if e.get("event") == "adjudicated"] == [
        ("ci-timeout", "unparsed")
    ]


def test_record_under_ci_conflict_on_route_rebase_prints_the_route_writes_one_route_event_and_exits_1(
    run_cli, adjudicate, tmp_path
):
    import json

    (tmp_path / ".tdd").mkdir()
    leaf = tmp_path / "leaf.out"
    leaf.write_text("ADJUDICATION: route rebase — the base moved again\n")
    code, out, err = run_cli(adjudicate, ["record", "7", "ci-conflict", str(leaf)], cwd=tmp_path)
    assert (code, out) == (1, "route rebase\n")
    events = [json.loads(l) for l in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [
        {k: e.get(k) for k in ("issue", "cause", "outcome", "reason")}
        for e in events
        if e.get("event") == "adjudicated"
    ] == [{"issue": "7", "cause": "ci-conflict", "outcome": "route", "reason": "the base moved again"}]



def test_record_under_unreplaced_cases_on_route_replaces_report_prints_the_route_writes_one_route_event_and_exits_1(
    run_cli, adjudicate, tmp_path
):
    import json

    (tmp_path / ".tdd").mkdir()
    leaf = tmp_path / "leaf.out"
    leaf.write_text("ADJUDICATION: route replaces-report — the report was written late\n")
    code, out, err = run_cli(adjudicate, ["record", "7", "unreplaced-cases", str(leaf)], cwd=tmp_path)
    assert (code, out) == (1, "route replaces-report\n")
    events = [json.loads(l) for l in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [
        {k: e.get(k) for k in ("issue", "cause", "outcome", "reason")}
        for e in events
        if e.get("event") == "adjudicated"
    ] == [{"issue": "7", "cause": "unreplaced-cases", "outcome": "route", "reason": "the report was written late"}]

@pytest.mark.parametrize("cause", ["pr-ready-failed", "report-missing", "step-add-refused", "replaces-report-failed", "unreplaced-cases", "reconcile-failed",
                                   "criterion-unreadable"])
def test_record_writes_one_adjudicated_event_of_the_cause_for_each_of_a_retry_a_bail_and_an_unparsable_answer(
    run_cli, adjudicate, tmp_path, cause
):
    import json

    (tmp_path / ".tdd").mkdir()
    answers = {
        "retry": "ADJUDICATION: retry — GitHub answered 502 once\n",
        "bail": "ADJUDICATION: bail — the token lacks the scope\n",
        "unparsed": "no answer line\n",
    }
    results = {}
    for name, text in answers.items():
        leaf = tmp_path / f"{name}.out"
        leaf.write_text(text)
        code, out, err = run_cli(adjudicate, ["record", "7", cause, str(leaf)], cwd=tmp_path)
        results[name] = (code, out)
    assert results == {"retry": (0, "retry\n"), "bail": (1, "bail\n"), "unparsed": (2, "unparsed\n")}
    events = [json.loads(l) for l in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [
        (e.get("issue"), e.get("cause"), e.get("outcome"), e.get("reason"))
        for e in events
        if e.get("event") == "adjudicated"
    ] == [
        ("7", cause, "retry", "GitHub answered 502 once"),
        ("7", cause, "bail", "the token lacks the scope"),
        ("7", cause, "unparsed", "no ADJUDICATION line"),
    ]


@pytest.mark.parametrize("cause", [
    "ci-conflict", "pr-ready-failed", "report-missing", "step-add-refused", "replaces-report-failed", "unreplaced-cases",
    "reconcile-failed", "criterion-unreadable",
])
def test_left_exits_0_when_every_adjudicated_event_of_the_cause_precedes_the_last_conductor_start(
    run_cli, adjudicate, monkeypatch, tmp_path, cause
):
    import json

    monkeypatch.delenv("VERI_ADJUDICATE_BUDGET", raising=False)
    start = {"issue": "7", "event": "conductor-start"}
    adjudicated = {"issue": "7", "event": "adjudicated", "cause": cause, "outcome": "retry"}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        "".join(json.dumps(e) + "\n" for e in [start, *[adjudicated] * 5, start])
    )
    code, out, err = run_cli(adjudicate, ["left", "7"], cwd=tmp_path)
    assert (code, out, err) == (0, "", "")


def test_record_under_graded_edit_outside_skill_edit_on_deviate_prints_deviate_writes_a_deviate_event_and_exits_4(
    run_cli, adjudicate, tmp_path
):
    import json

    (tmp_path / ".tdd").mkdir()
    leaf = tmp_path / "leaf.out"
    leaf.write_text("thinking\nADJUDICATION: deviate — the criterion names the prose this step changed\n")
    code, out, err = run_cli(adjudicate, ["record", "7", "graded-edit-outside-skill-edit", str(leaf)], cwd=tmp_path)
    assert (code, out) == (4, "deviate\n")
    events = [json.loads(l) for l in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [
        {k: e.get(k) for k in ("issue", "cause", "outcome", "reason")}
        for e in events
        if e.get("event") == "adjudicated"
    ] == [{
        "issue": "7",
        "cause": "graded-edit-outside-skill-edit",
        "outcome": "deviate",
        "reason": "the criterion names the prose this step changed",
    }]


def test_record_under_tests_frozen_refused_on_deviate_prints_deviate_writes_a_deviate_event_and_exits_4(
    run_cli, adjudicate, tmp_path
):
    import json

    (tmp_path / ".tdd").mkdir()
    leaf = tmp_path / "leaf.out"
    leaf.write_text("thinking\nADJUDICATION: deviate — the fixture the criterion needs moved\n")
    code, out, err = run_cli(adjudicate, ["record", "7", "tests-frozen-refused", str(leaf)], cwd=tmp_path)
    assert (code, out) == (4, "deviate\n")
    events = [json.loads(l) for l in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [
        {k: e.get(k) for k in ("issue", "cause", "outcome", "reason")}
        for e in events
        if e.get("event") == "adjudicated"
    ] == [{
        "issue": "7",
        "cause": "tests-frozen-refused",
        "outcome": "deviate",
        "reason": "the fixture the criterion needs moved",
    }]


def test_record_under_graded_edit_outside_skill_edit_on_retry_records_retry_and_exits_0_which_bails(
    run_cli, adjudicate, tmp_path
):
    import json

    (tmp_path / ".tdd").mkdir()
    leaf = tmp_path / "leaf.out"
    leaf.write_text("ADJUDICATION: retry — run it again\n")
    code, out, err = run_cli(adjudicate, ["record", "7", "graded-edit-outside-skill-edit", str(leaf)], cwd=tmp_path)
    assert (code, out) == (0, "retry\n")
    events = [json.loads(l) for l in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e.get("cause"), e.get("outcome")) for e in events if e.get("event") == "adjudicated"] == [
        ("graded-edit-outside-skill-edit", "retry")
    ]


def test_record_under_ci_timeout_which_no_waivable_rule_names_on_deviate_writes_unparsed_and_exits_2(
    run_cli, adjudicate, tmp_path
):
    import json

    (tmp_path / ".tdd").mkdir()
    leaf = tmp_path / "leaf.out"
    leaf.write_text("ADJUDICATION: deviate — the runner is slow, carry on\n")
    code, out, err = run_cli(adjudicate, ["record", "7", "ci-timeout", str(leaf)], cwd=tmp_path)
    assert (code, out) == (2, "unparsed\n")
    events = [json.loads(l) for l in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e.get("cause"), e.get("outcome")) for e in events if e.get("event") == "adjudicated"] == [
        ("ci-timeout", "unparsed")
    ]


def _write_events(tmp_path, events):
    import json

    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))


def test_deviation_left_exits_0_while_the_issue_holds_fewer_deviated_events_than_the_default_budget_of_1(
    run_cli, adjudicate, monkeypatch, tmp_path
):
    monkeypatch.delenv("VERI_DEVIATION_BUDGET", raising=False)
    _write_events(tmp_path, [
        {"issue": "7", "event": "conductor-start"},
        {"issue": "8", "event": "deviated", "rule": "graded-edit", "step": "3", "reason": "x"},
    ])
    code, out, err = run_cli(adjudicate, ["deviation-left", "7"], cwd=tmp_path)
    assert (code, out, err) == (0, "", "")


def test_deviation_left_exits_3_once_the_issue_holds_as_many_deviated_events_as_the_budget(
    run_cli, adjudicate, monkeypatch, tmp_path
):
    monkeypatch.delenv("VERI_DEVIATION_BUDGET", raising=False)
    _write_events(tmp_path, [
        {"issue": "7", "event": "conductor-start"},
        {"issue": "7", "event": "deviated", "rule": "graded-edit", "step": "3", "reason": "x"},
    ])
    code, out, err = run_cli(adjudicate, ["deviation-left", "7"], cwd=tmp_path)
    assert (code, out, err) == (3, "", "")


def test_deviation_left_exits_2_naming_the_variable_when_the_budget_is_not_a_whole_number(
    run_cli, adjudicate, monkeypatch, tmp_path
):
    _write_events(tmp_path, [{"issue": "7", "event": "conductor-start"}])
    for bad in ("-1", "one", "1.5"):
        monkeypatch.setenv("VERI_DEVIATION_BUDGET", bad)
        code, out, err = run_cli(adjudicate, ["deviation-left", "7"], cwd=tmp_path)
        assert (code, out, "VERI_DEVIATION_BUDGET" in err) == (2, "", True), bad


def test_check_budget_exits_2_naming_the_variable_for_a_deviation_budget_that_is_not_a_whole_number(
    run_cli, adjudicate, monkeypatch
):
    monkeypatch.delenv("VERI_ADJUDICATE_BUDGET", raising=False)
    monkeypatch.setenv("VERI_DEVIATION_BUDGET", "two")
    code, out, err = run_cli(adjudicate, ["--check-budget"])
    assert (code, out, "VERI_DEVIATION_BUDGET" in err) == (2, "", True)


def test_deviation_left_exits_2_when_the_event_log_cannot_be_read(run_cli, adjudicate, monkeypatch, tmp_path):
    monkeypatch.delenv("VERI_DEVIATION_BUDGET", raising=False)
    (tmp_path / ".tdd" / "events.jsonl").mkdir(parents=True)
    code, out, err = run_cli(adjudicate, ["deviation-left", "7"], cwd=tmp_path)
    assert (code, out) == (2, "")
