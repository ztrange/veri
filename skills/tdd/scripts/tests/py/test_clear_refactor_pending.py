"""In-process cases for veri/clear_refactor_pending.py, the module clear-refactor-pending.sh is a shim over."""
import importlib
import os
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


def test_main_exits_3_leaving_an_open_marked_step_a_crlf_mark_and_a_mark_before_a_space_untouched_and_clears_only_the_last_of_a_double_mark(
        tmp_path, capsysbinary, clear_refactor_pending):
    seeds = {
        "open": "- [ ] a ⟂ refactor pending\n".encode(),
        "crlf": "- [x] a ⟂ refactor pending\r\n".encode(),
        "space": "- [x] a ⟂ refactor pending \n".encode(),
        "double": "- [x] a ⟂ refactor pending ⟂ refactor pending\n".encode(),
    }
    results = {}
    for name, seed in seeds.items():
        led = tmp_path / f"{name}.md"
        led.write_bytes(seed)
        code = clear_refactor_pending.main([str(led), "a"])
        results[name] = (code, *capsysbinary.readouterr(), led.read_bytes())

    assert results == {
        "open": (3, b"", b"", seeds["open"]),
        "crlf": (3, b"", b"", seeds["crlf"]),
        "space": (3, b"", b"", seeds["space"]),
        "double": (0, b"", b"", "- [x] a ⟂ refactor pending\n".encode()),
    }


def test_main_rewrites_a_cleared_ledger_ending_in_exactly_one_newline_and_leaves_an_unmatched_or_empty_ledger_byte_identical(
        tmp_path, capsysbinary, clear_refactor_pending):
    seeds = {
        "unterminated": ("- [x] a ⟂ refactor pending".encode(), "a"),
        "triple": ("- [x] a ⟂ refactor pending\n\n\n".encode(), "a"),
        "unmatched": ("- [x] a ⟂ refactor pending\n\n\n".encode(), "zeta"),
        "empty": (b"", "a"),
    }
    results = {}
    for name, (seed, matcher) in seeds.items():
        led = tmp_path / f"{name}.md"
        led.write_bytes(seed)
        code = clear_refactor_pending.main([str(led), matcher])
        results[name] = (code, *capsysbinary.readouterr(), led.read_bytes())

    assert results == {
        "unterminated": (0, b"", b"", b"- [x] a\n"),
        "triple": (0, b"", b"", b"- [x] a\n"),
        "unmatched": (3, b"", b"", seeds["unmatched"][0]),
        "empty": (3, b"", b"", b""),
    }


def test_main_drops_a_nul_byte_on_a_clear_and_passes_a_non_utf8_byte_through_in_the_file_and_the_matcher(
        tmp_path, capsysbinary, clear_refactor_pending):
    nul = tmp_path / "nul.md"
    nul.write_bytes("- [x] a\0z ⟂ refactor pending\n".encode())
    code = clear_refactor_pending.main([str(nul), "a"])
    assert (code, *capsysbinary.readouterr(), nul.read_bytes()) == (0, b"", b"", b"- [x] az\n")

    raw = tmp_path / "raw.md"
    raw.write_bytes(b"- [x] a\xff" + " ⟂ refactor pending\n".encode())
    code = clear_refactor_pending.main([str(raw), os.fsdecode(b"a\xff")])
    assert (code, *capsysbinary.readouterr(), raw.read_bytes()) == (0, b"", b"", b"- [x] a\xff\n")


def test_main_matches_a_step_line_by_the_c_locale_grammar_clearing_a_capital_box_a_tab_and_ascii_space_before_the_dash_but_not_034_or_nbsp(
        tmp_path, capsysbinary, clear_refactor_pending):
    seeds = {
        "capital": "- [X] a ⟂ refactor pending\n".encode(),
        "tab": "-\t[x] a ⟂ refactor pending\n".encode(),
        "spaces": "  - [x] a ⟂ refactor pending\n".encode(),
        "formfeed": "\f- [x] a ⟂ refactor pending\n".encode(),
        "fs": "\034- [x] a ⟂ refactor pending\n".encode(),
        "nbsp": " - [x] a ⟂ refactor pending\n".encode(),
    }
    results = {}
    for name, seed in seeds.items():
        led = tmp_path / f"{name}.md"
        led.write_bytes(seed)
        code = clear_refactor_pending.main([str(led), "a"])
        results[name] = (code, *capsysbinary.readouterr(), led.read_bytes())

    assert results == {
        "capital": (0, b"", b"", b"- [X] a\n"),
        "tab": (0, b"", b"", b"-\t[x] a\n"),
        "spaces": (0, b"", b"", b"  - [x] a\n"),
        "formfeed": (0, b"", b"", b"\f- [x] a\n"),
        "fs": (3, b"", b"", seeds["fs"]),
        "nbsp": (3, b"", b"", seeds["nbsp"]),
    }
