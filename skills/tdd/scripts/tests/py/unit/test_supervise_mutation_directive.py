"""A step's `mutation-record: <path>` directive leaves the record deleted, unrestored (#3352)."""
from veri import supervise


def delete_record_under_step(tmp_path, monkeypatch, record, step):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", step)
    events = []
    monkeypatch.setattr(supervise, "mark", lambda role, env, *fields: events.append(fields))
    supervise.restore_mutation_records({record: b"mutation: a\n"}, "role", {}, "develop-red-1")
    return events


def test_3352_a_step_naming_a_record_as_a_directive_leaves_it_deleted_and_emits_no_restored_event(tmp_path, monkeypatch):
    record = ".tdd/issue-3352-mutations.md"
    events = delete_record_under_step(tmp_path, monkeypatch, record, f"Retire the stale record mutation-record: {record} for good")

    assert ((tmp_path / record).exists(), events) == (False, [])


def test_3352_a_step_only_quoting_the_marker_in_backticks_still_restores_the_record_and_emits_the_event(tmp_path, monkeypatch):
    record = ".tdd/issue-3352-mutations.md"
    events = delete_record_under_step(tmp_path, monkeypatch, record, f"Explain the `mutation-record: {record} ` marker in the docs")

    assert ((tmp_path / record).exists(), events) == (
        True,
        [("mutation-record-restored", "name=develop-red-1", f"file={record}")],
    )


def test_3352_a_step_only_quoting_the_marker_in_double_quotes_still_restores_the_record_and_emits_the_event(tmp_path, monkeypatch):
    record = ".tdd/issue-3352-mutations.md"
    events = delete_record_under_step(tmp_path, monkeypatch, record, f'Explain the "mutation-record: {record} " marker in the docs')

    assert ((tmp_path / record).exists(), events) == (
        True,
        [("mutation-record-restored", "name=develop-red-1", f"file={record}")],
    )


def test_3352_a_step_only_quoting_the_marker_in_single_quotes_still_restores_the_record_and_emits_the_event(tmp_path, monkeypatch):
    record = ".tdd/issue-3352-mutations.md"
    events = delete_record_under_step(tmp_path, monkeypatch, record, f"Explain the 'mutation-record: {record} ' marker in the docs")

    assert ((tmp_path / record).exists(), events) == (
        True,
        [("mutation-record-restored", "name=develop-red-1", f"file={record}")],
    )


def test_3352_apostrophes_in_prose_are_not_quotes_so_a_real_directive_between_them_still_counts(tmp_path, monkeypatch):
    record = ".tdd/issue-3352-mutations.md"
    step = f"the leaf shouldn't delete mutation-record: {record} , it isn't a directive's job"
    events = delete_record_under_step(tmp_path, monkeypatch, record, step)

    assert ((tmp_path / record).exists(), events) == (False, [])


def test_3395_a_directive_followed_by_a_comma_names_the_same_record_so_it_stays_deleted_and_emits_no_restored_event(tmp_path, monkeypatch):
    record = ".tdd/issue-3395-mutations.md"
    events = delete_record_under_step(tmp_path, monkeypatch, record, f"Retire the stale record mutation-record: {record}, for good")

    assert ((tmp_path / record).exists(), events) == (False, [])


def test_3395_a_directive_followed_by_a_period_semicolon_or_parenthesis_exempts_its_record_while_an_unnamed_one_is_restored(tmp_path, monkeypatch):
    names = {c: f".tdd/issue-3395-{c}-mutations.md" for c in "pscn"}
    step = (
        f"Retire mutation-record: {names['p']}. Then mutation-record: {names['s']}; "
        f"and (mutation-record: {names['c']});next"
    )
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", step)
    events = []
    monkeypatch.setattr(supervise, "mark", lambda role, env, *fields: events.append(fields))
    before = {path: b"mutation: a\n" for path in names.values()}
    supervise.restore_mutation_records(before, "role", {}, "develop-red-1")

    assert ({k: (tmp_path / v).exists() for k, v in names.items()}, events) == (
        {"p": False, "s": False, "c": False, "n": True},
        [("mutation-record-restored", "name=develop-red-1", f"file={names['n']}")],
    )


def test_3395_a_directive_with_no_trailing_punctuation_still_exempts_its_record_while_an_unnamed_one_is_restored(tmp_path, monkeypatch):
    named, unnamed = ".tdd/issue-3395-named-mutations.md", ".tdd/issue-3395-unnamed-mutations.md"
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", f"Retire the stale record mutation-record: {named} for good")
    events = []
    monkeypatch.setattr(supervise, "mark", lambda role, env, *fields: events.append(fields))
    supervise.restore_mutation_records({named: b"mutation: a\n", unnamed: b"mutation: a\n"}, "role", {}, "develop-red-1")

    assert ((tmp_path / named).exists(), (tmp_path / unnamed).exists(), events) == (
        False,
        True,
        [("mutation-record-restored", "name=develop-red-1", f"file={unnamed}")],
    )


def test_3395_a_changed_record_that_no_marker_names_is_restored_and_emits_the_event_while_a_named_one_keeps_its_edit(tmp_path, monkeypatch):
    named, unnamed = ".tdd/issue-3395-kept-mutations.md", ".tdd/issue-3395-edited-mutations.md"
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / named).write_bytes(b"mutation: edited\n")
    (tmp_path / unnamed).write_bytes(b"mutation: edited\n")
    monkeypatch.setenv("VERI_STEP", f"Rework mutation-record: {named}, only")
    events = []
    monkeypatch.setattr(supervise, "mark", lambda role, env, *fields: events.append(fields))
    supervise.restore_mutation_records({named: b"mutation: a\n", unnamed: b"mutation: a\n"}, "role", {}, "develop-red-1")

    assert ((tmp_path / named).read_bytes(), (tmp_path / unnamed).read_bytes(), events) == (
        b"mutation: edited\n",
        b"mutation: a\n",
        [("mutation-record-restored", "name=develop-red-1", f"file={unnamed}")],
    )
