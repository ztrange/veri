"""veri/journal_sample.py builds the sample journal from veri/event_table.py alone (PRD 030.4, SJ2 to SJ4)."""
import json
import pathlib
import time

from veri import event_table, journal_sample

SAMPLE = pathlib.Path(__file__).resolve().parents[6] / "fixtures" / "journal" / "sample.jsonl"
REGENERATE = "python3 skills/tdd/scripts/veri/journal_sample.py > fixtures/journal/sample.jsonl"


def test_two_runs_with_a_different_clock_environment_and_current_directory_print_the_same_bytes(
        run_cli, monkeypatch, tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    monkeypatch.setattr(time, "time", lambda: 1000.0)
    first = run_cli(journal_sample, [], env={"VERI_ISSUE": "11", "VERI_ACTOR": "developer", "VERI_HOME": str(tmp_path)},
                    cwd=tmp_path / "a")
    monkeypatch.setattr(time, "time", lambda: 9999999.0)
    second = run_cli(journal_sample, [], env={"VERI_ISSUE": "42", "VERI_ACTOR": "verifier", "VERI_PHASE": "green",
                                              "VERI_AWAKE_CLOCK": "/bin/false"}, cwd=tmp_path / "b")

    assert first[0] == 0 and first[1]
    assert first == second


def test_the_committed_sample_is_what_journal_sample_py_builds():
    committed = SAMPLE.read_bytes().splitlines()
    built = journal_sample.sample().splitlines()
    first = next((n for n, (ours, theirs) in enumerate(zip(committed, built, strict=False), 1) if ours != theirs),
                 min(len(committed), len(built)) + 1 if len(committed) != len(built) else None)

    assert first is None, (f"fixtures/journal/sample.jsonl line {first} differs from what journal_sample.py builds:"
                           f"\n  committed: {committed[first - 1] if first <= len(committed) else '(no line)'}"
                           f"\n  built:     {built[first - 1] if first <= len(built) else '(no line)'}"
                           f"\nregenerate it:  {REGENERATE}")


def test_the_sample_holds_a_line_for_every_declared_event_and_none_for_an_undeclared_one():
    sampled = [json.loads(line).get("event") for line in SAMPLE.read_text(encoding="utf-8").splitlines() if line.strip()]
    gaps = [f"event {name}: declared in veri/event_table.py, no line in fixtures/journal/sample.jsonl; regenerate it:"
            f"  {REGENERATE}" for name in event_table.EVENTS if name not in sampled]
    gaps += [f"event {name}: a line in fixtures/journal/sample.jsonl, not declared in veri/event_table.py; regenerate it:"
             f"  {REGENERATE}" for name in sampled if name not in event_table.EVENTS]

    assert not gaps, "fixtures/journal/sample.jsonl and veri/event_table.py's events differ:\n" + "\n".join(gaps)
