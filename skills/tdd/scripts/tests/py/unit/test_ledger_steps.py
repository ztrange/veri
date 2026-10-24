"""In-process cases for veri/ledger_steps.py, the module ledger-steps.sh is a shim over."""
import importlib
import io
import sys
import types

import pytest

USAGE = b"usage: ledger-steps.sh [current|last-done|current-or-last-done|next-phase|criterion <k>|has-mark <name>]\n"


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


def test_next_phase_prints_expand_on_an_unmarked_phased_step_migrate_once_expand_is_marked_and_exits_3_with_no_unfinished_phased_step(
        monkeypatch, capsysbinary, ledger_steps):
    phased = "- [ ] rename the slug helper ⟦phases: expand, migrate, contract-a, contract-b⟧ ⟦criterion 1⟧"
    ledgers = {
        "nothing marked": f"# Plan for #42\n\n- [x] add lowercasing\n{phased}\n- [ ] strip edge hyphens\n",
        "expand marked": f"# Plan for #42\n\n- [x] add lowercasing\n{phased} ⟂ expand done\n- [ ] strip edge hyphens\n",
        "no phased step": "# Plan for #42\n\n- [x] add lowercasing\n- [ ] strip edge hyphens\n",
    }
    results = {}
    for name, ledger in ledgers.items():
        fake_stdin(monkeypatch, ledger.encode())
        code = ledger_steps.main(["next-phase"])
        results[name] = (code, *capsysbinary.readouterr())

    assert results == {
        "nothing marked": (0, b"expand\n", b""),
        "expand marked": (0, b"migrate\n", b""),
        "no phased step": (3, b"", b""),
    }


def test_next_phase_answers_contract_b_after_expand_on_a_step_listing_only_expand_and_contract_b(
        monkeypatch, capsysbinary, ledger_steps):
    phased = "- [ ] rename the slug helper ⟦phases: expand, contract-b⟧ ⟦criterion 1⟧"
    ledgers = {
        "nothing marked": f"# Plan for #42\n\n- [x] add lowercasing\n{phased}\n",
        "expand marked": f"# Plan for #42\n\n- [x] add lowercasing\n{phased} ⟂ expand done\n",
    }
    results = {}
    for name, ledger in ledgers.items():
        fake_stdin(monkeypatch, ledger.encode())
        code = ledger_steps.main(["next-phase"])
        results[name] = (code, *capsysbinary.readouterr())

    assert results == {
        "nothing marked": (0, b"expand\n", b""),
        "expand marked": (0, b"contract-b\n", b""),
    }


def test_next_phase_exits_3_with_no_phase_when_the_only_open_phased_step_has_its_contract_owed_1410(
        monkeypatch, capsysbinary, ledger_steps):
    phased = (
        "- [ ] rename the slug helper ⟦phases: expand, migrate, contract-a, contract-b⟧ ⟦criterion 1⟧"
        " ⟂ expand done ⟂ migrate done ⟂ contract-a owed"
    )
    ledger = (
        f"# Plan for #42\n\n- [x] add lowercasing\n{phased}\n\n"
        "## Owed steps\n\n- rename the slug helper: contract-a\n"
    )
    fake_stdin(monkeypatch, ledger.encode())

    code = ledger_steps.main(["next-phase"])

    assert (code, *capsysbinary.readouterr()) == (3, b"", b"")


def test_main_prints_a_usage_line_naming_next_phase_on_a_bad_argument_1385(capsysbinary, ledger_steps):
    code = ledger_steps.main(["bogus"])
    out, err = capsysbinary.readouterr()

    assert (code, out, err.count(b"\n"), err.startswith(b"usage: ledger-steps.sh "), b"next-phase" in err) == (
        2, b"", 1, True, True)


def test_main_reads_a_steps_markers_from_its_trailing_marker_run_not_from_markers_its_prose_quotes_1450(
        monkeypatch, capsysbinary, ledger_steps):
    criterion_quoted = "a step tagged ⟦criterion 2⟧ is refused twice ⟦criterion 1⟧"
    phases_quoted = "explain the ⟦phases: expand⟧ notation ⟦criterion 3⟧"
    ledger = f"# Plan for #42\n\n- [ ] {criterion_quoted}\n- [ ] {phases_quoted}\n".encode()
    results = {}
    for verb in ("", "next-phase"):
        fake_stdin(monkeypatch, ledger)
        code = ledger_steps.main([verb] if verb else [])
        results[verb] = (code, *capsysbinary.readouterr())

    assert results == {
        "": (0, (
            f"1\topen\tstep\t0\t0\t1\t{criterion_quoted}\n"
            f"2\topen\tstep\t0\t0\t3\t{phases_quoted}\n"
        ).encode(), b""),
        "next-phase": (3, b"", b""),
    }


def test_main_reports_an_empty_criterion_for_a_step_whose_prose_quotes_one_and_whose_trailing_run_has_none_1450(
        monkeypatch, capsysbinary, ledger_steps):
    quoted = "a step tagged ⟦criterion 2⟧ is refused twice"
    fake_stdin(monkeypatch, f"# Plan for #42\n\n- [ ] {quoted}\n".encode())
    code = ledger_steps.main([])

    assert (code, *capsysbinary.readouterr()) == (0, f"1\topen\tstep\t0\t0\t\t{quoted}\n".encode(), b"")


def test_main_reports_a_kind_only_from_a_steps_trailing_marker_run_not_from_a_kind_its_prose_quotes_1450(
        monkeypatch, capsysbinary, ledger_steps):
    quoted = "a step tagged ⟦human-owed⟧ ⟦criterion 2⟧ needs a human ⟦criterion 1⟧"
    trailing = "the diff is read by hand ⟦diff-checked⟧ ⟦criterion 3⟧"
    fake_stdin(monkeypatch, f"# Plan for #42\n\n- [ ] {quoted}\n- [ ] {trailing}\n".encode())
    code = ledger_steps.main([])

    assert (code, *capsysbinary.readouterr()) == (0, (
        f"1\topen\tstep\t0\t0\t1\t{quoted}\n"
        f"2\topen\tdiff-checked\t0\t0\t3\t{trailing}\n"
    ).encode(), b"")


def test_has_mark_answers_0_only_for_a_step_whose_trailing_markers_carry_the_mark_not_one_that_quotes_it_1613(
        monkeypatch, capsysbinary, ledger_steps):
    quoting = "- [ ] a step that quotes ⟦ci-repair⟧ in its prose ⟦criterion 1⟧\n"
    repair = "- [ ] fix the red job ⟦ci-repair⟧ ⟦criterion 1⟧\n"
    results = {}
    for name, steps in {"quoting": quoting, "repair": quoting + repair}.items():
        fake_stdin(monkeypatch, f"# Plan for #42\n\n{steps}".encode())
        code = ledger_steps.main(["has-mark", "ci-repair"])
        results[name] = (code, *capsysbinary.readouterr())

    assert results == {"quoting": (3, b"", b""), "repair": (0, b"", b"")}


def test_has_mark_with_no_name_exits_2_with_a_usage_line_listing_has_mark_and_no_traceback_1624(
        monkeypatch, capsysbinary, ledger_steps):
    fake_stdin(monkeypatch, b"# Plan for #42\n\n- [ ] fix the red job \xe2\x9f\xa6ci-repair\xe2\x9f\xa7 \xe2\x9f\xa6criterion 1\xe2\x9f\xa7\n")
    try:
        code = ledger_steps.main(["has-mark"])
    except Exception as exc:
        code = type(exc).__name__
    out, err = capsysbinary.readouterr()

    assert (code, out, err.startswith(b"usage: ledger-steps.sh "), b"has-mark <name>" in err, b"Traceback" in err) == (
        2, b"", True, True, False)


def test_has_mark_with_an_empty_name_exits_2_with_a_usage_line_listing_has_mark_and_no_traceback_1624(
        monkeypatch, capsysbinary, ledger_steps):
    fake_stdin(monkeypatch, b"# Plan for #42\n\n- [ ] fix the red job \xe2\x9f\xa6ci-repair\xe2\x9f\xa7 \xe2\x9f\xa6criterion 1\xe2\x9f\xa7\n")
    try:
        code = ledger_steps.main(["has-mark", ""])
    except Exception as exc:
        code = type(exc).__name__
    out, err = capsysbinary.readouterr()

    assert (code, out, err.startswith(b"usage: ledger-steps.sh "), b"has-mark <name>" in err, b"Traceback" in err) == (
        2, b"", True, True, False)


def via_stdin(module, ledger):
    def main(argv):
        fake_stdin_text(ledger)
        return module.main(argv)

    return types.SimpleNamespace(main=main)


def fake_stdin_text(ledger):
    sys.stdin = io.TextIOWrapper(io.BytesIO(ledger.encode()))


KINDS = (
    "# Plan for #42\n\nprose\n\n"
    "- [x] add lowercasing ⟦criterion 1⟧ ⟂ refactor pending\n"
    "- [X] trim spaces ⟦added⟧ ⟦criterion 2⟧\n"
    "- [x] tidy names ⟦added⟧ ⟦criterion 3⟧ ⟂ refactor pending\n"
    "- [ ] strip edge hyphens ⟦criterion 3⟧\n"
    "  - [ ] note without a criterion\n"
    "- [ ] a person reads the page ⟦human-owed⟧ ⟦criterion 4⟧\n"
    "- [ ] `make test` is green ⟦full-suite⟧ ⟦criterion 5⟧"
)
OPEN = (
    "# Plan for #42\n\n- [x] add lowercasing ⟦criterion 1⟧\n"
    "- [ ] a person reads the page ⟦human-owed⟧ ⟦criterion 2⟧\n"
    "- [ ] `make test` is green ⟦full-suite⟧ ⟦criterion 3⟧\n"
    "- [ ] strip edge hyphens ⟦criterion 4⟧\n"
)
NONE = (
    "# Plan for #42\n\n- [x] add lowercasing ⟦criterion 1⟧\n"
    "- [ ] a person reads the page ⟦human-owed⟧ ⟦criterion 2⟧\n"
    "- [ ] `make test` is green ⟦full-suite⟧ ⟦criterion 3⟧\n"
)
TICKED = "# Plan for #42\n\n- [x] add lowercasing ⟦criterion 1⟧\n- [x] strip edge hyphens ⟦criterion 2⟧\n"


def test_cli_with_no_argument_prints_ledger_steps_records_for_every_step_kind_and_mark(
        run_cli, ledger_steps):
    got = run_cli(via_stdin(ledger_steps, KINDS), [])

    assert got == (0, (
        "1\tdone\tstep\t1\t0\t1\tadd lowercasing ⟦criterion 1⟧\n"
        "2\tdone\tstep\t0\t1\t2\ttrim spaces ⟦added⟧ ⟦criterion 2⟧\n"
        "3\tdone\tstep\t1\t1\t3\ttidy names ⟦added⟧ ⟦criterion 3⟧\n"
        "4\topen\tstep\t0\t0\t3\tstrip edge hyphens ⟦criterion 3⟧\n"
        "5\topen\tstep\t0\t0\t\tnote without a criterion\n"
        "6\topen\thuman-owed\t0\t0\t4\ta person reads the page ⟦human-owed⟧ ⟦criterion 4⟧\n"
        "7\topen\tfull-suite\t0\t0\t5\t`make test` is green ⟦full-suite⟧ ⟦criterion 5⟧\n"
    ), "")


def test_cli_current_prints_the_first_pending_step_else_the_first_open_step_kind_step_else_exits_3_with_no_output(
        run_cli, ledger_steps):
    got = [run_cli(via_stdin(ledger_steps, ledger), ["current"]) for ledger in (KINDS, OPEN, NONE)]

    assert got == [
        (0, "add lowercasing ⟦criterion 1⟧\n", ""),
        (0, "strip edge hyphens ⟦criterion 4⟧\n", ""),
        (3, "", ""),
    ]


def test_cli_current_or_last_done_prints_currents_answer_with_a_step_open_last_dones_when_every_step_is_ticked_and_exits_3_for_no_step(
        run_cli, ledger_steps):
    got = [run_cli(via_stdin(ledger_steps, ledger), ["current-or-last-done"])
           for ledger in (OPEN, TICKED, "# Plan for #42\n\nprose\n")]
    want_open = run_cli(via_stdin(ledger_steps, OPEN), ["current"])
    want_ticked = run_cli(via_stdin(ledger_steps, TICKED), ["last-done"])

    assert got == [want_open, want_ticked, (3, "", "")]
    assert got[:2] == [(0, "strip edge hyphens ⟦criterion 4⟧\n", ""), (0, "strip edge hyphens ⟦criterion 2⟧\n", "")]


def test_cli_bogus_exits_2_with_nothing_on_stdout_and_exactly_the_one_usage_line_listing_every_verb_including_has_mark_1624(
        run_cli, ledger_steps):
    got = run_cli(via_stdin(ledger_steps, KINDS), ["bogus"])

    assert got == (2, "", USAGE.decode())
    assert "has-mark <name>" in got[2]


def test_cli_next_phase_and_next_unchecked_both_exit_3_with_nothing_on_a_phased_step_whose_contract_is_filed_owed_1410(
        run_cli, ledger_steps):
    next_unchecked = importlib.import_module("veri.next_unchecked")
    owed = (
        "# Plan for #42\n\n- [x] add lowercasing ⟦criterion 1⟧\n"
        "- [ ] rename the slug helper ⟦phases: expand, migrate, contract-a, contract-b⟧ ⟦criterion 1⟧"
        " ⟂ expand done ⟂ migrate done ⟂ contract-a owed\n\n"
        "## Owed steps\n\n- rename the slug helper: contract-a\n"
    )

    got = [run_cli(via_stdin(ledger_steps, owed), ["next-phase"]),
           run_cli(via_stdin(next_unchecked, owed), [])]

    assert got == [(3, "", ""), (3, "", "")]


def test_cli_a_fixture_repair_step_prints_as_kind_step_with_its_criterion_and_next_unchecked_hands_it_over(
        run_cli, ledger_steps):
    next_unchecked = importlib.import_module("veri.next_unchecked")
    step = ("the supervise case passes under load: repairs the fixture 'awake-clock' in"
            " tests/supervise.test.sh, reproduced by a case in tests/supervise.test.sh"
            " ⟦fixture-repair⟧ ⟦criterion 1⟧")
    ledger = f"# Plan for #1021\n\n- [ ] {step}\n"

    got = [run_cli(via_stdin(ledger_steps, ledger), []),
           run_cli(via_stdin(next_unchecked, ledger), [])]

    assert got == [(0, f"1\topen\tstep\t0\t0\t1\t{step}\n", ""), (0, step + "\n", "")]


def test_cli_a_human_owed_step_with_the_mark_before_its_text_and_no_criterion_tag_is_kind_human_owed_and_next_unchecked_skips_it_2248(
        run_cli, ledger_steps):
    next_unchecked = importlib.import_module("veri.next_unchecked")
    ledger = "# Plan for #42\n\n- [ ] ⟦human-owed⟧ measure X once deployed\n"

    got = [run_cli(via_stdin(ledger_steps, ledger), []),
           run_cli(via_stdin(next_unchecked, ledger), [])]

    assert got == [(0, "1\topen\thuman-owed\t0\t0\t\t⟦human-owed⟧ measure X once deployed\n", ""), (3, "", "")]


def test_cli_a_human_owed_step_with_the_mark_before_its_text_and_a_criterion_tag_is_kind_human_owed_with_that_criterion_and_next_unchecked_skips_it_2248(
        run_cli, ledger_steps):
    next_unchecked = importlib.import_module("veri.next_unchecked")
    step = "⟦human-owed⟧ measure X once deployed ⟦criterion 2⟧"
    ledger = f"# Plan for #42\n\n- [ ] {step}\n"

    got = [run_cli(via_stdin(ledger_steps, ledger), []),
           run_cli(via_stdin(next_unchecked, ledger), [])]

    assert got == [(0, f"1\topen\thuman-owed\t0\t0\t2\t{step}\n", ""), (3, "", "")]


def test_cli_a_human_owed_step_with_the_mark_trailing_its_text_and_no_criterion_tag_is_kind_human_owed_and_next_unchecked_skips_it_2248(
        run_cli, ledger_steps):
    next_unchecked = importlib.import_module("veri.next_unchecked")
    step = "measure X once deployed ⟦human-owed⟧"
    ledger = f"# Plan for #42\n\n- [ ] {step}\n"

    got = [run_cli(via_stdin(ledger_steps, ledger), []),
           run_cli(via_stdin(next_unchecked, ledger), [])]

    assert got == [(0, f"1\topen\thuman-owed\t0\t0\t\t{step}\n", ""), (3, "", "")]
