"""In-process cases for veri/red_divergence.py, the module red-divergence.sh is a shim over."""
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
def red_divergence():
    return importlib.import_module("veri.red_divergence")


def run(monkeypatch, capsys, red_divergence, report, argv):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(report.encode()), newline="\n"))
    code = red_divergence.main(argv)
    return (code, *capsys.readouterr())


def test_main_reads_its_report_through_report_read_and_returns_each_exit_code_inside_0_to_3_with_its_stdout_and_stderr_ignoring_arguments(monkeypatch, capsys, red_divergence):
    diverged = (
        "PREDICTED_FAILURE: slugify: command not found\n"
        "FAIL_OUTPUT: FAIL - slugify lowercases the title (want exit 0, got 127)\n"
        "PREDICTION: DIVERGED\n"
        "PREDICTION_NOTE: the suite died on a missing helper before it reached the assertion"
    )
    matched = "FAIL_OUTPUT: FAIL - slugify lowercases the title\nPREDICTION: MATCHED"
    results = {
        "diverged": run(monkeypatch, capsys, red_divergence, diverged, []),
        "matched": run(monkeypatch, capsys, red_divergence, matched, []),
        "matched --bogus": run(monkeypatch, capsys, red_divergence, matched, ["--bogus"]),
        "no PREDICTION": run(monkeypatch, capsys, red_divergence, "FAIL_OUTPUT: FAIL - slugify lowercases the title\n", []),
    }

    assert results == {
        "diverged": (
            0,
            "The red leaf's prediction diverged from the failure it saw, so the test is the suspect.\n"
            "\n"
            "PREDICTED_FAILURE: slugify: command not found\n"
            "FAIL_OUTPUT: FAIL - slugify lowercases the title (want exit 0, got 127)\n"
            "PREDICTION_NOTE: the suite died on a missing helper before it reached the assertion\n",
            "",
        ),
        "matched": (3, "", ""),
        "matched --bogus": (3, "", ""),
        "no PREDICTION": (2, "", ""),
    }
    assert all(code in range(4) for code, _, _ in results.values())
