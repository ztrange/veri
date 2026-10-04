"""In-process cases for veri/ledger_steps.py, the module ledger-steps.sh is a shim over."""
import importlib
import io
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

USAGE = b"usage: ledger-steps.sh [current|last-done|criterion <k>]\n"


@pytest.fixture
def ledger_steps():
    return importlib.import_module("veri.ledger_steps")


def fake_stdin(monkeypatch, data):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(data)))


def test_main_refuses_with_2_and_the_usage_line_exits_3_for_no_current_step_and_prints_every_record_with_none(
        monkeypatch, capsysbinary, ledger_steps):
    ledger = (
        "# Plan\n"
        "- [x] a cog exists ⟦criterion 1⟧\n"
        "- [ ] the PR body lists the cogs ⟦human-owed⟧ ⟦criterion 2⟧\n"
        "- [ ] make test is green ⟦full-suite⟧ ⟦criterion 2⟧\n"
    ).encode()
    calls = {
        "bogus": ["bogus"],
        "criterion with no k": ["criterion"],
        "criterion two": ["criterion", "two"],
        "criterion 1 newline": ["criterion", "1\n"],
        "current": ["current"],
        "no argument": [],
    }
    results = {}
    for name, argv in calls.items():
        fake_stdin(monkeypatch, ledger)
        code = ledger_steps.main(argv)
        results[name] = (code, *capsysbinary.readouterr())

    assert all(code in range(4) for code, _, _ in results.values())
    assert results == {
        "bogus": (2, b"", USAGE),
        "criterion with no k": (2, b"", USAGE),
        "criterion two": (2, b"", USAGE),
        "criterion 1 newline": (2, b"", USAGE),
        "current": (3, b"", b""),
        "no argument": (0, (
            "1\tdone\tstep\t0\t0\t1\ta cog exists ⟦criterion 1⟧\n"
            "2\topen\thuman-owed\t0\t0\t2\tthe PR body lists the cogs ⟦human-owed⟧ ⟦criterion 2⟧\n"
            "3\topen\tfull-suite\t0\t0\t2\tmake test is green ⟦full-suite⟧ ⟦criterion 2⟧\n"
        ).encode(), b""),
    }
