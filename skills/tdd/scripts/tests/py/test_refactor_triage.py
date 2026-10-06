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
