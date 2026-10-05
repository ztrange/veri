"""In-process cases for veri/next_pending_refactor.py, the module next-pending-refactor.sh is a shim over."""
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
    "- [x] collapse non-alphanumerics to a single hyphen ⟂ refactor pending\n"
    "- [x] strip leading and trailing hyphens ⟂ refactor pending\n"
    "- [ ] percent-encode the remainder"
).encode()


@pytest.fixture
def next_pending_refactor():
    return importlib.import_module("veri.next_pending_refactor")


def fake_stdin(monkeypatch, data):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(data)))


def test_main_prints_the_first_pending_step_exits_3_over_a_settled_ledger_and_ignores_arguments(
        monkeypatch, capsysbinary, next_pending_refactor):
    settled = (
        "# Plan for #42\n"
        "\n"
        "- [x] add the slugify lowercasing\n"
        "- [ ] collapse non-alphanumerics to a single hyphen"
    ).encode()
    results = {}
    for ledger_name, ledger in (("slugify", SLUGIFY), ("settled", settled)):
        for argv in ([], ["--bogus"]):
            fake_stdin(monkeypatch, ledger)
            code = next_pending_refactor.main(argv)
            results[(ledger_name, *argv)] = (code, *capsysbinary.readouterr())

    assert all(code in range(4) for code, _, _ in results.values())
    assert results == {
        ("slugify",): (0, b"collapse non-alphanumerics to a single hyphen\n", b""),
        ("slugify", "--bogus"): (0, b"collapse non-alphanumerics to a single hyphen\n", b""),
        ("settled",): (3, b"", b""),
        ("settled", "--bogus"): (3, b"", b""),
    }


def test_main_prints_the_first_done_and_pending_record_veri_ledger_ledger_steps_returns(
        monkeypatch, capsysbinary, next_pending_refactor):
    ledger = (
        "# Plan for #42\n"
        "\n"
        "- [ ] still open though it ends in the mark ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [x] tidied already ⟦criterion 2⟧\n"
        "\v- [X] indented by a vertical tab, upper-case box ⟦criterion 3⟧ ⟂ refactor pending\n"
        "- [x] ⟦full-suite⟧ ⟦criterion 4⟧ ⟂ refactor pending"
    ).encode()
    ledger_steps = importlib.import_module("veri.ledger").ledger_steps
    first = next(record for record in ledger_steps(ledger.decode())
                 if record[1] == "done" and record[3] == "1")

    fake_stdin(monkeypatch, ledger)
    code = next_pending_refactor.main([])

    assert (code, *capsysbinary.readouterr()) == (0, (first[6] + "\n").encode(), b"")


def test_main_prints_the_step_text_and_exactly_one_newline_and_a_bare_pending_step_as_an_empty_line(
        monkeypatch, capsysbinary, next_pending_refactor):
    results = {}
    for ledger_name, ledger in (
            ("worded", "- [x] trim the slug ⟦criterion 1⟧ ⟂ refactor pending".encode()),
            ("bare", "- [x]  ⟂ refactor pending\n- [x] later ⟂ refactor pending\n".encode())):
        fake_stdin(monkeypatch, ledger)
        code = next_pending_refactor.main([])
        results[ledger_name] = (code, *capsysbinary.readouterr())

    assert results == {
        "worded": (0, "trim the slug ⟦criterion 1⟧\n".encode(), b""),
        "bare": (0, b"\n", b""),
    }


def test_main_returns_a_ticked_step_of_any_kind_counts_an_upper_case_box_and_exits_3_when_only_an_open_step_ends_in_the_mark(
        monkeypatch, capsysbinary, next_pending_refactor):
    results = {}
    for ledger_name, ledger in (
            ("full-suite", "- [ ] open ⟂ refactor pending\n- [x] ⟦full-suite⟧ ⟦criterion 2⟧ ⟂ refactor pending"),
            ("human-owed", "- [ ] open ⟂ refactor pending\n- [x] ⟦human-owed⟧ ⟦criterion 3⟧ ⟂ refactor pending"),
            ("diff-checked", "- [ ] open ⟂ refactor pending\n- [x] ⟦diff-checked⟧ ⟦criterion 4⟧ ⟂ refactor pending"),
            ("upper-case", "- [ ] open ⟂ refactor pending\n- [X] ticked upper-case ⟂ refactor pending"),
            ("open-only", "- [x] tidied already\n- [ ] still open ⟂ refactor pending\n")):
        fake_stdin(monkeypatch, ledger.encode())
        code = next_pending_refactor.main([])
        results[ledger_name] = (code, *capsysbinary.readouterr())

    assert results == {
        "full-suite": (0, "⟦full-suite⟧ ⟦criterion 2⟧\n".encode(), b""),
        "human-owed": (0, "⟦human-owed⟧ ⟦criterion 3⟧\n".encode(), b""),
        "diff-checked": (0, "⟦diff-checked⟧ ⟦criterion 4⟧\n".encode(), b""),
        "upper-case": (0, b"ticked upper-case\n", b""),
        "open-only": (3, b"", b""),
    }


def test_main_returns_3_with_nothing_on_stdout_for_empty_stdin(
        monkeypatch, capsysbinary, next_pending_refactor):
    fake_stdin(monkeypatch, b"")
    code = next_pending_refactor.main([])

    assert (code, capsysbinary.readouterr().out) == (3, b"")


def test_main_drops_nul_bytes_and_prints_a_non_utf8_byte_in_the_step_text_back_as_that_byte(
        monkeypatch, capsysbinary, next_pending_refactor):
    fake_stdin(monkeypatch, b"- [x] caf\xe9 sl\x00ug " + "⟂ refactor pending\n".encode())
    code = next_pending_refactor.main([])

    assert (code, *capsysbinary.readouterr()) == (0, b"caf\xe9 slug\n", b"")
