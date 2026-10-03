"""In-process cases for veri/parse_verdict.py, the module parse-verdict.sh is a shim over."""
import importlib
import io
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


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
