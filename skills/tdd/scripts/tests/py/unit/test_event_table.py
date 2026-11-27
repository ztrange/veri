"""veri/event_table.py is the one table of every event veri emits and its keys (PRD 030.1)."""
import ast

import pytest

from conftest import SCRIPTS

TABLE = SCRIPTS / "veri" / "event_table.py"


def test_the_table_module_imports_no_other_veri_module():
    tree = ast.parse(TABLE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    siblings = sorted(name for name in imported if name == "veri" or (SCRIPTS / "veri" / f"{name}.py").exists())

    assert not siblings, f"veri/event_table.py imports veri modules {siblings}; it must be readable alone"


def test_the_table_declares_the_events_journal_md_lacked_with_the_keys_their_writers_pass():
    from veri import event_table

    written = {"grading": {"unit", "verdict", "failing", "cost_usd", "id", "effort"},
               "prose-owed-waived": {"unit", "step"}, "suite-flake": {"at", "files"}, "skill-edit-no-author": {"unit"}}

    assert {event: set(event_table.keys(event)) for event in written} == written
    assert event_table.required("suite-flake") == {"files"}


def test_4018_the_table_declares_ci_rerun_and_ci_flake_each_with_a_sha_head_a_whole_run_and_the_files():
    from veri import event_table

    declared = {event: [(key, event_table.format(event, key)) for key in event_table.keys(event)]
                for event in ("ci-rerun", "ci-flake")}

    assert declared == {event: [("head", ("sha", False)), ("run", ("whole", False)), ("files", ("text", False))]
                        for event in ("ci-rerun", "ci-flake")}


def test_journal_md_lists_exactly_the_events_and_keys_the_table_declares():
    from veri import event_table, journal_schema

    page = (SCRIPTS.parent / "JOURNAL.md").read_text(encoding="utf-8")
    drift = []
    for event in sorted(set(event_table.EVENTS) | journal_schema.kinds(page)):
        if event not in event_table.EVENTS:
            drift.append(f"{event}: a JOURNAL.md row, not in veri/event_table.py's EVENTS")
            continue
        documented = journal_schema.fields(page, event)
        if documented is None:
            drift.append(f"{event}: in veri/event_table.py's EVENTS, no JOURNAL.md row")
            continue
        drift += [f"{event} key {key}: in veri/event_table.py's EVENTS, not in its JOURNAL.md row"
                  for key in event_table.keys(event) if key not in documented]
        drift += [f"{event} key {key}: in its JOURNAL.md row, not in veri/event_table.py's EVENTS"
                  for key in documented if key not in event_table.keys(event)]

    assert not drift, "skills/tdd/JOURNAL.md and veri/event_table.py differ:\n" + "\n".join(drift)


def test_every_key_of_every_event_and_every_string_common_key_has_a_format_from_the_closed_set():
    from veri import event_table

    declared = [(event, key) for event in event_table.EVENTS for key in event_table.keys(event)]
    declared += [(None, key) for key in event_table.CONTEXT_KEYS]
    problems = []
    for event, key in declared:
        form = event_table.format(event, key)[0]
        if not (form in event_table.FORMATS or (isinstance(form, tuple) and form)):
            problems.append(f"event {event or '(every line)'} key {key}: format {form!r} is none of"
                            f" {', '.join(event_table.FORMATS)} or a (value|…) list; give it one in the line"
                            f"  {event_table.declaring(event, None)}")

    assert not problems, "veri/event_table.py keys without a format from its closed set:\n" + "\n".join(problems)


def test_an_empty_value_is_invalid_for_a_key_not_marked_empty_allowed_whatever_its_format_and_valid_for_one_so_marked():
    from veri import event_table

    declared = [(event, key) for event in event_table.EVENTS for key in event_table.keys(event)]
    declared += [(None, key) for key in event_table.CONTEXT_KEYS]
    marked = {(event, key) for event, key in declared if event_table.format(event, key)[1]}
    unmarked_formats = {str(event_table.format(event, key)[0]) for event, key in set(declared) - marked}

    assert {"text", "whole", "url", "sha", "json", "decimal"} <= unmarked_formats and ("merged", "tag") in marked
    assert [(event, key) for event, key in declared if event_table.valid(event, key, "") != ((event, key) in marked)] == []


def keys_cell(event_table, event, keys):
    """The Keys cell of a JOURNAL.md row (or the run-context formats line) stating the table's formats for `keys`."""
    def stated(form, empty):
        words = "one of " + ", ".join(form) if isinstance(form, tuple) else str(form)
        return words + (", or empty" if empty else "")
    return "; ".join(f"`{key}` {stated(*event_table.format(event, key))}" for key in keys)


def test_journal_md_states_the_format_veri_event_table_declares_for_every_key():
    from veri import event_table, journal_schema

    page = (SCRIPTS.parent / "JOURNAL.md").read_text(encoding="utf-8")
    drift = []
    for event in event_table.EVENTS:
        stated = journal_schema.formats(page, event) or {}
        drift += [f"{event} key {key}: JOURNAL.md states {stated.get(key)!r}, veri/event_table.py declares"
                  f" {event_table.format(event, key)!r}; make the row's Keys cell  {keys_cell(event_table, event, event_table.keys(event))}"
                  for key in event_table.keys(event) if stated.get(key) != event_table.format(event, key)]
    context = journal_schema.context_formats(page) or {}
    drift += [f"(every line) key {key}: JOURNAL.md states {context.get(key)!r}, veri/event_table.py declares"
              f" {event_table.format(None, key)!r}; make the line  {journal_schema.CONTEXT_LEAD}"
              f" {keys_cell(event_table, None, event_table.CONTEXT_KEYS)}."
              for key in event_table.CONTEXT_KEYS if context.get(key) != event_table.format(None, key)]

    assert not drift, "skills/tdd/JOURNAL.md states formats veri/event_table.py does not declare:\n" + "\n".join(drift)


def test_no_list_in_journal_md_ends_with_an_ellipsis():
    from veri import journal_schema

    page = (SCRIPTS.parent / "JOURNAL.md").read_text(encoding="utf-8")
    open_ended = []
    for row in journal_schema.ROW.finditer(page):
        keys = journal_schema.fields(page, row.group(1)) or ()
        text = row.group(2) + "|" + row.group(3)
        for at in [i for i, char in enumerate(text) if char == "…"]:
            named = [name for name in journal_schema.NAME.findall(text[:at]) if name in keys]
            open_ended.append(f"{row.group(1)} key {named[-1] if named else '(none)'}: its list ends with …; write out"
                              " every value, as veri/event_table.py declares them")

    assert not open_ended, "skills/tdd/JOURNAL.md lists that end with …:\n" + "\n".join(open_ended)


def test_bail_s_cause_values_are_classify_bail_s_categories_and_its_classification_values_process_and_system():
    from veri import classify_bail, event_table

    causes = event_table.format("bail", "cause")[0]
    line = event_table.declaring("bail", None)
    differ = [f"bail cause {cause}: in veri/event_table.py's bail line, not in classify_bail.CATEGORIES; drop it from"
              f" the line  {line}" for cause in causes if cause not in classify_bail.CATEGORIES]
    differ += [f"bail cause {cause}: in classify_bail.CATEGORIES, not in veri/event_table.py's bail line; add it to the"
               f" line  {line}" for cause in classify_bail.CATEGORIES if cause not in causes]

    assert not differ, "bail's cause values and classify_bail.CATEGORIES differ:\n" + "\n".join(differ)
    assert sorted(event_table.format("bail", "classification")[0]) == ["process", "system"], line


@pytest.mark.tree_audit("reads every .sh and .md file under skills/ for event.sh call sites")
def test_every_literal_event_and_key_of_an_event_sh_call_under_skills_is_declared_in_the_table():
    from veri import event_table

    from event_roster import event_sh_call_sites

    sites = event_sh_call_sites()
    assert any(keys for _, _, keys in sites), "no event.sh call site with a key found under skills/"
    gaps = [f"{where}: event {event!r} is not in veri/event_table.py; add  {event_table.declaring(event, None)}"
            for where, event, _ in sites if event not in event_table.EVENTS]
    gaps += [f"{where}: event {event!r} key {key!r} is not in veri/event_table.py; make its line"
             f"  {event_table.declaring(event, key)}"
             for where, event, keys in sites if event in event_table.EVENTS
             for key in keys if key not in event_table.keys(event)]

    assert not gaps, "event.sh call sites under skills/ the table does not declare:\n" + "\n".join(gaps)


def test_4712_the_table_declares_deviated_with_rule_step_and_a_non_empty_reason_required_and_allows_outcome_deviate():
    from veri import event_table

    assert (set(event_table.keys("deviated")), event_table.required("deviated")) == ({"rule", "step", "reason"},) * 2
    assert (event_table.valid("deviated", "reason", ""), event_table.valid("deviated", "rule", "graded-edit")) == (False, True)
    assert event_table.valid("adjudicated", "outcome", "deviate")


def test_4730_the_table_allows_cause_tests_frozen_refused_on_adjudicated():
    from veri import event_table

    assert event_table.valid("adjudicated", "cause", "tests-frozen-refused")


def test_4730_the_table_allows_rule_tests_frozen_on_deviated():
    from veri import event_table

    assert event_table.valid("deviated", "rule", "tests-frozen")


def test_4730_the_table_still_refuses_a_rule_no_waivable_rule_names_on_deviated():
    from veri import event_table

    assert not event_table.valid("deviated", "rule", "nope")
