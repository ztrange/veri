"""In-process cases for veri/next_unchecked.py, the module next-unchecked.sh is a shim over."""
import importlib
import io
import sys

import pytest

SLUGIFY = (
    "# Plan for #42\n"
    "\n"
    "- [x] add the slugify lowercasing\n"
    "- [ ] collapse non-alphanumerics to a single hyphen\n"
    "- [ ] strip leading and trailing hyphens"
).encode()


@pytest.fixture
def next_unchecked():
    return importlib.import_module("veri.next_unchecked")


def fake_stdin(monkeypatch, data):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(data)))


def test_main_prints_the_first_open_step_exits_3_over_an_all_done_ledger_and_ignores_arguments(
        monkeypatch, capsysbinary, next_unchecked):
    all_done = (
        "# Plan for #42\n"
        "\n"
        "- [x] add the slugify lowercasing\n"
        "- [x] collapse non-alphanumerics to a single hyphen"
    ).encode()
    results = {}
    for ledger_name, ledger in (("slugify", SLUGIFY), ("all done", all_done)):
        for argv in ([], ["--bogus"]):
            fake_stdin(monkeypatch, ledger)
            code = next_unchecked.main(argv)
            results[(ledger_name, *argv)] = (code, *capsysbinary.readouterr())

    assert all(code in range(4) for code, _, _ in results.values())
    assert results == {
        ("slugify",): (0, b"collapse non-alphanumerics to a single hyphen\n", b""),
        ("slugify", "--bogus"): (0, b"collapse non-alphanumerics to a single hyphen\n", b""),
        ("all done",): (3, b"", b""),
        ("all done", "--bogus"): (3, b"", b""),
    }


def test_main_prints_the_first_open_step_or_diff_checked_record_veri_ledger_finds(
        monkeypatch, capsysbinary, next_unchecked):
    ledger = (
        "# Plan for #42\n"
        "\n"
        "- [X] ticked with an upper-case box ⟦criterion 1⟧\n"
        "- [ ] run the whole suite ⟦full-suite⟧ ⟦criterion 2⟧\n"
        "- [ ] ask a human ⟦human-owed⟧ ⟦criterion 3⟧\n"
        "- [ ] the counted line is gone ⟦diff-checked⟧ ⟦criterion 4⟧\n"
        "\v- [ ] the vertical-tab-indented step ⟦criterion 5⟧\n"
        "- [x] already done ⟦criterion 6⟧"
    )
    ledger_steps = importlib.import_module("veri.ledger").ledger_steps
    want = next(
        record[6] for record in ledger_steps(ledger)
        if record[1] == "open" and record[2] in ("step", "diff-checked"))
    fake_stdin(monkeypatch, ledger.encode())

    code = next_unchecked.main([])

    assert (code, *capsysbinary.readouterr()) == (0, (want + "\n").encode(), b"")


def test_main_prints_the_text_and_one_newline_and_a_textless_open_step_as_an_empty_line(
        monkeypatch, capsysbinary, next_unchecked):
    results = {}
    for name, ledger in (
            ("text", b"- [x] done\n- [ ] collapse to one hyphen\n- [ ] later"),
            ("bare box", b"- [x] done\n- [ ]\n- [ ] later"),
            ("box and one space", b"- [x] done\n- [ ] \n- [ ] later")):
        fake_stdin(monkeypatch, ledger)
        code = next_unchecked.main([])
        results[name] = (code, *capsysbinary.readouterr())

    assert results == {
        "text": (0, b"collapse to one hyphen\n", b""),
        "bare box": (0, b"\n", b""),
        "box and one space": (0, b"\n", b""),
    }


def test_main_exits_3_silent_for_empty_stdin_and_keeps_an_open_steps_refactor_pending_mark(
        monkeypatch, capsysbinary, next_unchecked):
    results = {}
    for name, ledger in (
            ("empty", b""),
            ("pending open", "- [x] done\n- [ ] the cog turns ⟦criterion 2⟧ ⟂ refactor pending\n".encode())):
        fake_stdin(monkeypatch, ledger)
        code = next_unchecked.main([])
        results[name] = (code, *capsysbinary.readouterr())

    assert results == {
        "empty": (3, b"", b""),
        "pending open": (0, "the cog turns ⟦criterion 2⟧ ⟂ refactor pending\n".encode(), b""),
    }


def test_main_drops_nul_bytes_and_prints_a_non_utf8_byte_back_as_itself(
        monkeypatch, capsysbinary, next_unchecked):
    fake_stdin(monkeypatch, b"- [x] done\n- [ ] a caf\xe9 c\x00og\n- [ ] later")

    code = next_unchecked.main([])

    assert (code, *capsysbinary.readouterr()) == (0, b"a caf\xe9 cog\n", b"")


def test_main_writes_nothing_on_stderr_for_a_printed_step_exit_3_or_arguments_given(
        monkeypatch, capsysbinary, next_unchecked):
    stderr = {}
    for ledger_name, ledger in (("printed step", SLUGIFY), ("no step", b"# Plan for #42\n")):
        for argv in ([], ["--bogus", "extra"]):
            fake_stdin(monkeypatch, ledger)
            code = next_unchecked.main(argv)
            stderr[(ledger_name, *argv)] = (code, capsysbinary.readouterr().err)

    assert stderr == {
        ("printed step",): (0, b""),
        ("printed step", "--bogus", "extra"): (0, b""),
        ("no step",): (3, b""),
        ("no step", "--bogus", "extra"): (3, b""),
    }


CONTRACT_CASES = (
    ("no checkboxes exits 3", "# just a heading\nsome prose", 3, ""),
    ("nested step", "  - [ ] nested criterion", 0, "nested criterion"),
    ("verbatim special chars",
     '- [x] done one\n- [ ] `slugify("a/b")` returns `a-b`', 0, '`slugify("a/b")` returns `a-b`'),
    ("first line unchecked", "- [ ] only step", 0, "only step"),
    ("owed bullets are not steps",
     "# Plan for #42\n\n"
     "- [x] collapse non-alphanumerics to a single hyphen\n"
     "- [x] strip leading and trailing hyphens\n\n"
     "## Owed steps\n\n"
     "- a unicode dash collapses too\n"
     '- an empty slug falls back to "n-a"', 3, ""),
    ("full-suite skipped",
     "# Plan for #42\n\n"
     "- [ ] the suites are green ⟦full-suite⟧ ⟦criterion 1⟧\n"
     "- [ ] pin the second step ⟦criterion 2⟧", 0, "pin the second step ⟦criterion 2⟧"),
    ("human-owed skipped",
     "# Plan for #42\n\n"
     "- [ ] each suite broken on purpose, its red output recorded ⟦human-owed⟧ ⟦criterion 1⟧\n"
     "- [ ] pin the second step ⟦criterion 2⟧", 0, "pin the second step ⟦criterion 2⟧"),
    ("quoted marker handed out",
     "# Plan for #42\n\n"
     "- [ ] a step whose text quotes ⟦full-suite⟧ or ⟦human-owed⟧ is still handed to a leaf ⟦criterion 2⟧",
     0, "a step whose text quotes ⟦full-suite⟧ or ⟦human-owed⟧ is still handed to a leaf ⟦criterion 2⟧"),
    ("written marker skipped",
     "# Plan for #42\n\n"
     "- [ ] the suites are green ⟦full-suite⟧ ⟦criterion 1⟧\n"
     "- [ ] each suite broken on purpose, its red output recorded ⟦human-owed⟧ ⟦criterion 2⟧\n"
     "- [ ] pin the third step ⟦criterion 3⟧", 0, "pin the third step ⟦criterion 3⟧"),
    ("written plus quoted marker skipped",
     "# Plan for #42\n\n"
     "- [ ] the text quotes ⟦human-owed⟧ yet the suites are green ⟦full-suite⟧ ⟦criterion 1⟧\n"
     "- [ ] pin the second step ⟦criterion 2⟧", 0, "pin the second step ⟦criterion 2⟧"),
    ("fully ticked quoting ledger exits 3",
     "# Plan for #42\n\n"
     "- [x] a step whose text quotes ⟦full-suite⟧ or ⟦human-owed⟧ is still handed to a leaf ⟦criterion 1⟧\n"
     "- [x] the suites are green ⟦full-suite⟧ ⟦criterion 2⟧\n"
     "- [x] pin the third step ⟦criterion 3⟧", 3, ""),
    ("suite-repair handed out",
     "# Plan for #42\n\n"
     "- [ ] the suites are green ⟦full-suite⟧ ⟦criterion 3⟧\n"
     "- [ ] repair widget-counts.test.sh: FAIL - counts ⟦suite-repair⟧ ⟦criterion 4⟧\n"
     "- [ ] pin the third step ⟦criterion 5⟧",
     0, "repair widget-counts.test.sh: FAIL - counts ⟦suite-repair⟧ ⟦criterion 4⟧"),
    ("diff-checked handed out",
     "# Plan for #42\n\n"
     "- [ ] the dead counted line is gone ⟦diff-checked⟧ ⟦criterion 1⟧\n"
     "- [ ] pin the second step ⟦criterion 2⟧",
     0, "the dead counted line is gone ⟦diff-checked⟧ ⟦criterion 1⟧"),
)


def test_main_answers_each_contract_case_of_the_bash_suite(monkeypatch, capsysbinary, next_unchecked):
    results, want = {}, {}
    for name, ledger, code, text in CONTRACT_CASES:
        fake_stdin(monkeypatch, ledger.encode())
        results[name] = (next_unchecked.main([]), *capsysbinary.readouterr())
        want[name] = (code, (text + "\n").encode() if code == 0 else b"", b"")

    assert len(CONTRACT_CASES) == 13
    assert results == want
