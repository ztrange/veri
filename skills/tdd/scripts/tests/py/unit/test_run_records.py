"""In-process cases for veri/run_records.py: a run's records on origin's refs/veri/runs/<n>, every git call faked."""
import importlib
import json
import os

import pytest

from process_fakes import HANGS


@pytest.fixture
def run_records():
    return importlib.import_module("veri.run_records")


def _kill_reaches(monkeypatch, fake):
    """os.killpg forwards the bound's kill to the fake children by pid, never to a real group."""
    monkeypatch.setattr(os, "killpg", lambda group, sig: [c.send_signal(sig) for c in fake.popens if c.pid == group])


def test_the_carried_journal_keeps_the_issues_lines_and_those_naming_no_issue_as_the_report_counts_them(tmp_path, run_records):
    (tmp_path / ".tdd").mkdir()
    lines = [{"issue": "7", "event": "start"}, {"issue": "", "event": "usage"}, {"event": "test-run"},
             {"issue": "8", "event": "start"}]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in lines))

    carried = run_records.records(str(tmp_path), "7")["events.jsonl"].decode().splitlines()

    assert [json.loads(line) for line in carried] == lines[:3]


def test_the_ref_carries_only_what_a_reader_restores_the_journal_lines_and_the_skill_pin_not_the_timeout_pin(tmp_path, run_records):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text('{"issue": "7", "event": "start"}\n')
    (tmp_path / ".tdd" / "issue-7-skill-commit").write_text("abc1234\n")
    (tmp_path / ".tdd" / "issue-7-timeout").write_text("3600\n")

    assert sorted(run_records.records(str(tmp_path), "7")) == ["events.jsonl", "issue-7-skill-commit"]


def test_a_records_push_and_fetch_that_never_answer_end_after_veri_git_network_timeout_as_no_answer_on_one_stderr_line(
        tmp_path, monkeypatch, capsys, fake_processes, run_records):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_GIT_NETWORK_TIMEOUT", "5")
    fake = fake_processes.answers({
        "git rev-parse --abbrev-ref HEAD": (0, "tdd/7-records\n", ""),
        "git hash-object": (0, "b" * 40 + "\n", ""),
        "git mktree": (0, "c" * 40 + "\n", ""),
        "git commit-tree": (0, "d" * 40 + "\n", ""),
        "git remote get-url origin": (0, "https://example.invalid/r.git\n", ""),
        "git push": HANGS,
        "git fetch": HANGS,
    })
    _kill_reaches(monkeypatch, fake)

    run_records.after_push()
    pushed = capsys.readouterr().err.splitlines()
    read = run_records.read("7", "events.jsonl", str(tmp_path))
    fetched = capsys.readouterr().err.splitlines()

    assert (len(pushed), "VERI_GIT_NETWORK_TIMEOUT" in "".join(pushed), read, len(fetched),
            "VERI_GIT_NETWORK_TIMEOUT" in "".join(fetched)) == (1, True, None, 1, True)
