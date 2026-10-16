"""In-process cases for veri/parse_verdict.py, the module parse-verdict.sh is a shim over."""
import importlib
import io
import sys

import pytest


@pytest.fixture
def parse_verdict():
    return importlib.import_module("veri.parse_verdict")


def test_main_returns_2_naming_an_unrecognised_verdict_word_with_nothing_on_stdout(monkeypatch, capsys, parse_verdict):
    monkeypatch.setattr(sys, "stdin", io.StringIO("VERDICT: MAYBE\nREASON: unsure"))

    code = parse_verdict.main([])
    out, err = capsys.readouterr()

    assert (code, out, err) == (2, "", "parse-verdict: unrecognised verdict word 'MAYBE'\n")


def test_main_returns_0_for_pass_and_1_for_reject_printing_the_reason(monkeypatch, capsys, parse_verdict):
    results = []
    for verdict in ("PASS", "REJECT"):
        monkeypatch.setattr(sys, "stdin", io.StringIO(f"VERDICT: {verdict}\nREASON: the step is pinned"))
        code = parse_verdict.main([])
        results.append((code, *capsys.readouterr()))

    assert results == [(0, "the step is pinned\n", ""), (1, "the step is pinned\n", "")]


def test_main_reads_the_last_indented_verdict_line_in_any_case_past_new_step_lines(monkeypatch, capsys, parse_verdict):
    inputs = {
        "last verdict wins": "My first instinct was VERDICT: PASS but on reflection:\nVERDICT: REJECT\nREASON: The failure is an ImportError from a typo, not the missing behavior.",
        "case insensitive": "verdict: pass\nreason: Genuine pass — target test and full suite are green.",
        "indented verdict line": "   VERDICT: PASS\n   REASON: All good.",
        "new_step plain": "I read the diff against the base sha.\nVERDICT: PASS\nREASON: The transform is behaviour-preserving and the suite is green.",
        "new_step proposing": "I read the diff against the base sha.\nNEW_STEP: slugify returns an empty string for input that is all separators\nVERDICT: PASS\nREASON: The transform is behaviour-preserving and the suite is green.",
    }
    results = {}
    for name, text in inputs.items():
        monkeypatch.setattr(sys, "stdin", io.StringIO(text))
        code = parse_verdict.main([])
        results[name] = (code, capsys.readouterr().out)

    assert results == {
        "last verdict wins": (1, "The failure is an ImportError from a typo, not the missing behavior.\n"),
        "case insensitive": (0, "Genuine pass — target test and full suite are green.\n"),
        "indented verdict line": (0, "All good.\n"),
        "new_step plain": (0, "The transform is behaviour-preserving and the suite is green.\n"),
        "new_step proposing": (0, "The transform is behaviour-preserving and the suite is green.\n"),
    }


def test_main_reads_a_multiline_or_inline_reason_and_drops_a_closing_fence(monkeypatch, capsys, parse_verdict):
    inputs = {
        "multiline reason": "VERDICT: REJECT\nREASON: Two problems:\n- the test is over-coupled to the implementation\n- it is also far too complex for one criterion",
        "reason inline after verdict": "VERDICT: REJECT — the test never actually runs the code under test",
        "fenced verdict block": "I ran the test myself.\n```\nVERDICT: REJECT\nREASON: The test asserts a constant and never calls slugify().\n```",
        "multiline reason then fence": "VERDICT: REJECT\nREASON: Two problems:\n- vacuous assertion\n- no call to the function\n```",
    }
    results = {}
    for name, text in inputs.items():
        monkeypatch.setattr(sys, "stdin", io.StringIO(text))
        code = parse_verdict.main([])
        results[name] = (code, capsys.readouterr().out)

    assert results == {
        "multiline reason": (1, "Two problems:\n- the test is over-coupled to the implementation\n- it is also far too complex for one criterion\n"),
        "reason inline after verdict": (1, "the test never actually runs the code under test\n"),
        "fenced verdict block": (1, "The test asserts a constant and never calls slugify().\n"),
        "multiline reason then fence": (1, "Two problems:\n- vacuous assertion\n- no call to the function\n"),
    }


def test_main_ignores_arguments_and_reads_only_a_line_starting_with_a_whitespace_delimited_verdict(monkeypatch, capsys, parse_verdict):
    inputs = {
        "arguments ignored": (["extra", "args"], "VERDICT: PASS\nREASON: ok\n"),
        "empty stdin": ([], ""),
        "last line without newline": ([], "VERDICT: REJECT\nREASON: no newline at the end"),
        "pass alone": ([], "VERDICT: PASS"),
        "verdict mid-line": ([], "the answer is VERDICT: PASS"),
        "word with a full stop": ([], "VERDICT: PASS."),
        "word joined to a dash": ([], "VERDICT: PASS—reason"),
        "bare verdict": ([], "VERDICT:"),
    }
    results = {}
    for name, (argv, text) in inputs.items():
        monkeypatch.setattr(sys, "stdin", io.StringIO(text))
        code = parse_verdict.main(argv)
        results[name] = (code, *capsys.readouterr())

    no_verdict = "parse-verdict: no VERDICT: line found\n"
    assert results == {
        "arguments ignored": (0, "ok\n", ""),
        "empty stdin": (2, "", no_verdict),
        "last line without newline": (1, "no newline at the end\n", ""),
        "pass alone": (0, "\n", ""),
        "verdict mid-line": (2, "", no_verdict),
        "word with a full stop": (2, "", "parse-verdict: unrecognised verdict word 'PASS.'\n"),
        "word joined to a dash": (2, "", "parse-verdict: unrecognised verdict word 'PASS—REASON'\n"),
        "bare verdict": (2, "", "parse-verdict: unrecognised verdict word ''\n"),
    }


def test_main_strips_reason_labels_inline_separators_and_one_closing_fence_with_ascii_whitespace_only(monkeypatch, capsys, parse_verdict):
    inputs = {
        "reason label stripped from the first line only": "VERDICT: REJECT\nREASON: first\nREASON: second",
        "lowercase indented reason label": "VERDICT: PASS\n  reason: ok",
        "following lines beat the inline text": "VERDICT: REJECT — inline\nfollowing",
        "inline used when following lines are blank": "VERDICT: REJECT — inline\n   \n\t",
        "inline used after an empty reason label": "VERDICT: REJECT : inline\nREASON:   ",
        "each separator stripped once in order": "VERDICT: REJECT —–-: x",
        "colon before dash strips only the colon": "VERDICT: REJECT :- x",
        "em dash stripped at most once": "VERDICT: REJECT ——x",
        "hyphen stripped at most once": "VERDICT: REJECT - -x",
        "only the last fence dropped": "VERDICT: REJECT\nREASON: a\n```\nb\n~~~",
        "two closing fences drop one": "VERDICT: REJECT\nREASON: a\n```\n  ```  ",
        "fence with text kept": "VERDICT: PASS\nREASON: a\n``` x",
        "no-break space not trimmed": "VERDICT: PASS\nREASON:  kept ",
        "file separator not trimmed": "VERDICT: PASS\nREASON: \x1ckept\x1c",
        "long s not upper-cased": "VERDICT: paſs",
    }
    results = {}
    for name, text in inputs.items():
        monkeypatch.setattr(sys, "stdin", io.StringIO(text))
        code = parse_verdict.main([])
        results[name] = (code, *capsys.readouterr())

    assert results == {
        "reason label stripped from the first line only": (1, "first\nREASON: second\n", ""),
        "lowercase indented reason label": (0, "ok\n", ""),
        "following lines beat the inline text": (1, "following\n", ""),
        "inline used when following lines are blank": (1, "inline\n", ""),
        "inline used after an empty reason label": (1, "inline\n", ""),
        "each separator stripped once in order": (1, "x\n", ""),
        "colon before dash strips only the colon": (1, "- x\n", ""),
        "em dash stripped at most once": (1, "—x\n", ""),
        "hyphen stripped at most once": (1, "-x\n", ""),
        "only the last fence dropped": (1, "a\n```\nb\n", ""),
        "two closing fences drop one": (1, "a\n```\n", ""),
        "fence with text kept": (0, "a\n``` x\n", ""),
        "no-break space not trimmed": (0, " kept \n", ""),
        "file separator not trimmed": (0, "\x1ckept\x1c\n", ""),
        "long s not upper-cased": (2, "", "parse-verdict: unrecognised verdict word 'PAſS'\n"),
    }
