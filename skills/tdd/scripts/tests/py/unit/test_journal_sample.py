"""veri/journal_sample.py builds the sample journal from veri/event_table.py alone (PRD 030.4, SJ2)."""
import time

from veri import journal_sample


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
