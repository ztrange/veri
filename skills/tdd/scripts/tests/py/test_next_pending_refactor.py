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
