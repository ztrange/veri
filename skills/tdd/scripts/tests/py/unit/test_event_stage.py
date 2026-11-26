"""event.stage: one helper marks a stage, a `stage-start` before its body and a `stage-end` after it on every exit
(PRD 035.5a, MW2, MW8)."""
import json

import pytest
from veri import event


@pytest.fixture
def run(tmp_path, monkeypatch):
    """A run directory, holding its `.tdd/`, and a monotonic clock that reads 100 s, then 107.9 s."""
    readings = iter([100.0, 107.9])
    monkeypatch.setattr(event.time, "monotonic", lambda: next(readings))
    (tmp_path / ".tdd").mkdir()
    return tmp_path


def stage_lines(run):
    log = run / ".tdd" / "events.jsonl"
    return [{key: line[key] for key in ("event", "stage", "status", "secs", "issue") if key in line}
            for line in map(json.loads, log.read_text().splitlines())]


@pytest.mark.parametrize("code", [0, 1, 2])
def test_4228_a_stage_writes_its_start_runs_its_body_and_writes_its_end_with_the_bodys_exit_code_and_whole_seconds(
        run, code):
    returned = event.stage("baseline", lambda: code, str(run), {"issue": "7"})

    assert returned == code
    assert stage_lines(run) == [{"event": "stage-start", "stage": "baseline", "issue": "7"},
                                {"event": "stage-end", "stage": "baseline", "status": str(code), "secs": "7",
                                 "issue": "7"}]


def test_4228_a_body_that_raises_ends_its_stage_with_status_2_and_its_error_goes_on(run):
    def body():
        raise RuntimeError("broken")

    with pytest.raises(RuntimeError, match="broken"):
        event.stage("preflight", body, str(run), {"issue": "7"})

    assert stage_lines(run)[-1] == {"event": "stage-end", "stage": "preflight", "status": "2", "secs": "7",
                                    "issue": "7"}


@pytest.mark.parametrize("code", [0, 1, 3])
def test_4228_with_the_journal_directory_unwritable_a_stage_returns_its_bodys_exit_code_unchanged(run, code, capfd):
    (run / ".tdd" / "events.jsonl").mkdir()  # a directory where the run's event log should be

    returned = event.stage("baseline", lambda: code, str(run), {"issue": "7"})

    assert returned == code
    assert list((run / ".tdd" / "events.jsonl").iterdir()) == []
    assert capfd.readouterr().err != ""


@pytest.mark.parametrize("code", [4, 128])
def test_4228_a_body_exit_code_outside_0_to_3_ends_its_stage_with_status_2_and_is_returned_unchanged(run, code):
    returned = event.stage("preflight", lambda: code, str(run), {"issue": "7"})

    assert returned == code
    assert stage_lines(run)[-1] == {"event": "stage-end", "stage": "preflight", "status": "2", "secs": "7",
                                    "issue": "7"}


@pytest.mark.parametrize("code", [0, 1, 3])
def test_4228_a_stage_line_whose_write_exits_the_process_still_runs_the_body_and_returns_its_code(run, monkeypatch, code):
    ran = []

    def short_write(*args, **kwargs):
        raise SystemExit(2)  # append_once's short journal write

    monkeypatch.setattr(event, "append", short_write)

    returned = event.stage("baseline", lambda: ran.append(code) or code, str(run), {"issue": "7"})

    assert (returned, ran) == (code, [code])


@pytest.mark.parametrize("code", [0, 1, 2])
def test_4230_a_stage_in_a_directory_with_no_tdd_runs_its_body_unmarked_and_creates_no_tdd(tmp_path, code):
    returned = event.stage("ci-wait", lambda: code, str(tmp_path), {"issue": "7"})

    assert (returned, (tmp_path / ".tdd").exists()) == (code, False)
