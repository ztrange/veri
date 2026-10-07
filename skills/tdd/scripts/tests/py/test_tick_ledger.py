"""In-process cases for veri/tick_ledger.py, the module tick-ledger.sh is a shim over."""
import errno
import importlib
import os
import pathlib
import resource
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


def test_main_rewrites_the_ledger_as_printf_over_a_command_substitution_collapsing_trailing_newlines_adding_a_final_one_and_dropping_nul(
        tmp_path, capsysbinary, tick_ledger):
    results = {}
    for seed in (b"- [ ] a\n\n\n", b"- [ ] a", b"- [ ] a\0z"):
        ledger = tmp_path / f"ledger{len(results)}.md"
        ledger.write_bytes(seed)
        code = tick_ledger.main([str(ledger), "a"])
        capsysbinary.readouterr()
        results[seed] = (code, ledger.read_bytes())

    assert results == {
        b"- [ ] a\n\n\n": (0, b"- [x] a\n"),
        b"- [ ] a": (0, b"- [x] a\n"),
        b"- [ ] a\0z": (0, b"- [x] az\n"),
    }


def test_main_ticks_the_first_open_step_for_an_omitted_or_empty_matcher_ignores_arguments_after_the_second_and_reads_the_flag_only_first(
        tmp_path, capsysbinary, tick_ledger):
    results = {}
    for argv in ([], [""], ["b", "--refactor-pending"], ["--refactor-pending"]):
        ledger = tmp_path / f"ledger{len(results)}.md"
        ledger.write_bytes(b"- [ ] a\n- [ ] b\n")
        code = tick_ledger.main([str(ledger), *argv])
        results[tuple(argv)] = (code, *capsysbinary.readouterr(), ledger.read_bytes())

    assert results == {
        (): (0, b"", b"", b"- [x] a\n- [ ] b\n"),
        ("",): (0, b"", b"", b"- [x] a\n- [ ] b\n"),
        ("b", "--refactor-pending"): (0, b"", b"", b"- [ ] a\n- [x] b\n"),
        ("--refactor-pending",): (3, b"", b"", b"- [ ] a\n- [ ] b\n"),
    }


def test_main_leaves_an_empty_ledger_unwritten_with_exit_3_marks_a_crlf_step_after_its_cr_and_skips_a_lower_and_upper_x_step(
        tmp_path, capsysbinary, tick_ledger):
    results = {}
    for flag, seed, matcher in (
            ([], b"", "a"),
            (["--refactor-pending"], b"- [ ] a\r\n", "a"),
            ([], b"- [x] a\n- [X] a\n- [ ] a\n", "a")):
        ledger = tmp_path / f"ledger{len(results)}.md"
        ledger.write_bytes(seed)
        os.utime(ledger, ns=(0, 0))
        code = tick_ledger.main([*flag, str(ledger), matcher])
        results[seed] = (code, *capsysbinary.readouterr(), ledger.read_bytes(), ledger.stat().st_mtime_ns == 0)

    assert results == {
        b"": (3, b"", b"", b"", True),
        b"- [ ] a\r\n": (0, b"", b"", "- [x] a\r ⟂ refactor pending\n".encode(), False),
        b"- [x] a\n- [X] a\n- [ ] a\n": (0, b"", b"", b"- [x] a\n- [X] a\n- [x] a\n", False),
    }


def test_main_raises_out_of_main_on_a_missing_ledger_rather_than_returning_a_code(
        tmp_path, capsysbinary, tick_ledger):
    with pytest.raises(FileNotFoundError):
        tick_ledger.main([str(tmp_path / "missing.md"), "a"])


def test_main_returns_2_on_a_directory_as_the_ledger_with_one_stderr_line_naming_it(
        tmp_path, capsysbinary, tick_ledger):
    code = tick_ledger.main([str(tmp_path), "a"])
    out, err = capsysbinary.readouterr()
    assert (code, out) == (2, b"")
    assert err.decode() == f"tick-ledger.sh: {tmp_path}: Is a directory\n"


def test_main_ticks_a_criterion_notation_step_by_a_matcher_carrying_its_criterion_marker_and_marks_it_refactor_pending(
        tmp_path, capsysbinary, tick_ledger):
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes("- [x] add lowercasing ⟦criterion 1⟧\n- [ ] collapse to single hyphen ⟦criterion 1⟧\n"
                       "- [ ] strip edge hyphens\n".encode())
    code = tick_ledger.main(["--refactor-pending", str(ledger), "collapse to single hyphen ⟦criterion 1⟧"])
    out, _ = capsysbinary.readouterr()

    assert (code, out, ledger.read_bytes().decode().split("\n")[1]) == (
        0, b"", "- [x] collapse to single hyphen ⟦criterion 1⟧ ⟂ refactor pending")


def test_main_leaves_the_ledger_byte_identical_and_returns_2_when_writing_the_ticked_ledger_fails_817(
        tmp_path, capsysbinary, tick_ledger):
    seed = "".join(f"- [ ] step {n} of a ledger long enough to outgrow the file size limit\n" for n in range(8)).encode()
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)
    soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
    resource.setrlimit(resource.RLIMIT_FSIZE, (64, hard))
    try:
        code = tick_ledger.main([str(ledger), "step 3"])
    except OSError as error:
        code = type(error).__name__
    finally:
        resource.setrlimit(resource.RLIMIT_FSIZE, (soft, hard))
    capsysbinary.readouterr()

    assert (code, ledger.read_bytes()) == (2, seed)


def test_main_keeps_the_ledger_file_permissions_when_it_ticks_a_step_817(tmp_path, capsysbinary, tick_ledger):
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(b"- [ ] alpha\n")
    ledger.chmod(0o640)

    code = tick_ledger.main([str(ledger), "alpha"])
    capsysbinary.readouterr()

    assert (code, oct(ledger.stat().st_mode & 0o777)) == (0, oct(0o640))


def test_main_leaves_no_file_but_the_ledger_beside_it_when_writing_the_ticked_ledger_fails_817(
        tmp_path, capsysbinary, tick_ledger):
    seed = "".join(f"- [ ] step {n} of a ledger long enough to outgrow the file size limit\n" for n in range(8)).encode()
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)
    soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
    resource.setrlimit(resource.RLIMIT_FSIZE, (64, hard))
    try:
        code = tick_ledger.main([str(ledger), "step 3"])
    except OSError as error:
        code = type(error).__name__
    finally:
        resource.setrlimit(resource.RLIMIT_FSIZE, (soft, hard))
    capsysbinary.readouterr()

    assert (code, sorted(path.name for path in tmp_path.iterdir())) == (2, ["ledger.md"])


def test_main_leaves_the_ledger_byte_identical_and_returns_2_when_the_temporary_file_beside_it_cannot_be_created_817(
        tmp_path, capsysbinary, tick_ledger, monkeypatch):
    seed = b"- [ ] alpha\n- [ ] beta\n"
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)
    real_open = os.open

    def refusing_open(path, *args, **kwargs):
        if os.path.dirname(os.path.abspath(path)) == str(tmp_path) and os.path.abspath(path) != str(ledger):
            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC), path)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(os, "open", refusing_open)
    try:
        code = tick_ledger.main([str(ledger), "beta"])
    except OSError as error:
        code = type(error).__name__
    monkeypatch.undo()
    capsysbinary.readouterr()

    assert (code, ledger.read_bytes()) == (2, seed)
