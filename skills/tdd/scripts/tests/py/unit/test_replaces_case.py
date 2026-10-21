"""In-process cases for veri/replaces_case.py, the one parser of a replaces-case step's named cases."""
import importlib


def test_parse_1521_yields_exactly_the_names_and_suite_each_replaces_case_step_carries():
    replaces_case = importlib.import_module("veri.replaces_case")
    mark = " ⟦replaces-case⟧ ⟦criterion 1⟧"
    suite = "skills/tdd/scripts/tests/supervise.test.sh"
    apostrophe = "#472: supervise.sh's header names the watchdog's clock source and why it pauses"
    in_name = "#512: case 50's slept-through leaf stays suspended and reports status 0 with secs in the awake range"
    comma_a = "#1126 a writer in a conductor's group ends 143, never 141 of SIGPIPE"
    comma_b = "#1246 a writer in a conductor's group that writes after the SIGTERM, ends 143, never 141"
    fixtures = [
        (f"- [x] header check: replaces '{apostrophe}' in {suite}{mark}", [apostrophe], suite),
        (f"- [x] the 'migration' case isn't cut: replaces '{in_name}' in {suite}{mark}", [in_name], suite),
        (f"- [x] `cut_whole` call, the 'old' idiom: replaces '{comma_a}', '{comma_b}' in {suite}{mark}",
         [comma_a, comma_b], suite),
        (f"- [x] one clause: replaces '{apostrophe}' in {suite}, run-leaf.sh leaving slice 7's list{mark}",
         [apostrophe], suite),
        (f"- [x] double quotes: replaces \"{apostrophe}\", \"{in_name}\" in {suite}{mark}",
         [apostrophe, in_name], suite),
        (f"- [x] backticks: replaces `{apostrophe}`, `{in_name}` in {suite}{mark}",
         [apostrophe, in_name], suite),
        (f"- [x] deleted suite: replaces '{in_name}' in skills/tdd/scripts/tests/deleted-suite.test.sh{mark}",
         [in_name], "skills/tdd/scripts/tests/deleted-suite.test.sh"),
    ]

    parsed = [replaces_case.parse(step) for step, _, _ in fixtures]

    assert parsed == [(names, expected_suite) for _, names, expected_suite in fixtures]


def test_parse_1954_returns_none_for_a_name_left_holding_a_quote_then_a_separator():
    replaces_case = importlib.import_module("veri.replaces_case")
    step = "- [x] a mixed clause: replaces 'a', b' in t/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"

    assert replaces_case.parse(step) is None


def test_parse_1603_returns_none_for_a_step_naming_the_mark_without_a_replaces_clause():
    replaces_case = importlib.import_module("veri.replaces_case")
    step = "- [x] the Red prompt for replaces-case steps names the mark ⟦replaces-case⟧ ⟦criterion 5⟧"

    assert replaces_case.parse(step) is None


def test_parse_1603_does_not_raise_for_a_quoted_replaces_clause_with_no_suite_after_it():
    replaces_case = importlib.import_module("veri.replaces_case")
    step = "- [x] the old guard replaces 'a case that is gone' ⟦replaces-case⟧ ⟦criterion 6⟧"

    replaces_case.parse(step)
