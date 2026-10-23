"""Small cases for veri.run_end's answer to whether a run has ended."""
import importlib
import json


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


def test_a_live_pid_whose_command_line_is_not_run_conductor_for_this_issue_leaves_the_run_ended_unknown_2007(tmp_path, monkeypatch):
    import os
    run_end = importlib.import_module("veri.run_end")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    (tmp_path / ".tdd" / "conductor.pid").write_text(f"{os.getpid()}\n")
    answers = {}
    for name, line in {"other-issue": "bash /x/run-conductor.sh 8",
                       "python-other-issue": "python3 /x/veri/run_conductor.py 70",
                       "unrelated": "vim run_conductor_notes_7.txt"}.items():
        monkeypatch.setattr(run_end, "command_line", lambda pid, line=line: line, raising=False)
        ended, cause, mark = run_end.run_end(tmp_path)
        answers[name] = (ended, cause, not mark)

    assert answers == {name: (True, "unknown", True)
                       for name in ("other-issue", "python-other-issue", "unrelated")}
