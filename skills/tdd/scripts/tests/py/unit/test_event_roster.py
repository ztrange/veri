"""In-process cases for veri/event_roster.py, the scanner of every event name emitted under skills/."""
from veri import event_roster


def test_a_name_emitted_by_an_event_sh_call_site_is_in_the_roster(tmp_path, monkeypatch):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "run.sh").write_text('event.sh lone-fixture-event key=1\n')
    monkeypatch.setattr(event_roster, "SKILLS", tmp_path)

    assert set(event_roster.emitted_events()) == {"lone-fixture-event"}
