"""In-process cases for veri/next_unchecked.py, the module next-unchecked.sh is a shim over."""
import importlib
import io
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

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
