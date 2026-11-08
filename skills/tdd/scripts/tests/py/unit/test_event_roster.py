"""In-process cases for veri/event_roster.py, the scanner of every event name emitted under skills/."""
from veri import event_roster


def test_a_name_emitted_by_an_event_sh_call_site_is_in_the_roster(tmp_path, monkeypatch):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "run.sh").write_text('event.sh lone-fixture-event key=1\n')
    monkeypatch.setattr(event_roster, "SKILLS", tmp_path)

    assert set(event_roster.emitted_events()) == {"lone-fixture-event"}


def test_a_name_emitted_by_an_event_mark_call_is_in_the_roster(tmp_path, monkeypatch):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "mod.py").write_text('event.mark(tdd, event.context(env), "lone-mark-event", ["k=1"])\n')
    monkeypatch.setattr(event_roster, "SKILLS", tmp_path)

    assert set(event_roster.emitted_events()) == {"lone-mark-event"}


def test_a_name_emitted_by_an_event_mark_call_with_an_empty_first_argument_is_in_the_roster(tmp_path, monkeypatch):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "mod.py").write_text('event.mark("", "lone-empty-first-event", ["k=1"])\n')
    monkeypatch.setattr(event_roster, "SKILLS", tmp_path)

    assert set(event_roster.emitted_events()) == {"lone-empty-first-event"}


def test_a_name_emitted_by_a_verify_mark_call_is_in_the_roster(tmp_path, monkeypatch):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "mod.py").write_text('verify.mark(role, "lone-verify-event", "k=1")\n')
    monkeypatch.setattr(event_roster, "SKILLS", tmp_path)

    assert set(event_roster.emitted_events()) == {"lone-verify-event"}


def test_a_name_emitted_by_a_supervise_mark_call_is_in_the_roster(tmp_path, monkeypatch):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "mod.py").write_text('supervise.mark(role, env, "lone-supervise-event", "k=1")\n')
    monkeypatch.setattr(event_roster, "SKILLS", tmp_path)

    assert set(event_roster.emitted_events()) == {"lone-supervise-event"}
