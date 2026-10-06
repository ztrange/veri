"""In-process cases for veri/clear_refactor_pending.py, the module clear-refactor-pending.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = b"usage: clear-refactor-pending.sh <ledger-file> <matcher>\n"


@pytest.fixture
def clear_refactor_pending():
    return importlib.import_module("veri.clear_refactor_pending")


def test_main_refuses_a_missing_or_empty_ledger_file_clears_the_first_matching_mark_and_exits_3_leaving_an_unmatched_ledger_untouched(
        tmp_path, capsysbinary, clear_refactor_pending):
    seed = "- [x] a ⟂ refactor pending\n- [x] b ⟂ refactor pending\n".encode()
    cleared = tmp_path / "cleared.md"
    cleared.write_bytes(seed)
    unmatched = tmp_path / "unmatched.md"
    unmatched.write_bytes(seed)
    results = {}
    for argv in ([], [""], [str(cleared), "a"], [str(unmatched), "zeta"]):
        code = clear_refactor_pending.main(argv)
        results[tuple(argv)] = (code, *capsysbinary.readouterr())

    assert results == {
        (): (2, b"", USAGE),
        ("",): (2, b"", USAGE),
        (str(cleared), "a"): (0, b"", b""),
        (str(unmatched), "zeta"): (3, b"", b""),
    }
    assert cleared.read_bytes() == "- [x] a\n- [x] b ⟂ refactor pending\n".encode()
    assert unmatched.read_bytes() == seed
