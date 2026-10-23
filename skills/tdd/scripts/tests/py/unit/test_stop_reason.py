"""Small cases for stop-reason.sh's report, driven in-process through run_cli."""
import importlib
import json
import os

from conftest import live_conductor


def test_a_run_whose_events_log_ends_with_a_done_event_prints_done_and_that_events_pr(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    events = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "events.jsonl"
    events.parent.mkdir(parents=True)
    events.write_text("".join(json.dumps(e) + "\n" for e in (
        {"ts": 100, "issue": "7", "event": "step-done"},
        {"ts": 200, "issue": "7", "event": "done", "pr": "https://github.com/o/r/pull/9"})))

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out) == (0, "done https://github.com/o/r/pull/9\n")


def test_a_run_whose_events_log_ends_with_a_bail_or_a_stop_event_prints_that_events_fields(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    for issue, last in (
            ("7", {"ts": 200, "issue": "7", "event": "bail", "phase": "red", "classification": "process"}),
            ("8", {"ts": 200, "issue": "8", "event": "stop", "mode": "graceful"})):
        events = tmp_path / ".tdd" / "wt" / issue / ".tdd" / "events.jsonl"
        events.parent.mkdir(parents=True)
        events.write_text("".join(json.dumps(e) + "\n" for e in (
            {"ts": 100, "issue": issue, "event": "step-done"}, last)))

    bailed = run_cli(stop_reason, ["7"], cwd=tmp_path)
    stopped = run_cli(stop_reason, ["8"], cwd=tmp_path)

    assert (bailed[0], bailed[1], stopped[0], stopped[1]) == (
        0, "bailed red process\n", 0, "stopped graceful\n")


def test_a_run_with_a_live_conductor_and_no_end_event_prints_running(tmp_path, monkeypatch, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    run = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    live_conductor(monkeypatch, run, "7")

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out) == (0, "running\n")


def test_a_run_with_no_end_event_and_no_live_conductor_prints_usage_limit_and_the_reset_time_of_the_last_result_record(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    for issue, text in (("7", "You've hit your weekly limit · resets Oct 7, 3pm"),
                        ("8", "You've hit your weekly limit")):
        run = tmp_path / ".tdd" / "wt" / issue / ".tdd"
        run.mkdir(parents=True)
        (run / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": issue, "event": "step-done"}) + "\n")
        (tmp_path / ".tdd" / ("conductor-%s.log" % issue)).write_text("".join(json.dumps(r) + "\n" for r in (
            {"type": "system", "subtype": "init"},
            {"type": "result", "is_error": True, "result": text})))

    with_reset = run_cli(stop_reason, ["7"], cwd=tmp_path)
    without_reset = run_cli(stop_reason, ["8"], cwd=tmp_path)

    assert (with_reset[0], with_reset[1], without_reset[0], without_reset[1]) == (
        0, "usage-limit Oct 7, 3pm\n", 0, "usage-limit\n")


def test_a_run_with_no_end_event_and_no_live_conductor_prints_usage_limit_when_its_last_leaf_log_reports_a_rate_limit_error(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    run = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    (run / "develop-green.log").write_text("".join(json.dumps(r) + "\n" for r in (
        {"type": "system", "subtype": "init"},
        {"type": "assistant", "error": "rate_limit", "message": {"content": [{"type": "text", "text": "429"}]}})))
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in (
        {"type": "system", "subtype": "init"},
        {"type": "result", "is_error": False, "result": "Step finished"})))

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out) == (0, "usage-limit\n")


def test_a_run_with_no_end_event_no_live_conductor_and_no_usage_limit_prints_unknown_and_the_last_result_text(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    run = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in (
        {"type": "system", "subtype": "init"},
        {"type": "result", "is_error": False, "result": "Connection reset by peer"})))

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out) == (0, "unknown Connection reset by peer\n")


def test_after_its_first_line_it_prints_gap_from_to_for_each_pair_of_consecutive_events_further_apart_than_the_default_sleep_gap(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    run = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text("".join(json.dumps({"ts": ts, "issue": "7", "event": "step-done"}) + "\n"
                                             for ts in (100, 1000, 2001, 2500)))
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in (
        {"type": "result", "is_error": False, "result": "Connection reset by peer"},)))

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out) == (0, "unknown Connection reset by peer\ngap 1000 2001\n")


def test_a_set_sleep_gap_replaces_the_default_so_a_pair_100_seconds_apart_prints_a_gap_line_and_a_pair_60_seconds_apart_does_not(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    run = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text("".join(json.dumps({"ts": ts, "issue": "7", "event": "step-done"}) + "\n"
                                             for ts in (100, 200, 260)))
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in (
        {"type": "result", "is_error": False, "result": "Connection reset by peer"},)))

    code, out, err = run_cli(stop_reason, ["7"], env={"VERI_SLEEP_GAP": "60"}, cwd=tmp_path)

    assert (code, out) == (0, "unknown Connection reset by peer\ngap 100 200\n")


def test_a_sleep_gap_that_is_not_a_whole_number_of_at_least_1_exits_2_with_a_diagnostic_naming_VERI_SLEEP_GAP(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    run = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text("".join(json.dumps({"ts": ts, "issue": "7", "event": "step-done"}) + "\n"
                                             for ts in (100, 200)))
    (tmp_path / ".tdd" / "conductor-7.log").write_text(json.dumps(
        {"type": "result", "is_error": False, "result": "Connection reset by peer"}) + "\n")

    outcomes = {}
    for bad in ("0", "abc", "1.5", ""):
        code, out, err = run_cli(stop_reason, ["7"], env={"VERI_SLEEP_GAP": bad}, cwd=tmp_path)
        outcomes[bad] = (code, "VERI_SLEEP_GAP" in err)

    assert outcomes == {bad: (2, True) for bad in ("0", "abc", "1.5", "")}


def test_a_run_directory_with_no_events_log_exits_2_naming_the_missing_events_log_and_prints_no_exception_1816(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    (tmp_path / ".tdd" / "wt" / "7").mkdir(parents=True)

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out, "events.jsonl" in err, "Error" in err or "Traceback" in err) == (2, "", True, False)


def test_a_run_with_no_end_event_and_no_live_conductor_whose_conductor_log_holds_no_result_record_exits_2_naming_that_log_and_prints_no_exception_1816(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    run = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    (tmp_path / ".tdd" / "conductor-7.log").write_text(json.dumps({"type": "system", "subtype": "init"}) + "\n")

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out, "conductor-7.log" in err, "result" in err, "Error" in err or "Traceback" in err) == (
        2, "", True, True, False)


def test_a_run_with_no_end_event_whose_conductor_pid_names_a_dead_process_does_not_print_running_1816(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    run = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    (run / "conductor.pid").write_text("99999999\n")
    (tmp_path / ".tdd" / "conductor-7.log").write_text(json.dumps(
        {"type": "result", "is_error": True, "result": "You've hit your weekly limit"}) + "\n")

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out) == (0, "usage-limit\n")


def test_a_run_with_no_end_event_and_no_live_conductor_and_no_conductor_log_anywhere_exits_2_naming_the_clones_log_and_prints_no_exception_1867(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    run = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out, err.startswith("stop-reason.sh: no conductor log at "),
            err.endswith(os.path.join(".tdd", "conductor-7.log") + "\n"), err.count("\n")) == (
        2, "", True, True, 1)


def test_a_run_with_no_end_event_and_no_live_conductor_reports_from_the_conductor_log_in_its_own_tdd_and_prefers_it_over_the_clones_1867(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    run = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    for where, reset in ((run, "3pm"), (tmp_path / ".tdd", "9pm")):
        (where / "conductor-7.log").write_text(json.dumps(
            {"type": "result", "is_error": True, "result": "You've hit your limit resets %s" % reset}) + "\n")

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out, err) == (0, "usage-limit 3pm\n", "")


def test_a_run_with_no_end_event_and_no_live_conductor_whose_conductor_log_is_only_in_the_clones_tdd_reports_from_it_1867(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    run = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    (tmp_path / ".tdd" / "conductor-7.log").write_text(json.dumps(
        {"type": "result", "is_error": True, "result": "You've hit your limit resets 9pm"}) + "\n")

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out, err) == (0, "usage-limit 9pm\n", "")


def test_a_conductor_log_whose_last_launch_has_no_result_record_exits_2_and_never_prints_the_earlier_launchs_reason_1938(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    run = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    conductor_log = tmp_path / ".tdd" / "conductor-7.log"
    conductor_log.write_text("".join(json.dumps(r) + "\n" for r in (
        {"type": "system", "subtype": "init"},
        {"type": "result", "is_error": True, "result": "You've hit your weekly limit · resets Oct 7, 3pm"},
        {"type": "system", "subtype": "init"})))

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out, "no result record in" in err, "conductor-7.log" in err) == (2, "", True, True)


def test_a_conductor_log_whose_last_launch_has_a_result_record_is_decided_by_that_record_alone_1938(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    run = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in (
        {"type": "system", "subtype": "init"},
        {"type": "result", "is_error": True, "result": "You've hit your weekly limit · resets Oct 7, 3pm"},
        {"type": "system", "subtype": "init"},
        {"type": "result", "is_error": True, "result": "boom"})))

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out, err) == (0, "unknown boom\n", "")


def test_an_events_log_holding_a_line_that_is_not_json_exits_2_and_prints_nothing_to_stdout(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    events = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "events.jsonl"
    events.parent.mkdir(parents=True)
    events.write_text(json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\nnot json\n"
                      + json.dumps({"ts": 200, "issue": "7", "event": "done", "pr": "p"}) + "\n")

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out) == (2, "")
