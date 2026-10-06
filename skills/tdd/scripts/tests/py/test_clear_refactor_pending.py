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


def test_main_writes_what_the_ledger_modules_ledger_clear_pending_returns_and_passes_it_the_matcher(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    matchers = []

    def substitute(text, matcher):
        matchers.append(matcher)
        return True, f"cleared by the module: {matcher}\n"

    monkeypatch.setattr(sys.modules["ledger"], "ledger_clear_pending", substitute)
    led = tmp_path / "issue-42.md"
    led.write_bytes("- [x] collapse to single hyphen ⟂ refactor pending\n".encode())

    code = clear_refactor_pending.main([str(led), "collapse to single hyphen"])

    assert (code, *capsysbinary.readouterr()) == (0, b"", b"")
    assert matchers == ["collapse to single hyphen"]
    assert led.read_bytes() == b"cleared by the module: collapse to single hyphen\n"


def test_main_returns_2_leaving_the_ledger_byte_identical_when_the_ledger_modules_ledger_clear_pending_hands_back_status_7(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    def substitute(text, matcher):
        return 7, "written by a foreign status\n"

    monkeypatch.setattr(sys.modules["ledger"], "ledger_clear_pending", substitute)
    seed = "- [x] a ⟂ refactor pending\n".encode()
    led = tmp_path / "issue-42.md"
    led.write_bytes(seed)

    code = clear_refactor_pending.main([str(led), "a"])

    assert (code, *capsysbinary.readouterr()) == (2, b"", b"")
    assert led.read_bytes() == seed


def test_main_reads_a_lone_ledger_file_as_an_empty_matcher_clearing_the_first_marked_done_step_and_ignores_arguments_after_the_second(
        tmp_path, capsysbinary, clear_refactor_pending):
    seed = "- [x] a ⟂ refactor pending\n- [x] b ⟂ refactor pending\n".encode()
    lone = tmp_path / "lone.md"
    lone.write_bytes(seed)
    extra = tmp_path / "extra.md"
    extra.write_bytes(seed)
    results = {}
    for argv in ([str(lone)], [str(extra), "b", "zeta", "eta"]):
        code = clear_refactor_pending.main(argv)
        results[tuple(argv)] = (code, *capsysbinary.readouterr())

    assert results == {
        (str(lone),): (0, b"", b""),
        (str(extra), "b", "zeta", "eta"): (0, b"", b""),
    }
    assert lone.read_bytes() == "- [x] a\n- [x] b ⟂ refactor pending\n".encode()
    assert extra.read_bytes() == "- [x] a ⟂ refactor pending\n- [x] b\n".encode()


def test_main_matches_the_matcher_as_a_literal_substring_of_the_whole_line_box_and_mark_included(
        tmp_path, capsysbinary, clear_refactor_pending):
    seed = "- [x] a ⟂ refactor pending\n- [x] b * c ⟂ refactor pending\n".encode()
    results = {}
    for name, matcher in (("pending", "refactor pending"), ("box", "[x] a"), ("mark", "a ⟂"),
                          ("star", "*"), ("glob", "b*c")):
        led = tmp_path / f"{name}.md"
        led.write_bytes(seed)
        code = clear_refactor_pending.main([str(led), matcher])
        results[matcher] = (code, *capsysbinary.readouterr(), led.read_bytes())

    first_cleared = "- [x] a\n- [x] b * c ⟂ refactor pending\n".encode()
    assert results == {
        "refactor pending": (0, b"", b"", first_cleared),
        "[x] a": (0, b"", b"", first_cleared),
        "a ⟂": (0, b"", b"", first_cleared),
        "*": (0, b"", b"", "- [x] a ⟂ refactor pending\n- [x] b * c\n".encode()),
        "b*c": (3, b"", b"", seed),
    }
