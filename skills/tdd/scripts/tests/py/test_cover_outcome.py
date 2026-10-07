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
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(report.encode())))
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
