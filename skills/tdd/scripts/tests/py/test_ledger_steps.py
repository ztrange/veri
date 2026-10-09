"""In-process cases for veri/ledger_steps.py, the module ledger-steps.sh is a shim over."""
import importlib
import io
import sys

import pytest

USAGE = b"usage: ledger-steps.sh [current|last-done|current-or-last-done|criterion <k>]\n"


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


def test_current_or_last_done_prints_currents_answer_else_last_dones_else_exits_3_with_nothing(
        monkeypatch, capsysbinary, ledger_steps):
    ledgers = {
        "open": (
            "- [x] a cog exists ⟦criterion 1⟧\n"
            "- [ ] the cog turns ⟦criterion 2⟧\n"
        ),
        "all ticked": (
            "- [x] a cog exists ⟦criterion 1⟧\n"
            "- [x] the cog turns ⟦criterion 2⟧\n"
        ),
        "no step": "# Plan\n\nprose\n",
    }
    results = {}
    for name, ledger in ledgers.items():
        for verb in ("current", "last-done", "current-or-last-done"):
            fake_stdin(monkeypatch, ledger.encode())
            code = ledger_steps.main([verb])
            results[name, verb] = (code, *capsysbinary.readouterr())

    assert results["open", "current-or-last-done"] == results["open", "current"]
    assert results["all ticked", "current-or-last-done"] == results["all ticked", "last-done"]
    assert {name: results[name, "current-or-last-done"] for name in ledgers} == {
        "open": (0, "the cog turns ⟦criterion 2⟧\n".encode(), b""),
        "all ticked": (0, "the cog turns ⟦criterion 2⟧\n".encode(), b""),
        "no step": (3, b"", b""),
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


def test_main_reads_the_verb_from_argv_0_alone_an_empty_verb_prints_every_record_and_empty_stdin_prints_nothing(
        monkeypatch, capsysbinary, ledger_steps):
    ledger = (
        "- [x] a cog exists ⟦criterion 1⟧\n"
        "- [ ] the cog turns ⟦criterion 2⟧\n"
    ).encode()
    body = b"## Acceptance criteria\n- [ ] c1\n- [ ] c2\n"
    calls = {
        "current": (ledger, ["current"]),
        "current extra": (ledger, ["current", "extra"]),
        "criterion 1": (body, ["criterion", "1"]),
        "criterion 1 extra": (body, ["criterion", "1", "extra"]),
        "no argument": (ledger, []),
        "empty verb": (ledger, [""]),
        "empty stdin": (b"", []),
    }
    results = {}
    for name, (stdin, argv) in calls.items():
        fake_stdin(monkeypatch, stdin)
        code = ledger_steps.main(argv)
        results[name] = (code, *capsysbinary.readouterr())

    every_record = (
        "1\tdone\tstep\t0\t0\t1\ta cog exists ⟦criterion 1⟧\n"
        "2\topen\tstep\t0\t0\t2\tthe cog turns ⟦criterion 2⟧\n"
    ).encode()
    assert results == {
        "current": (0, "the cog turns ⟦criterion 2⟧\n".encode(), b""),
        "current extra": (0, "the cog turns ⟦criterion 2⟧\n".encode(), b""),
        "criterion 1": (0, b"c1\n", b""),
        "criterion 1 extra": (0, b"c1\n", b""),
        "no argument": (0, every_record, b""),
        "empty verb": (0, every_record, b""),
        "empty stdin": (0, b"", b""),
    }


def test_main_passes_bytes_through_as_bash_does_drops_nul_and_keeps_the_cr_of_a_crlf_document(
        monkeypatch, capsysbinary, ledger_steps):
    calls = {
        "xff byte": (b"- [ ] a \xff cog\n", ["current"]),
        "nul byte": (b"- [ ] a c\x00og\n", ["current"]),
        "crlf criterion": (b"## Acceptance criteria\r\n- [ ] c1\r\n- [ ] c2\r\n", ["criterion", "1"]),
        "crlf pending": (
            "- [x] the cog is oiled ⟂ refactor pending\r\n- [ ] the cog stops\r\n".encode(), []),
    }
    results = {}
    for name, (stdin, argv) in calls.items():
        fake_stdin(monkeypatch, stdin)
        code = ledger_steps.main(argv)
        results[name] = (code, *capsysbinary.readouterr())

    assert results == {
        "xff byte": (0, b"a \xff cog\n", b""),
        "nul byte": (0, b"a cog\n", b""),
        "crlf criterion": (0, b"c1\r\n", b""),
        "crlf pending": (0, (
            "1\tdone\tstep\t0\t0\t\tthe cog is oiled ⟂ refactor pending\r\n"
            "2\topen\tstep\t0\t0\t\tthe cog stops\r\n"
        ).encode(), b""),
    }


class UnreadableStdin(io.RawIOBase):
    def readable(self):
        return True

    def readinto(self, buffer):
        raise IsADirectoryError(21, "Is a directory")


def test_main_raises_rather_than_returning_when_stdout_is_closed_or_stdin_cannot_be_read(
        monkeypatch, ledger_steps):
    fake_stdin(monkeypatch, "- [ ] the cog turns ⟦criterion 1⟧\n".encode())
    monkeypatch.setattr(sys, "stdout", None)
    with pytest.raises(Exception):
        ledger_steps.main([])

    monkeypatch.undo()
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BufferedReader(UnreadableStdin())))
    with pytest.raises(Exception):
        ledger_steps.main(["current"])


def test_main_prints_every_record_of_a_replaces_case_ledger_and_current_hands_out_its_open_step_and_criterion_08_past_the_count_exits_3(
        monkeypatch, capsysbinary, ledger_steps):
    step = ('replace skills/tdd/scripts/tests/status.test.sh case "status prints the plan" '
            'with a pytest case ⟦replaces-case⟧ ⟦criterion 6⟧')
    marks = (
        "# Plan for #42\n\nprose\n\n"
        "- [x] add lowercasing ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [ ] strip edge hyphens ⟦added⟧ ⟦criterion 2⟧\n"
    ).encode()
    replaces = f"# Plan for #42\n\n- [x] add lowercasing ⟦criterion 5⟧\n- [ ] {step}\n".encode()
    body = (
        "## What is happening\n\n- [ ] a checkbox in the prose\n\n"
        "## Acceptance criteria\n\n- [ ] first criterion\n"
        '- [ ] second criterion carries `$S` and "quotes"\n\n'
        "## Notes\n\n- [ ] a checkbox after the section\n"
    ).encode()
    calls = {
        "marks": (marks, []),
        "replaces-case records": (replaces, []),
        "replaces-case current": (replaces, ["current"]),
        "criterion 08 past the count": (body, ["criterion", "08"]),
    }
    results = {}
    for name, (stdin, argv) in calls.items():
        fake_stdin(monkeypatch, stdin)
        code = ledger_steps.main(argv)
        results[name] = (code, *capsysbinary.readouterr())

    assert results == {
        "marks": (0, (
            "1\tdone\tstep\t1\t0\t1\tadd lowercasing ⟦criterion 1⟧\n"
            "2\topen\tstep\t0\t1\t2\tstrip edge hyphens ⟦added⟧ ⟦criterion 2⟧\n"
        ).encode(), b""),
        "replaces-case records": (0, (
            "1\tdone\tstep\t0\t0\t5\tadd lowercasing ⟦criterion 5⟧\n"
            f"2\topen\tstep\t0\t0\t6\t{step}\n"
        ).encode(), b""),
        "replaces-case current": (0, f"{step}\n".encode(), b""),
        "criterion 08 past the count": (3, b"", b""),
    }
