"""In-process cases for veri/refactor_triage.py, the module refactor-triage.sh is a shim over."""
import importlib
import io
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def refactor_triage():
    return importlib.import_module("veri.refactor_triage")


def fake_stdin(monkeypatch, data):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(data)))


def test_main_prints_structural_candidates_exits_3_with_none_left_and_refuses_a_report_with_exit_2_and_its_diagnostic(
        monkeypatch, capsysbinary, refactor_triage):
    results = {}
    for report in (
            b"CANDIDATES: structural | x\n",
            b"CANDIDATES: cosmetic | x\n",
            b"CANDIDATES: none\n",
            b"",
            b"CANDIDATES: cosmic | x\n"):
        fake_stdin(monkeypatch, report)
        code = refactor_triage.main([])
        results[report] = (code, *capsysbinary.readouterr())

    assert all(code in range(4) for code, _, _ in results.values())
    assert results == {
        b"CANDIDATES: structural | x\n": (0, b"x\n", b""),
        b"CANDIDATES: cosmetic | x\n": (3, b"", b""),
        b"CANDIDATES: none\n": (3, b"", b""),
        b"": (2, b"", b"refactor-triage: the report has no CANDIDATES: line\n"),
        b"CANDIDATES: cosmic | x\n": (
            2, b"",
            b"refactor-triage: candidate line has no class, or one that is neither structural nor cosmetic: "
            b"CANDIDATES: cosmic | x\n"),
    }


def test_main_reads_a_test_only_candidate_as_its_own_class_exiting_3_alone_printing_only_the_structural_beside_it_and_refusing_a_capitalised_class(
        monkeypatch, capsysbinary, refactor_triage):
    results = {}
    for report in (
            b'RESULT: applied "inline the single-use variable", suite green\n'
            b"CANDIDATES: test-only | fold the three mktemp fixtures into one helper\n",
            b"CANDIDATES: test-only | x\nCANDIDATES: structural | y\n",
            b"CANDIDATES: Test-only | x\n"):
        fake_stdin(monkeypatch, report)
        code = refactor_triage.main([])
        results[report] = (code, capsysbinary.readouterr().out)

    assert results == {
        b'RESULT: applied "inline the single-use variable", suite green\n'
        b"CANDIDATES: test-only | fold the three mktemp fixtures into one helper\n": (3, b""),
        b"CANDIDATES: test-only | x\nCANDIDATES: structural | y\n": (0, b"y\n"),
        b"CANDIDATES: Test-only | x\n": (2, b""),
    }


def test_main_reads_an_out_of_scope_candidate_and_never_prints_it_exiting_3_alone_printing_only_the_structural_beside_it_in_either_order_and_refusing_a_capitalised_class(
        monkeypatch, capsysbinary, refactor_triage):
    results = {}
    for report in (
            b"CANDIDATES: out-of-scope | x\n",
            b"CANDIDATES: out-of-scope | x\nCANDIDATES: structural | y\n",
            b"CANDIDATES: structural | y\nCANDIDATES: out-of-scope | x\n",
            b"CANDIDATES: Out-of-scope | x\n"):
        fake_stdin(monkeypatch, report)
        code = refactor_triage.main([])
        results[report] = (code, *capsysbinary.readouterr())

    assert results == {
        b"CANDIDATES: out-of-scope | x\n": (3, b"", b""),
        b"CANDIDATES: out-of-scope | x\nCANDIDATES: structural | y\n": (0, b"y\n", b""),
        b"CANDIDATES: structural | y\nCANDIDATES: out-of-scope | x\n": (0, b"y\n", b""),
        b"CANDIDATES: Out-of-scope | x\n": (
            2, b"",
            b"refactor-triage: candidate line has no class, or one that is neither structural nor cosmetic: "
            b"CANDIDATES: Out-of-scope | x\n"),
    }
