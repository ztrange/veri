"""In-process cases for veri/cover_outcome.py, the module cover-outcome.sh is a shim over."""
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
def cover_outcome():
    return importlib.import_module("veri.cover_outcome")


def run(monkeypatch, capsys, cover_outcome, report, argv):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(report.encode()), newline="\n"))
    code = cover_outcome.main(argv)
    return (code, *capsys.readouterr())


def test_main_returns_each_exit_code_inside_0_to_3_with_its_stdout_and_stderr_ignoring_arguments(monkeypatch, capsys, cover_outcome):
    caught = "COVERED: yes\nCAUGHT_BY: widget.test.sh: a stubbed widget stays blue"
    results = {
        "yes": run(monkeypatch, capsys, cover_outcome, caught, []),
        "yes --bogus": run(monkeypatch, capsys, cover_outcome, caught, ["--bogus"]),
        "no": run(monkeypatch, capsys, cover_outcome, "COVERED: no\n", []),
        "none": run(monkeypatch, capsys, cover_outcome, "MUTATION: flip the colour\n", []),
        "type-only": run(monkeypatch, capsys, cover_outcome, "COVERED: type-only\nPROOF: npx tsc --noEmit\n", []),
    }

    assert results == {
        "yes": (0, "widget.test.sh: a stubbed widget stays blue\n", ""),
        "yes --bogus": (0, "widget.test.sh: a stubbed widget stays blue\n", ""),
        "no": (1, "", ""),
        "none": (2, "", "cover-outcome: no COVERED: line found\n"),
        "type-only": (3, "type-only: npx tsc --noEmit\n", ""),
    }
    assert all(code in range(4) for code, _, _ in results.values())


def test_main_reads_its_report_through_report_read_and_answers_each_covered_branch_the_contract_cases_leave_open(monkeypatch, capsys, cover_outcome):
    no_line = (2, "", "cover-outcome: no COVERED: line found\n")
    reports = {
        "yes without CAUGHT_BY": "COVERED: yes\n",
        "yes with PROOF": "COVERED: yes\nCAUGHT_BY: widget.test.sh: blue\nPROOF: npx tsc --noEmit\n",
        "Yes": "COVERED: Yes\nCAUGHT_BY: widget.test.sh: blue\n",
        "YES": "COVERED: YES\nCAUGHT_BY: widget.test.sh: blue\n",
        "yes with a trailing space": "COVERED: yes \nCAUGHT_BY: widget.test.sh: blue\n",
        "maybe": "COVERED: maybe\n",
        "empty": "COVERED: \n",
        "no with CAUGHT_BY and PROOF": "COVERED: no\nCAUGHT_BY: widget.test.sh: blue\nPROOF: npx tsc --noEmit\n",
        "no then yes": "COVERED: no\nCAUGHT_BY: widget.test.sh: blue\nCOVERED: yes\n",
        "yes with a carriage return": "COVERED: yes\r\nCAUGHT_BY: widget.test.sh: blue\n",
        "unterminated no": "MUTATION: flip the colour\nCOVERED: no",
    }
    results = {name: run(monkeypatch, capsys, cover_outcome, report, []) for name, report in reports.items()}

    assert results == {
        "yes without CAUGHT_BY": (0, "\n", ""),
        "yes with PROOF": (0, "widget.test.sh: blue\n", ""),
        "Yes": no_line,
        "YES": no_line,
        "yes with a trailing space": no_line,
        "maybe": no_line,
        "empty": no_line,
        "no with CAUGHT_BY and PROOF": (1, "", ""),
        "no then yes": (0, "widget.test.sh: blue\n", ""),
        "yes with a carriage return": no_line,
        "unterminated no": (1, "", ""),
    }


def test_main_answers_each_proof_branch_of_unreachable_and_type_only(monkeypatch, capsys, cover_outcome):
    def without(kind):
        return (2, "", "cover-outcome: COVERED: %s without a PROOF: line\n" % kind)

    reports = {
        "unreachable without PROOF": "COVERED: unreachable\n",
        "type-only without PROOF": "COVERED: type-only\n",
        "empty PROOF": "COVERED: type-only\nPROOF: \n",
        "PROOF:NONE with no space": "COVERED: type-only\nPROOF:NONE\n",
        "PROOF: NONE": "COVERED: type-only\nPROOF: NONE\n",
        "PROOF: none": "COVERED: type-only\nPROOF: none\n",
        "PROOF: NONE with a trailing space": "COVERED: type-only\nPROOF: NONE \n",
        "PROOF: NONE — no caller": "COVERED: type-only\nPROOF: NONE — no caller\n",
        "unreachable with PROOF": "COVERED: unreachable\nPROOF: no caller reaches the branch\n",
    }
    results = {name: run(monkeypatch, capsys, cover_outcome, report, []) for name, report in reports.items()}

    assert results == {
        "unreachable without PROOF": without("unreachable"),
        "type-only without PROOF": without("type-only"),
        "empty PROOF": without("type-only"),
        "PROOF:NONE with no space": without("type-only"),
        "PROOF: NONE": without("type-only"),
        "PROOF: none": (3, "type-only: none\n", ""),
        "PROOF: NONE with a trailing space": (3, "type-only: NONE \n", ""),
        "PROOF: NONE — no caller": (3, "type-only: NONE — no caller\n", ""),
        "unreachable with PROOF": (3, "unreachable: no caller reaches the branch\n", ""),
    }


def test_main_passes_a_byte_that_is_not_utf_8_through_unchanged_from_caught_by_and_from_proof(monkeypatch, capsysbinary, cover_outcome):
    def run_bytes(report):
        monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(report), encoding="utf-8", newline="\n"))
        code = cover_outcome.main([])
        return (code, *capsysbinary.readouterr())

    results = {
        "CAUGHT_BY": run_bytes(b"COVERED: yes\nCAUGHT_BY: widget\xff.test.sh\n"),
        "PROOF": run_bytes(b"COVERED: type-only\nPROOF: npx tsc \xff--noEmit\n"),
    }

    assert results == {
        "CAUGHT_BY": (0, b"widget\xff.test.sh\n", b""),
        "PROOF": (3, b"type-only: npx tsc \xff--noEmit\n", b""),
    }
