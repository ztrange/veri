"""A step's `mutation-record: <path>` directive leaves the record deleted, unrestored (#3352)."""
from veri import supervise


def test_3352_a_step_naming_a_record_as_a_directive_leaves_it_deleted_and_emits_no_restored_event(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    record = ".tdd/issue-3352-mutations.md"
    monkeypatch.setenv("VERI_STEP", f"Retire the stale record mutation-record: {record} for good")
    events = []
    monkeypatch.setattr(supervise, "mark", lambda role, env, *fields: events.append(fields))

    supervise.restore_mutation_records({record: b"mutation: a\n"}, "role", {}, "develop-red-1")

    assert ((tmp_path / record).exists(), events) == (False, [])


def test_3352_a_step_only_quoting_the_marker_in_backticks_still_restores_the_record_and_emits_the_event(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    record = ".tdd/issue-3352-mutations.md"
    monkeypatch.setenv("VERI_STEP", f"Explain the `mutation-record: {record} ` marker in the docs")
    events = []
    monkeypatch.setattr(supervise, "mark", lambda role, env, *fields: events.append(fields))

    supervise.restore_mutation_records({record: b"mutation: a\n"}, "role", {}, "develop-red-1")

    assert ((tmp_path / record).exists(), events) == (
        True,
        [("mutation-record-restored", "name=develop-red-1", f"file={record}")],
    )


def test_3352_a_step_only_quoting_the_marker_in_double_quotes_still_restores_the_record_and_emits_the_event(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    record = ".tdd/issue-3352-mutations.md"
    monkeypatch.setenv("VERI_STEP", f'Explain the "mutation-record: {record} " marker in the docs')
    events = []
    monkeypatch.setattr(supervise, "mark", lambda role, env, *fields: events.append(fields))

    supervise.restore_mutation_records({record: b"mutation: a\n"}, "role", {}, "develop-red-1")

    assert ((tmp_path / record).exists(), events) == (
        True,
        [("mutation-record-restored", "name=develop-red-1", f"file={record}")],
    )
