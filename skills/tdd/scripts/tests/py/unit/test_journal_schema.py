"""In-process cases for veri/journal_schema.py: what JOURNAL.md's table documents, and what writers pass."""
from pathlib import Path

from veri import journal_schema

TABLE = (
    "# Journal\n\nThe `prose-only` event is mentioned here but has no row.\n\n"
    "| Event | Keys | Meaning |\n|---|---|---|\n"
    "| `alpha` | `one`, `two` | Two keys. |\n"
    "| `beta` | — | No keys. |\n"
    "| `gamma` | `need`, `maybe`, `gone` | `maybe` is optional: present only sometimes. The `gone` key is absent otherwise. |\n"
)


def test_kinds_are_the_first_column_of_the_table_rows_only():
    assert journal_schema.kinds(TABLE) == {"alpha", "beta", "gamma"}


def test_fields_are_the_backticked_names_of_the_keys_column_in_order():
    assert journal_schema.fields(TABLE, "alpha") == ("one", "two")


def test_a_row_with_a_dash_documents_no_fields():
    assert journal_schema.fields(TABLE, "beta") == ()


def test_a_kind_without_a_row_has_no_documented_fields():
    assert journal_schema.fields(TABLE, "prose-only") is None


def test_a_key_the_meaning_calls_optional_or_absent_is_optional():
    assert journal_schema.optional(TABLE, "gamma") == {"maybe", "gone"}
    assert journal_schema.optional(TABLE, "alpha") == set()


def test_the_real_journal_documents_bail_with_its_optional_suites():
    text = (Path(journal_schema.__file__).resolve().parents[2] / "JOURNAL.md").read_text(encoding="utf-8")

    assert journal_schema.fields(text, "bail") == ("cause", "classification", "suites", "failed")
    assert journal_schema.optional(text, "bail") == {"classification", "suites", "failed"}
    assert "usage" in journal_schema.kinds(text)


def test_a_writer_call_gives_its_literal_kind_and_field_names():
    source = 'event.mark(".", ctx, "plan", ["steps=%d" % n, f"x={y}", "k=" + v, "c=1", other])\n'

    assert journal_schema.writer_calls(source) == [(1, "plan", ["steps", "x", "k", "c"])]


def test_an_event_line_call_gives_the_kind_and_fields_of_its_argument_list_bytes_or_str():
    source = ('f.write(event.line([b"step-added", b"colour=red", b"n=%d" % n], ctx, 1, b"2"))\n'
              'event.line(["plan", "steps=" + n], ctx, ts, awake)\n')

    assert journal_schema.writer_calls(source) == [(1, "step-added", ["colour", "n"]), (2, "plan", ["steps"])]


def test_every_writer_call_shape_is_seen():
    source = (
        'event.append(".", {}, "a", ["f1=1"])\n'
        'verify.mark(role, "b", "f2=1", "f3=2")\n'
        'supervise.mark(role, env, "c", f"f4={x}")\n'
        'push_branch.record("d", "f5=1")\n'
    )

    assert [(kind, names) for _, kind, names in journal_schema.writer_calls(source)] == [
        ("a", ["f1"]), ("b", ["f2", "f3"]), ("c", ["f4"]), ("d", ["f5"])]


def test_a_bare_mark_is_a_writer_only_inside_the_module_that_defines_it():
    assert journal_schema.writer_calls('mark(role, env, "launch", "name=x")\n') == []
    assert journal_schema.writer_calls('mark(role, env, "launch", "name=x")\n', "supervise") == [(1, "launch", ["name"])]
    assert journal_schema.writer_calls('mark(role, "relaunch", "cause=y")\n', "verify") == [(1, "relaunch", ["cause"])]


def test_a_conditional_or_starred_field_list_is_read_through():
    source = 'event.mark(d, c, "exit", ["a=1", *(["detail=" + x] if x else [])])\n'

    assert journal_schema.writer_calls(source) == [(1, "exit", ["a", "detail"])]


def test_a_computed_kind_is_reported_without_a_kind_and_a_variable_field_list_without_names():
    source = 'event.mark(d, c, event_name, pairs)\nevent.mark(d, c, "usage", pairs)\n'

    assert journal_schema.writer_calls(source) == [(1, None, []), (2, "usage", [])]


def test_other_calls_named_mark_or_append_are_not_writers():
    source = 'rows.append(1)\nledger.mark(x, "y", "z=1")\nevent.context(env)\n'

    assert journal_schema.writer_calls(source) == []


def test_a_kind_named_by_a_module_level_string_constant_is_resolved():
    source = 'CAUSE = "preflight-refused"\n\ndef go():\n    event.mark(run, {}, CAUSE, ["check=x"])\n'

    assert journal_schema.writer_calls(source) == [(4, "preflight-refused", ["check"])]


def test_a_name_assigned_twice_or_inside_a_function_is_not_resolved():
    source = 'K = "a"\nK = "b"\ndef go():\n    J = "c"\n    event.mark(r, {}, K, [])\n    event.mark(r, {}, J, [])\n'

    assert journal_schema.writer_calls(source) == [(5, None, []), (6, None, [])]


def test_4741_the_real_journal_names_no_retired_bail_cause_or_event():
    text = (Path(journal_schema.__file__).resolve().parents[2] / "JOURNAL.md").read_text(encoding="utf-8")

    assert [name for name in ("repin-failed", "not-checked", "mutation-record-restored", "pin-retired")
            if name in text] == []
