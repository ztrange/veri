"""In-process cases for veri/seam_outcome.py, the module seam-outcome.sh is a shim over."""
import importlib
import io
import sys

import pytest


@pytest.fixture
def seam_outcome():
    return importlib.import_module("veri.seam_outcome")


def run(monkeypatch, capsys, seam_outcome, report, argv=()):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(report.encode()), encoding="utf-8", newline="\n"))
    code = seam_outcome.main(list(argv))
    return (code, *capsys.readouterr())


def test_main_answers_reaches_yes_with_its_seam_0_reaches_no_with_its_reason_1_and_an_unreadable_report_2_4106(
        monkeypatch, capsys, seam_outcome):
    yes = "narration\nSEAM: bin/parse --strict\nREACHES: yes\nPROOF: bin/parse calls parse() in src/parse.py\n"
    no = "SEAM: parse_all()\nREACHES: no\nPROOF: parse_all() never calls parse(); only an edit would reach it\n"
    results = {
        "yes": run(monkeypatch, capsys, seam_outcome, yes),
        "no": run(monkeypatch, capsys, seam_outcome, no),
        "neither": run(monkeypatch, capsys, seam_outcome, "SEAM: bin/parse\nPROOF: read it\n"),
        "yes without a seam": run(monkeypatch, capsys, seam_outcome, "REACHES: yes\nPROOF: it does\n"),
        "yes with seam NONE": run(monkeypatch, capsys, seam_outcome, "SEAM: NONE\nREACHES: yes\n"),
        "unknown answer": run(monkeypatch, capsys, seam_outcome, "SEAM: bin/parse\nREACHES: maybe\n"),
    }

    assert {name: (code, out) for name, (code, out, _) in results.items()} == {
        "yes": (0, "bin/parse --strict\n"),
        "no": (1, "parse_all() never calls parse(); only an edit would reach it\n"),
        "neither": (2, ""),
        "yes without a seam": (2, ""),
        "yes with seam NONE": (2, ""),
        "unknown answer": (2, ""),
    }
    assert all(err.startswith("seam-outcome: ") for code, _, err in results.values() if code == 2)


def test_an_argument_is_refused_with_the_usage_and_exit_2_4106(monkeypatch, capsys, seam_outcome):
    code, out, err = run(monkeypatch, capsys, seam_outcome, "SEAM: x\nREACHES: yes\n", ["--bogus"])

    assert (code, out) == (2, "")
    assert "'--bogus'" in err and seam_outcome.USAGE in err
