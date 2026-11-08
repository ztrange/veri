"""In-process cases for veri/event_roster.py, the scanner of every event name emitted under skills/."""
import pytest

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


def test_a_name_emitted_by_a_push_branch_record_call_is_in_the_roster(tmp_path, monkeypatch):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "mod.py").write_text('push_branch.record("lone-push-event", "k=1")\n')
    monkeypatch.setattr(event_roster, "SKILLS", tmp_path)

    assert set(event_roster.emitted_events()) == {"lone-push-event"}


def test_a_name_emitted_through_a_cause_constant_is_in_the_roster(tmp_path, monkeypatch):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "mod.py").write_text('CAUSE = "lone-cause-event"\n')
    monkeypatch.setattr(event_roster, "SKILLS", tmp_path)

    assert set(event_roster.emitted_events()) == {"lone-cause-event"}


def test_a_cause_constant_on_a_later_line_is_in_the_roster_but_one_not_starting_a_line_is_not(tmp_path, monkeypatch):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "mod.py").write_text(
        'import os\n\nX_CAUSE = "prefixed-event"\n    CAUSE = "indented-event"\nCAUSE = "later-line-event"\n'
    )
    monkeypatch.setattr(event_roster, "SKILLS", tmp_path)

    assert set(event_roster.emitted_events()) == {"later-line-event"}


def test_a_name_emitted_by_a_bare_mark_call_is_in_the_roster(tmp_path, monkeypatch):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "mod.py").write_text('    mark(role, env, "lone-bare-mark-event", "k=1")\n')
    monkeypatch.setattr(event_roster, "SKILLS", tmp_path)

    assert set(event_roster.emitted_events()) == {"lone-bare-mark-event"}


def test_a_bare_mark_call_whose_second_argument_is_a_ledger_state_is_not_in_the_roster(tmp_path, monkeypatch):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "mod.py").write_text('    mark(phase, "owed")\n')
    monkeypatch.setattr(event_roster, "SKILLS", tmp_path)

    assert set(event_roster.emitted_events()) == set()


def test_a_name_emitted_by_a_bare_mark_call_with_the_role_first_is_in_the_roster(tmp_path, monkeypatch):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "mod.py").write_text('    marked = mark(role, "lone-role-first-event", "cause=x")\n')
    monkeypatch.setattr(event_roster, "SKILLS", tmp_path)

    assert set(event_roster.emitted_events()) == {"lone-role-first-event"}


def test_a_name_emitted_by_a_bare_record_call_is_in_the_roster(tmp_path, monkeypatch):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "mod.py").write_text('    return record("lone-bare-record-event", "k=1")\n')
    monkeypatch.setattr(event_roster, "SKILLS", tmp_path)

    assert set(event_roster.emitted_events()) == {"lone-bare-record-event"}


@pytest.mark.tree_audit("runs the roster guard, which reads every file under skills/")
def test_the_journal_guard_goes_red_on_an_event_left_only_in_another_rows_prose(tmp_path, monkeypatch):
    import test_journal_event_roster as guard

    rows = guard.JOURNAL.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [line for line in rows if not line.startswith("| `resume` |")]
    assert len(kept) == len(rows) - 1
    copy = tmp_path / "JOURNAL.md"
    copy.write_text("".join(kept), encoding="utf-8")
    monkeypatch.setattr(guard, "JOURNAL", copy)

    with pytest.raises(AssertionError) as red:
        guard.test_every_event_emitted_under_skills_is_documented_in_journal_md()
    assert "resume (emitted in" in str(red.value)
