"""Small cases for veri.run_end's answer to whether a run has ended."""
import importlib
import json
import os

PARENT = 424242


def fake_ps(monkeypatch, own, parent_line=""):
    """Answer pid_file's ps reads: this process runs <own>, its parent PARENT runs <parent_line>."""
    table = {("command", os.getpid()): own, ("ppid", os.getpid()): str(PARENT), ("command", PARENT): parent_line}
    for name in ("pid_file", "veri.pid_file"):
        monkeypatch.setattr(importlib.import_module(name), "_ps",
                            lambda field, pid: table.get((field, int(pid)), ""), raising=True)


def test_a_run_whose_log_holds_a_done_bail_or_stop_event_with_no_later_resume_has_ended_with_that_cause_and_mark(tmp_path):
    run_end = importlib.import_module("veri.run_end")
    marks = {"done": {"ts": 200, "issue": "7", "event": "done", "pr": "https://github.com/o/r/pull/9"},
             "bailed": {"ts": 200, "issue": "7", "event": "bail", "phase": "red"},
             "stopped": {"ts": 200, "issue": "7", "event": "stop", "mode": "graceful"}}
    answers = {}
    for cause, mark in marks.items():
        run = tmp_path / cause
        (run / ".tdd").mkdir(parents=True)
        (run / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in (
            {"ts": 100, "issue": "7", "event": "step-done"}, mark)))
        answers[cause] = run_end.run_end(run)

    assert answers == {cause: (True, cause, mark) for cause, mark in marks.items()}


def test_a_run_with_no_mark_no_live_conductor_and_no_conductor_log_has_ended_with_cause_unknown_2007(tmp_path):
    run_end = importlib.import_module("veri.run_end")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")

    ended, cause, mark = run_end.run_end(tmp_path)

    assert (ended, cause, not mark) == (True, "unknown", True)


def test_a_live_pid_whose_command_line_is_not_a_claude_leaves_the_run_ended_unknown_2007(tmp_path, monkeypatch):
    run_end = importlib.import_module("veri.run_end")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    (tmp_path / ".tdd" / "conductor.pid").write_text(f"{os.getpid()}\n")
    answers = {}
    for name, line in {"other-issue": "bash /x/run-conductor.sh 8",
                       "python-other-issue": "python3 /x/veri/run_conductor.py 70",
                       "unrelated": "vim run_conductor_notes_7.txt"}.items():
        fake_ps(monkeypatch, line, "python3 /x/veri/run_conductor.py 7")
        ended, cause, mark = run_end.run_end(tmp_path)
        answers[name] = (ended, cause, not mark)

    assert answers == {name: (True, "unknown", True)
                       for name in ("other-issue", "python-other-issue", "unrelated")}


def test_a_live_claude_child_whose_parent_is_run_conductor_py_has_not_ended_and_whose_parent_is_not_has_2007(tmp_path, monkeypatch):
    run_end = importlib.import_module("veri.run_end")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    (tmp_path / ".tdd" / "conductor.pid").write_text(f"{os.getpid()}\n")
    answers = {}
    for name, parent_line in {"python-conductor": "python3 /x/veri/run_conductor.py 7",
                              "other-parent": "bash -l"}.items():
        fake_ps(monkeypatch, "claude -p --model sonnet", parent_line)
        ended, cause, mark = run_end.run_end(tmp_path)
        answers[name] = (ended, not mark)

    assert answers == {"python-conductor": (False, True), "other-parent": (True, True)}


def test_a_run_with_no_mark_whose_conductor_pid_answers_kill_0_as_a_live_conductor_has_not_ended_with_cause_none_2007(tmp_path, monkeypatch):
    run_end = importlib.import_module("veri.run_end")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    (tmp_path / ".tdd" / "conductor.pid").write_text(f"{os.getpid()}\n")
    fake_ps(monkeypatch, "claude -p --model opus", "python3 /x/veri/run_conductor.py 7 --flag")

    assert run_end.run_end(tmp_path) == (False, None, {})


def test_a_run_with_bail_then_resume_then_launch_events_and_a_live_conductor_has_not_ended_and_only_marks_after_the_last_resume_stand_2007(tmp_path, monkeypatch):
    run_end = importlib.import_module("veri.run_end")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "conductor.pid").write_text(f"{os.getpid()}\n")
    fake_ps(monkeypatch, "claude -p --model opus", "python3 /x/veri/run_conductor.py 7")
    log = tmp_path / ".tdd" / "events.jsonl"
    prefix = [{"ts": 100, "issue": "7", "event": "bail", "phase": "red"},
              {"ts": 200, "issue": "7", "event": "resume"},
              {"ts": 300, "issue": "7", "event": "launch"},
              {"ts": 400, "issue": "7", "event": "launch"}]
    log.write_text("".join(json.dumps(e) + "\n" for e in prefix))
    resumed = run_end.run_end(tmp_path)
    log.write_text("".join(json.dumps(e) + "\n" for e in prefix + [{"ts": 500, "issue": "7", "event": "stop", "mode": "graceful"}]))
    stopped_after = run_end.run_end(tmp_path)

    assert (resumed, stopped_after[:2]) == ((False, None, {}), (True, "stopped"))


def test_a_run_with_no_mark_and_no_live_conductor_whose_latest_launch_ends_in_a_usage_limit_result_has_ended_with_cause_usage_limit_2007(tmp_path):
    run_end = importlib.import_module("veri.run_end")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    records = [{"type": "system", "subtype": "init"},
               {"type": "result", "result": "boom"},
               {"type": "system", "subtype": "init"},
               {"type": "result", "result": "Claude usage limit reached. The limit resets 3pm"}]
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))

    ended, cause, mark = run_end.run_end(tmp_path)

    assert (ended, cause, not mark) == (True, "usage-limit", True)


def test_a_run_with_no_mark_and_no_live_conductor_ends_with_cause_usage_limit_on_a_rate_limit_leaf_log_or_the_clones_conductor_log_2007(tmp_path, monkeypatch):
    run_end = importlib.import_module("veri.run_end")
    event = json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n"

    def lines(*records):
        return "".join(json.dumps(r) + "\n" for r in records)

    leafy = tmp_path / "leafy"
    (leafy / ".tdd").mkdir(parents=True)
    (leafy / ".tdd" / "events.jsonl").write_text(event)
    (leafy / ".tdd" / "conductor-7.log").write_text(
        lines({"type": "system", "subtype": "init"}, {"type": "result", "result": "boom"}))
    leaf_log = leafy / ".tdd" / "develop-green.log"
    leaf_log.write_text(lines({"type": "assistant"}, {"type": "assistant", "error": "rate_limit"}))
    os.utime(leaf_log, (4102444800, 4102444800))

    clone = tmp_path / "clone"
    (clone / ".tdd").mkdir(parents=True)
    (clone / ".tdd" / "conductor-7.log").write_text(
        lines({"type": "system", "subtype": "init"},
              {"type": "result", "result": "Claude usage limit reached"}))
    bare = tmp_path / "bare"
    (bare / ".tdd").mkdir(parents=True)
    (bare / ".tdd" / "events.jsonl").write_text(event)
    monkeypatch.chdir(clone)

    answers = [run_end.run_end(d)[:2] for d in (leafy, bare)]

    assert answers == [(True, "usage-limit"), (True, "usage-limit")]


def test_a_run_with_no_mark_and_no_live_conductor_whose_latest_launch_has_no_result_record_has_ended_with_cause_killed_2007(tmp_path):
    run_end = importlib.import_module("veri.run_end")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    records = [{"type": "system", "subtype": "init"},
               {"type": "result", "result": "done"},
               {"type": "system", "subtype": "init"},
               {"type": "assistant"}]
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))

    ended, cause, mark = run_end.run_end(tmp_path)

    assert (ended, cause, not mark) == (True, "killed", True)


def test_a_run_with_no_mark_and_no_live_conductor_whose_latest_launch_ends_in_a_result_that_is_not_a_usage_limit_has_ended_with_cause_unknown_2007(tmp_path):
    run_end = importlib.import_module("veri.run_end")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    records = [{"type": "system", "subtype": "init"},
               {"type": "result", "result": "Claude usage limit reached"},
               {"type": "system", "subtype": "init"},
               {"type": "result", "result": "all steps finished"}]
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))

    ended, cause, mark = run_end.run_end(tmp_path)

    assert (ended, cause, not mark) == (True, "unknown", True)


def test_a_pid_that_answers_kill_0_but_whose_process_is_not_a_conductor_has_ended_with_the_cause_read_from_the_conductor_log_2007(tmp_path, monkeypatch):
    run_end = importlib.import_module("veri.run_end")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    (tmp_path / ".tdd" / "conductor.pid").write_text(f"{os.getpid()}\n")
    records = [{"type": "system", "subtype": "init"},
               {"type": "result", "result": "Claude usage limit reached"}]
    (tmp_path / ".tdd" / "conductor-7.log").write_text("".join(json.dumps(r) + "\n" for r in records))
    fake_ps(monkeypatch, "vim notes.txt", "bash /x/run-conductor.sh 8")

    ended, cause, mark = run_end.run_end(tmp_path)

    assert (ended, cause, not mark) == (True, "usage-limit", True)


def test_a_live_conductor_for_this_issue_leaves_the_run_not_ended_when_the_last_event_has_no_issue_field_2198(tmp_path, monkeypatch):
    run_end = importlib.import_module("veri.run_end")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in (
        {"ts": 100, "issue": "7", "event": "step-done"}, {"ts": 200, "event": "note"})))
    (tmp_path / ".tdd" / "conductor.pid").write_text(f"{os.getpid()}\n")
    fake_ps(monkeypatch, "claude -p --model opus", "python3 /x/veri/run_conductor.py 7")

    ended, cause, mark = run_end.run_end(tmp_path)

    assert (ended, cause, not mark) == (False, None, True)


def test_a_live_claude_child_of_run_conductor_recorded_in_conductor_pid_with_no_events_yet_has_not_ended_and_an_unrelated_live_pid_has_2249(tmp_path, monkeypatch):
    run_end = importlib.import_module("veri.run_end")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text("")
    (tmp_path / ".tdd" / "conductor.pid").write_text(f"{os.getpid()}\n")
    answers = {}
    for name, (own, parent_line) in {"conductor": ("claude -p --model sonnet", "python3 /x/veri/run_conductor.py 7"),
                                   "unrelated": ("vim notes.txt", "bash -l")}.items():
        fake_ps(monkeypatch, own, parent_line)
        ended, cause, mark = run_end.run_end(tmp_path)
        answers[name] = (ended, not mark)

    assert answers == {"conductor": (False, True), "unrelated": (True, True)}
