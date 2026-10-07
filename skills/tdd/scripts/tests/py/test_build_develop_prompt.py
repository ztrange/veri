"""In-process cases for veri/build_develop_prompt.py, the module build-develop-prompt.sh is a shim over."""
import importlib
import importlib.util
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

PHASES = b"red|green|refactor|cover|transform|diff|structural|predicate|revise|reconcile|exhausted|over-budget|rebase"
USAGE = b"build-develop-prompt.sh: usage: " + PHASES + b" <issue-spec-file> <step-text> <test-cmd> ...\n"


@pytest.fixture
def build_develop_prompt():
    return importlib.import_module("veri.build_develop_prompt")


def test_main_refuses_no_argument_an_unknown_phase_a_short_count_an_unknown_revise_phase_and_a_missing_fast_cmd_with_exit_2_and_its_message_then_the_usage_line(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")
    s, r = str(spec), str(reason)
    results = {}
    for argv in ([], ["bogus", s, "s", "c"], ["green", s, "s", "c"],
                 ["revise", "bogus", s, "s", "c", r], ["diff", s, "s", "c"],
                 ["revise", "diff", s, "s", "c", r]):
        code = build_develop_prompt.main(argv)
        results[tuple(argv)] = (code, *capsysbinary.readouterr())

    assert results == {
        (): (2, b"", USAGE),
        ("bogus", s, "s", "c"): (
            2, b"", b"build-develop-prompt.sh: unknown phase 'bogus' (want " + PHASES + b")\n" + USAGE),
        ("green", s, "s", "c"): (2, b"", b"build-develop-prompt: green needs 7 arguments, got 4\n" + USAGE),
        ("revise", "bogus", s, "s", "c", r): (
            2, b"", b"build-develop-prompt.sh: unknown phase to revise 'bogus' (want red|green|refactor|diff)\n"
            + USAGE),
        ("diff", s, "s", "c"): (2, b"", b"build-develop-prompt: diff needs 5 arguments, got 4\n" + USAGE),
        ("revise", "diff", s, "s", "c", r): (2, b"", b"build-develop-prompt: missing <fast-cmd>\n" + USAGE),
    }


def test_main_refuses_in_the_check_order_each_missing_argument_by_its_own_name_and_ignores_arguments_past_the_count(
        tmp_path, capsysbinary, build_develop_prompt):
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")
    s, r = str(spec), str(reason)

    def refused(message):
        return (2, b"", b"build-develop-prompt" + message + b"\n" + USAGE)

    expected = {
        ("", s, "s", "c"): refused(b".sh: unknown phase '' (want " + PHASES + b")"),
        ("revise", "bogus", "a", "b", "c"): refused(b": revise needs 6 arguments, got 5"),
        ("red", s, "s"): refused(b": red needs 4 arguments, got 3"),
        ("cover", s, "s"): refused(b": cover needs 4 arguments, got 3"),
        ("transform", s, "s"): refused(b": transform needs 4 arguments, got 3"),
        ("diff", s, "s", "c"): refused(b": diff needs 5 arguments, got 4"),
        ("refactor", s, "s", "c"): refused(b": refactor needs 5 arguments, got 4"),
        ("structural", s, "s", "c"): refused(b": structural needs 5 arguments, got 4"),
        ("predicate", s, "s", "c"): refused(b": predicate needs 5 arguments, got 4"),
        ("exhausted", s, "s", "c"): refused(b": exhausted needs 5 arguments, got 4"),
        ("revise", "red", s, "s", "c"): refused(b": revise needs 6 arguments, got 5"),
        ("reconcile", s, "s", "c", "b"): refused(b": reconcile needs 6 arguments, got 5"),
        ("over-budget", s, "s", "c", "1"): refused(b": over-budget needs 6 arguments, got 5"),
        ("green", s, "s", "c", "tp", "tt"): refused(b": green needs 7 arguments, got 6"),
        ("rebase", s, "s", "c", "a", "b"): refused(b": rebase needs 7 arguments, got 6"),
        ("revise", "", s, "s", "c", r): refused(b": missing <phase> being revised"),
        ("red", "", "", ""): refused(b": missing <issue-spec-file>"),
        ("red", s, "", ""): refused(b": missing <step-text>"),
        ("red", s, "s", ""): refused(b": missing <test-cmd>"),
        ("revise", "red", "", "s", "c", r): refused(b": missing <issue-spec-file>"),
        ("revise", "diff", s, "s", "", "", ""): refused(b": missing <test-cmd>"),
        ("green", s, "s", "c", "", "", ""): refused(b": missing <test-path>"),
        ("green", s, "s", "c", "tp", "", ""): refused(b": missing <target-test>"),
        ("green", s, "s", "c", "tp", "tt", ""): refused(b": missing <fast-cmd>"),
        ("diff", s, "s", "c", ""): refused(b": missing <fast-cmd>"),
        ("structural", s, "s", "c", ""): refused(b": missing <issue-touched-files>"),
        ("predicate", s, "s", "c", ""): refused(b": missing <issue-touched-files>"),
        ("refactor", s, "s", "c", ""): refused(b": missing <touched-files>"),
        ("revise", "red", s, "s", "c", ""): refused(b": missing <reason-file>"),
        ("exhausted", s, "s", "c", ""): refused(b": missing <reason-file>"),
        ("revise", "diff", s, "s", "c", "", ""): refused(b": missing <reason-file>"),
        ("revise", "diff", s, "s", "c", r, ""): refused(b": missing <fast-cmd>"),
        ("reconcile", s, "s", "c", "", ""): refused(b": missing <branch>"),
        ("reconcile", s, "s", "c", "b", ""): refused(b": missing <remote-sha>"),
        ("rebase", s, "s", "c", "", "", ""): refused(b": missing <onto-sha>"),
        ("rebase", s, "s", "c", "a", "", ""): refused(b": missing <pre-rebase-sha>"),
        ("rebase", s, "s", "c", "a", "b", ""): refused(b": missing <conflicting-files>"),
        ("over-budget", s, "s", "c", "", ""): refused(b": missing <spent>"),
        ("over-budget", s, "s", "c", "1", ""): refused(b": missing <budget>"),
    }
    results = {}
    for argv in expected:
        code = build_develop_prompt.main(list(argv))
        results[argv] = (code, *capsysbinary.readouterr())

    complete = [("red", s, "s", "c"), ("cover", s, "s", "c"), ("transform", s, "s", "c"),
                ("diff", s, "s", "c", "f"), ("refactor", s, "s", "c", "t"), ("structural", s, "s", "c", "t"),
                ("predicate", s, "s", "c", "t"), ("exhausted", s, "s", "c", r),
                ("revise", "red", s, "s", "c", r), ("revise", "green", s, "s", "c", r),
                ("revise", "refactor", s, "s", "c", r), ("revise", "diff", s, "s", "c", r, "f"),
                ("reconcile", s, "s", "c", "b", "sha"), ("over-budget", s, "s", "c", "1", "2"),
                ("green", s, "s", "c", "tp", "tt", "f"), ("rebase", s, "s", "c", "a", "b", "x")]
    ignored = {}
    for argv in complete:
        answers = []
        for extra in ((), ("",), ("past", "the", "count")):
            code = build_develop_prompt.main(list(argv + extra))
            answers.append((code, *capsysbinary.readouterr()))
        ignored[argv] = (answers[0][0], answers[1] == answers[0], answers[2] == answers[0])

    assert results == expected
    assert ignored == {argv: (0, True, True) for argv in complete}
    assert type(build_develop_prompt.PHASES) is tuple
    assert "|".join(build_develop_prompt.PHASES).encode() == PHASES
    assert build_develop_prompt.REVISE_PHASES == ("red", "green", "refactor", "diff")


def test_main_refuses_a_spent_then_a_budget_that_is_not_a_whole_string_non_negative_decimal_before_any_file_is_read_and_a_revised_phase_with_a_trailing_newline(
        tmp_path, capsysbinary):
    module = tmp_path / "scripts" / "veri" / "build_develop_prompt.py"
    module.parent.mkdir(parents=True)
    module.write_bytes((SCRIPTS / "veri" / "build_develop_prompt.py").read_bytes())
    loader = importlib.util.spec_from_file_location("build_develop_prompt_without_prompts", module)
    no_prompts = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(no_prompts)
    s = str(tmp_path / "no-such-spec.md")
    r = str(tmp_path / "no-such-reason.md")

    def refused(message):
        return (2, b"", message.encode() + b"\n" + USAGE)

    def not_decimal(name, value):
        return refused(f"build-develop-prompt: <{name}> '{value}' is not a non-negative decimal number")

    expected = {}
    for bad in ("-1", "3,", "qwixnum", "1e3", ".5", "3.47 because", "3\n", "3.47\n", "٣", "3.٤"):
        expected[("over-budget", s, "s", "c", bad, "2.50")] = not_decimal("spent", bad)
        expected[("over-budget", s, "s", "c", "3.47", bad)] = not_decimal("budget", bad)
    expected[("over-budget", s, "s", "c", "qwixnum", "zork")] = not_decimal("spent", "qwixnum")
    expected[("revise", "red\n", s, "s", "c", r)] = refused(
        "build-develop-prompt.sh: unknown phase to revise 'red\n' (want red|green|refactor|diff)")
    results = {}
    for argv in expected:
        code = no_prompts.main(list(argv))
        results[argv] = (code, *capsysbinary.readouterr())

    assert results == expected
