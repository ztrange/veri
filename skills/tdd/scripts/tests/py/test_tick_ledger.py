"""In-process cases for veri/tick_ledger.py, the module tick-ledger.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = b"usage: tick-ledger.sh [--refactor-pending] <ledger-file> <matcher>\n"


@pytest.fixture
def tick_ledger():
    return importlib.import_module("veri.tick_ledger")


def test_main_refuses_a_missing_or_empty_ledger_file_with_the_usage_line_and_exits_3_leaving_an_unmatched_ledger_untouched(
        tmp_path, capsysbinary, tick_ledger):
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(b"- [ ] alpha\n")
    results = {}
    for argv in ([], [""], ["--refactor-pending"], ["--refactor-pending", ""], [str(ledger), "zeta"]):
        code = tick_ledger.main(argv)
        results[tuple(argv)] = (code, *capsysbinary.readouterr())

    assert results == {
        (): (2, b"", USAGE),
        ("",): (2, b"", USAGE),
        ("--refactor-pending",): (2, b"", USAGE),
        ("--refactor-pending", ""): (2, b"", USAGE),
        (str(ledger), "zeta"): (3, b"", b""),
    }
    assert ledger.read_bytes() == b"- [ ] alpha\n"
