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


def test_main_ticks_the_matching_step_in_place_marking_it_refactor_pending_only_with_the_flag(
        tmp_path, capsysbinary, tick_ledger):
    seed = (b"# Plan for #42\n\n- [ ] add lowercasing\n- [ ] collapse to single hyphen\n"
            b"- [ ] strip edge hyphens\n")
    results = {}
    for flag in (["--refactor-pending"], []):
        ledger = tmp_path / f"ledger{len(flag)}.md"
        ledger.write_bytes(seed)
        code = tick_ledger.main([*flag, str(ledger), "collapse to single hyphen"])
        out, _ = capsysbinary.readouterr()
        results[tuple(flag)] = (code, out, ledger.read_bytes())

    assert results == {
        ("--refactor-pending",): (0, b"", "# Plan for #42\n\n- [ ] add lowercasing\n"
                                  "- [x] collapse to single hyphen ⟂ refactor pending\n"
                                  "- [ ] strip edge hyphens\n".encode()),
        (): (0, b"", b"# Plan for #42\n\n- [ ] add lowercasing\n- [x] collapse to single hyphen\n"
                     b"- [ ] strip edge hyphens\n"),
    }


def test_main_returns_0_for_a_tick_3_for_an_unmatched_matcher_and_2_for_no_argument_every_exit_inside_0_to_3(
        tmp_path, capsysbinary, tick_ledger):
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(b"- [ ] alpha\n- [ ] beta\n")
    codes = [tick_ledger.main(argv) for argv in ([str(ledger), "alpha"], [str(ledger), "zeta"], [])]
    capsysbinary.readouterr()

    assert codes == [0, 3, 2]
    assert all(0 <= code <= 3 for code in codes)
