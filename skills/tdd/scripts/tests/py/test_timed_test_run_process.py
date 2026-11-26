"""Process cases for veri/timed_test_run.py: the ones that start a real process; the small cases are in unit/test_timed_test_run.py."""
import importlib
import json
import os
import re
import subprocess

import pytest


@pytest.fixture
def timed_test_run():
    return importlib.import_module("veri.timed_test_run")


@pytest.mark.process("git init making tmp_path a worktree whose subdirectory is the working directory, and a real true run")
def test_issue_1528_main_from_a_subdirectory_of_a_worktree_records_its_test_run_under_dot_tdd_of_the_toplevel(
        tmp_path, monkeypatch, timed_test_run):
    root = tmp_path / "repo"
    cwd = root / "sub"
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    monkeypatch.delenv("VERI_AWAKE_CLOCK", raising=False)

    assert timed_test_run.main(["fast", "", "true"]) == 0

    assert os.listdir(cwd) == []
    lines = (root / ".tdd" / "events.jsonl").read_text().splitlines()
    assert [json.loads(text)["event"] for text in lines] == ["test-run"]


def _read_events(directory):
    path = directory / ".tdd" / "events.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.is_file() else []


@pytest.mark.process("a real sh -c run as the wrapped command")
def test_cli_runs_the_command_and_writes_one_test_run_event_with_tier_suites_and_seconds_exiting_with_its_status(
        tmp_path, run_cli, timed_test_run):
    suites = "skills/tdd/scripts/tests/unit/next-unchecked.test.sh skills/tdd/scripts/tests/event.test.sh"
    env = {"VERI_ISSUE": "342", "VERI_ACTOR": "developer", "VERI_PHASE": "green", "VERI_STEP": "1",
           "VERI_ATTEMPT": "1"}

    code, out, err = run_cli(timed_test_run, ["fast", suites, "sh", "-c", "exit 7"], env=env, cwd=tmp_path)

    records = _read_events(tmp_path)
    assert (code, len(records)) == (7, 1)
    assert (records[0]["event"], records[0]["tier"], records[0]["suites"]) == ("test-run", "fast", suites)
    assert re.fullmatch(r"[0-9]+", records[0]["seconds"])


@pytest.mark.process("a real sh -c run as the wrapped command, once exiting 7 and once exiting 0")
@pytest.mark.parametrize("want", [7, 0])
def test_cli_records_the_commands_own_exit_status_on_the_test_run_event(
        want, tmp_path, run_cli, timed_test_run):
    env = {"VERI_ISSUE": "383", "VERI_ACTOR": "developer", "VERI_PHASE": "red", "VERI_STEP": "1",
           "VERI_ATTEMPT": "1"}

    code, out, err = run_cli(timed_test_run, ["fast", "skills/tdd/scripts/tests/event.test.sh", "sh", "-c",
                                              "exit %d" % want], env=env, cwd=tmp_path)

    assert (code, [r["status"] for r in _read_events(tmp_path)]) == (want, [str(want)])


@pytest.mark.process("a real sh -c run as the wrapped command, from two working directories")
def test_cli_from_another_working_directory_answers_as_in_place_with_its_one_test_run_line_in_that_directory(
        tmp_path, run_cli, timed_test_run):
    env = {"VERI_ISSUE": "804", "VERI_ACTOR": "developer", "VERI_PHASE": "red", "VERI_STEP": "1",
           "VERI_ATTEMPT": "1"}
    argv = ["fast", "x.test.sh", "sh", "-c", "echo out; echo err >&2; exit 5"]
    here, far = tmp_path / "here", tmp_path / "far"
    here.mkdir()
    far.mkdir()

    in_place = run_cli(timed_test_run, argv, env=env, cwd=here)
    from_afar = run_cli(timed_test_run, argv, env=env, cwd=far)

    for directory, (code, out, err) in ((here, in_place), (far, from_afar)):
        saved = list((directory / ".tdd" / "test-runs").iterdir())
        assert (code, err, len(saved), saved[0].read_text()) == (5, "", 1, "out\nerr\n"), out
        assert out.splitlines()[-1] == f"full output: {directory.resolve() / '.tdd' / 'test-runs' / saved[0].name}", out
    records = _read_events(far)
    assert [(r["event"], r["status"]) for r in records] == [("test-run", "5")]
    assert sorted(p.name for p in tmp_path.iterdir()) == ["far", "here"]
