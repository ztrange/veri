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


def test_current_prints_the_first_pending_step_with_the_mark_cut_else_the_first_open_step_or_diff_checked_step(
        monkeypatch, capsysbinary, ledger_steps):
    ledgers = {
        "pending": (
            "- [x] a cog exists ⟦criterion 1⟧\n"
            "- [ ] the cog turns ⟦replaces-case⟧ ⟦criterion 6⟧\n"
            "- [x] the cog is oiled ⟦criterion 2⟧ ⟂ refactor pending\n"
            "- [x] the cog is greased ⟦criterion 3⟧ ⟂ refactor pending\n"
        ),
        "replaces-case": (
            "- [x] a cog exists ⟦criterion 1⟧\n"
            "- [ ] the PR body lists the cogs ⟦human-owed⟧ ⟦criterion 2⟧\n"
            "- [ ] make test is green ⟦full-suite⟧ ⟦criterion 2⟧\n"
            "- [ ] the cog turns ⟦replaces-case⟧ ⟦criterion 6⟧\n"
            "- [ ] the cog stops ⟦criterion 7⟧\n"
        ),
        "diff-checked": (
            "- [ ] the PR body lists the cogs ⟦human-owed⟧ ⟦criterion 2⟧\n"
            "- [ ] the cog is unchanged ⟦diff-checked⟧ ⟦criterion 3⟧\n"
            "- [ ] the cog stops ⟦criterion 7⟧\n"
        ),
    }
    results = {}
    for name, ledger in ledgers.items():
        fake_stdin(monkeypatch, ledger.encode())
        code = ledger_steps.main(["current"])
        results[name] = (code, *capsysbinary.readouterr())

    assert results == {
        "pending": (0, "the cog is oiled ⟦criterion 2⟧\n".encode(), b""),
        "replaces-case": (0, "the cog turns ⟦replaces-case⟧ ⟦criterion 6⟧\n".encode(), b""),
        "diff-checked": (0, "the cog is unchanged ⟦diff-checked⟧ ⟦criterion 3⟧\n".encode(), b""),
    }


def test_last_done_prints_the_last_done_step_x_or_X_with_the_mark_cut_an_empty_line_for_empty_text_else_exits_3(
        monkeypatch, capsysbinary, ledger_steps):
    ledgers = {
        "pending": (
            "- [x] a cog exists ⟦criterion 1⟧\n"
            "- [X] the cog is oiled ⟦criterion 2⟧ ⟂ refactor pending\n"
            "- [ ] the cog stops ⟦criterion 3⟧\n"
        ),
        "lowercase x": (
            "- [X] a cog exists ⟦criterion 1⟧\n"
            "- [x] the cog turns ⟦criterion 2⟧\n"
            "- [ ] the cog stops ⟦criterion 3⟧\n"
        ),
        "empty text": (
            "- [x] a cog exists ⟦criterion 1⟧\n"
            "- [x]\n"
            "- [ ] the cog stops ⟦criterion 2⟧\n"
        ),
        "none done": (
            "- [ ] a cog exists ⟦criterion 1⟧\n"
            "- [ ] make test is green ⟦full-suite⟧ ⟦criterion 2⟧\n"
        ),
    }
    results = {}
    for name, ledger in ledgers.items():
        fake_stdin(monkeypatch, ledger.encode())
        code = ledger_steps.main(["last-done"])
        results[name] = (code, *capsysbinary.readouterr())

    assert results == {
        "pending": (0, "the cog is oiled ⟦criterion 2⟧\n".encode(), b""),
        "lowercase x": (0, "the cog turns ⟦criterion 2⟧\n".encode(), b""),
        "empty text": (0, b"\n", b""),
        "none done": (3, b"", b""),
    }


def test_criterion_prints_the_kth_step_line_of_every_acceptance_criteria_section_else_exits_3(
        monkeypatch, capsysbinary, ledger_steps):
    body = (
        "# Title\n"
        "- [ ] not a criterion\n"
        "## Acceptance criteriaX\n"
        "- [ ] c1\n"
        "### a subsection\n"
        "  - [ ] c2\n"
        "* [ ] not a step\n"
        "## Other\n"
        "- [ ] not a criterion either\n"
        "## Acceptance criteria\n"
        "- [x] c3 ⟂ refactor pending\n"
        "- [ ] c4"
    ).encode()
    results = {}
    for k in ("0", "1", "2", "3", "4", "5"):
        fake_stdin(monkeypatch, body)
        code = ledger_steps.main(["criterion", k])
        results[k] = (code, *capsysbinary.readouterr())

    assert results == {
        "0": (3, b"", b""),
        "1": (0, b"c1\n", b""),
        "2": (0, b"c2\n", b""),
        "3": (0, b"c3\n", b""),
        "4": (0, b"c4\n", b""),
        "5": (3, b"", b""),
    }


def test_criterion_reads_k_as_bash_base_10_64_bit_arithmetic_and_refuses_empty_signed_spaced_or_non_ascii_k(
        monkeypatch, capsysbinary, ledger_steps):
    body = "## Acceptance criteria\n" + "".join(f"- [ ] c{i}\n" for i in range(1, 9))
    ks = ("08", "0", "18446744073709551617", "99999999999999999999", "", "-1", " 1", "١")
    results = {}
    for k in ks:
        fake_stdin(monkeypatch, body.encode())
        code = ledger_steps.main(["criterion", k])
        results[k] = (code, *capsysbinary.readouterr())

    assert results == {
        "08": (0, b"c8\n", b""),
        "0": (3, b"", b""),
        "18446744073709551617": (0, b"c1\n", b""),
        "99999999999999999999": (3, b"", b""),
        "": (2, b"", USAGE),
        "-1": (2, b"", USAGE),
        " 1": (2, b"", USAGE),
        "١": (2, b"", USAGE),
    }
