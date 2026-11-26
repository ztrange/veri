"""run_conductor.main's skill snapshot on disk: read-only while the run executes it, removed at exit (#3963)."""
import importlib
import json
import os

import pytest

import pinned_scripts
from test_run_conductor_process import (
    fake_pin,
    fake_snapshot,
    past_the_guards,
    scratch_tmpdir,
)

COMMIT = "1" * 40
SKILL = {"SKILL.md": "# skill\n", "scripts/status.sh": "echo status\n"}


def launched(tmp_path, monkeypatch, capfdbinary, probe, issue="4242", files=SKILL):
    """run_conductor.main(<issue>) with git and tar faked, the launch replaced by <probe>(snapshot); answers
    (exit code, names left in the scratch TMPDIR)."""
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    scratch = tmp_path / "tmp" if (tmp_path / "tmp").is_dir() else scratch_tmpdir(tmp_path, monkeypatch)
    monkeypatch.chdir(tmp_path)
    calls = fake_pin(monkeypatch, COMMIT, {COMMIT + "^{commit}"})
    fake_snapshot(monkeypatch, calls, 0, 0, files=files)
    run_conductor = importlib.import_module("veri.run_conductor")
    monkeypatch.setattr(run_conductor, "launch", lambda snapshot, *_, **__: probe(snapshot) or 0)
    code = run_conductor.main([issue])
    capfdbinary.readouterr()
    return code, sorted(os.listdir(scratch))


def test_main_removes_a_snapshot_whose_files_and_directories_are_read_only_at_exit_leaving_nothing_of_it_3963(
        tmp_path, monkeypatch, capfdbinary):
    assert launched(tmp_path, monkeypatch, capfdbinary, pinned_scripts.make_read_only) == (0, [])


def test_main_replaces_a_read_only_pinned_scripts_copy_the_last_launch_left_on_the_next_launch_3963(
        tmp_path, monkeypatch, capfdbinary):
    run_conductor = importlib.import_module("veri.run_conductor")
    monkeypatch.setattr(run_conductor, "is_registered_worktree", lambda issue: True)
    kept = tmp_path / ".tdd" / "wt" / "4242" / ".tdd" / "pinned-scripts"
    first = launched(tmp_path, monkeypatch, capfdbinary, lambda snapshot: None)
    pinned_scripts.make_read_only(str(kept))

    second = launched(tmp_path, monkeypatch, capfdbinary, lambda snapshot: None,
                      files={"SKILL.md": "# skill\n", "scripts/status.sh": "echo second\n"})

    assert (first, second, (kept / "status.sh").read_text(), (kept / ".gitignore").read_text()) == (
        (0, []), (0, []), "echo second\n", "*\n")


@pytest.mark.skipif(os.geteuid() == 0, reason="uid 0 writes through missing write bits")
def test_main_makes_a_write_into_a_file_of_the_fresh_snapshot_fail_with_a_permission_error_3963(
        tmp_path, monkeypatch, capfdbinary):
    tried = []

    def write_into(snapshot):
        try:
            with open(os.path.join(snapshot, "scripts", "status.sh"), "a") as script:
                script.write("echo stray\n")
            tried.append("written")
        except OSError as error:
            tried.append(type(error).__name__)

    assert (launched(tmp_path, monkeypatch, capfdbinary, write_into), tried) == ((0, []), ["PermissionError"])


def test_main_writes_the_digest_of_the_extracted_snapshot_to_the_main_trees_issue_snapshot_digest_file_3964(
        tmp_path, monkeypatch, capfdbinary):
    seen = []

    assert launched(tmp_path, monkeypatch, capfdbinary, lambda snapshot: seen.append(
        pinned_scripts.snapshot_digest(snapshot))) == (0, [])
    assert (tmp_path / ".tdd" / "issue-4242-snapshot-digest").read_text() == pinned_scripts.digest_text(seen[0]) != "[]\n"


def test_main_on_a_snapshot_a_leaf_edited_says_so_logs_snapshot_changed_and_exits_2_removing_the_snapshot_3964(
        tmp_path, monkeypatch, capfdbinary):
    run_conductor = importlib.import_module("veri.run_conductor")
    errors = []
    real = run_conductor.main

    def main_keeping_stderr(argv):
        code = real(argv)
        errors.append(capfdbinary.readouterr().err)
        return code
    monkeypatch.setattr(run_conductor, "main", main_keeping_stderr)

    def edit(snapshot):
        script = os.path.join(snapshot, "scripts", "status.sh")
        pinned_scripts.change_mode(script, lambda mode: mode | 0o200)
        with open(script, "a") as handle:
            handle.write("echo edited\n")

    answer = launched(tmp_path, monkeypatch, capfdbinary, edit)
    log = tmp_path / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl"
    events = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []

    assert (answer, errors, [(e["event"], e.get("path")) for e in events]) == (
        (2, []), [b"run-conductor: the skill snapshot changed during the run\n"],
        [("snapshot-changed", "scripts/status.sh")])


def exit_of(tmp_path, monkeypatch, capfdbinary, probe):
    """(launched answer, stderr of main, [(event, path)] of the run's event log) for a launch whose leaf is <probe>."""
    run_conductor = importlib.import_module("veri.run_conductor")
    errors, real = [], run_conductor.main

    def main_keeping_stderr(argv):
        code = real(argv)
        errors.append(capfdbinary.readouterr().err)
        return code
    monkeypatch.setattr(run_conductor, "main", main_keeping_stderr)
    answer = launched(tmp_path, monkeypatch, capfdbinary, probe)
    log = tmp_path / ".tdd" / "wt" / "4242" / ".tdd" / "events.jsonl"
    events = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    return answer, errors, [(e["event"], e.get("path")) for e in events]


def digest_file(tmp_path):
    return tmp_path / ".tdd" / "issue-4242-snapshot-digest"


def test_main_at_exit_catches_an_edited_snapshot_whose_digest_file_a_leaf_rewrote_to_match_3964(
        tmp_path, monkeypatch, capfdbinary):
    def edit_and_relabel(snapshot):
        script = os.path.join(snapshot, "scripts", "status.sh")
        pinned_scripts.change_mode(script, lambda mode: mode | 0o200)
        with open(script, "a") as handle:
            handle.write("echo edited\n")
        digest_file(tmp_path).write_text(pinned_scripts.digest_text(pinned_scripts.snapshot_digest(snapshot)))

    assert exit_of(tmp_path, monkeypatch, capfdbinary, edit_and_relabel) == (
        (2, []), [b"run-conductor: the skill snapshot changed during the run\n"],
        [("snapshot-changed", "scripts/status.sh")])


def test_main_at_exit_reports_a_digest_file_a_leaf_rewrote_naming_the_digest_file_3964(
        tmp_path, monkeypatch, capfdbinary):
    def relabel(snapshot):
        digest_file(tmp_path).write_text("0 SKILL.md\n")

    assert exit_of(tmp_path, monkeypatch, capfdbinary, relabel) == (
        (2, []), [b"run-conductor: the skill snapshot changed during the run\n"],
        [("snapshot-changed", str(digest_file(tmp_path)))])


def test_main_removes_the_snapshot_even_when_keeping_its_scripts_fails_on_a_fifo_a_leaf_left_3964(
        tmp_path, monkeypatch, capfdbinary):
    run_conductor = importlib.import_module("veri.run_conductor")
    monkeypatch.setattr(run_conductor, "is_registered_worktree", lambda issue: True)

    def leave_a_fifo(snapshot):
        pinned_scripts.change_mode(os.path.join(snapshot, "scripts"), lambda mode: mode | 0o200)
        os.mkfifo(os.path.join(snapshot, "scripts", "pipe"))

    with pytest.raises(OSError):
        launched(tmp_path, monkeypatch, capfdbinary, leave_a_fifo)
    assert os.listdir(tmp_path / "tmp") == []
