"""In-process cases for veri/stop_requested.py, the module stop-requested.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def stop_requested():
    return importlib.import_module("veri.stop_requested")


def test_main_answers_a_mode_no_request_a_bad_argument_and_clear_with_their_exit_codes(
        monkeypatch, tmp_path, capsysbinary, stop_requested):
    monkeypatch.chdir(tmp_path)
    stop = tmp_path / ".tdd" / "stop"

    assert stop_requested.main([]) == 3
    assert capsysbinary.readouterr() == (b"", b"")

    stop.parent.mkdir()
    stop.write_bytes(b"now\n")
    assert stop_requested.main([]) == 0
    assert capsysbinary.readouterr() == (b"now\n", b"")

    stop.write_bytes(b"at-ledger\n")
    assert stop_requested.main(["--bogus"]) == 2
    assert capsysbinary.readouterr() == (b"", b"usage: stop-requested.sh [--clear]\n")
    assert stop.read_bytes() == b"at-ledger\n"

    assert stop_requested.main(["--clear"]) == 0
    assert not stop.exists()


def test_main_accepts_a_mode_added_to_stop_modes_and_refuses_one_outside_it_naming_the_list(
        monkeypatch, tmp_path, capsysbinary, stop_requested):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(importlib.import_module("stop_modes"), "STOP_MODES",
                        ("at-ledger", "at-leaf", "now", "at-step"))
    stop = tmp_path / ".tdd" / "stop"
    stop.parent.mkdir()

    stop.write_bytes(b"at-step\n")
    assert stop_requested.main([]) == 0
    assert capsysbinary.readouterr() == (b"at-step\n", b"")

    stop.write_bytes(b"bogus\n")
    assert stop_requested.main([]) == 2
    assert capsysbinary.readouterr() == (
        b"",
        "stop-requested: .tdd/stop must name a mode — at-ledger, at-leaf, now or at-step: 'bogus'\n".encode())


def test_main_reads_its_arguments_as_stop_requested_sh_does(
        monkeypatch, tmp_path, capsysbinary, stop_requested):
    monkeypatch.chdir(tmp_path)
    stop = tmp_path / ".tdd" / "stop"
    stop.parent.mkdir()
    usage = (b"", b"usage: stop-requested.sh [--clear]\n")

    stop.write_bytes(b"now\n")
    assert stop_requested.main(["--clear", "--bogus"]) == 2
    assert capsysbinary.readouterr() == usage
    assert stop.read_bytes() == b"now\n"

    stop.write_bytes(b"bogus\n")
    assert stop_requested.main(["--bogus", "--clear"]) == 2
    assert capsysbinary.readouterr() == usage
    assert stop.read_bytes() == b"bogus\n"

    for word in ("clear", "--CLEAR", "--clear=1", "--bogus"):
        stop.write_bytes(b"at-leaf\n")
        assert stop_requested.main([word]) == 2, word
        assert capsysbinary.readouterr() == usage, word
        assert stop.read_bytes() == b"at-leaf\n", word

    for mode in (b"at-ledger", b"at-leaf", b"now"):
        stop.write_bytes(mode + b"\n")
        assert stop_requested.main([""]) == 0, mode
        assert capsysbinary.readouterr() == (mode + b"\n", b""), mode
        assert stop_requested.main([]) == 0, mode
        assert capsysbinary.readouterr() == (mode + b"\n", b""), mode

    stop.unlink()
    assert stop_requested.main([""]) == 3
    assert capsysbinary.readouterr() == (b"", b"")


def test_main_reads_only_the_first_line_whole_as_stop_requested_sh_does(
        monkeypatch, tmp_path, capsysbinary, stop_requested):
    monkeypatch.chdir(tmp_path)
    stop = tmp_path / ".tdd" / "stop"
    stop.parent.mkdir()

    def refusal(mode):
        return (b"", "stop-requested: .tdd/stop must name a mode — at-ledger, at-leaf or now: '".encode()
                + mode + b"'\n")

    stop.write_bytes(b"now\nbogus\n")
    assert stop_requested.main([]) == 0
    assert capsysbinary.readouterr() == (b"now\n", b"")

    for mode in (b" now", b"now ", b"now\t", b"now\r"):
        stop.write_bytes(mode + b"\n")
        assert stop_requested.main([]) == 2, mode
        assert capsysbinary.readouterr() == refusal(mode), mode

    for content in (b"now", b""):
        stop.write_bytes(content)
        assert stop_requested.main([]) == 2, content
        assert capsysbinary.readouterr() == refusal(b""), content

    stop.write_bytes(b"no\0w\n")
    assert stop_requested.main([]) == 0
    assert capsysbinary.readouterr() == (b"now\n", b"")

    stop.unlink()
    stop.mkdir()
    assert stop_requested.main([]) == 3
    assert capsysbinary.readouterr() == (b"", b"")
    stop.rmdir()

    stop.symlink_to(tmp_path / "nowhere")
    assert stop_requested.main([]) == 3
    assert capsysbinary.readouterr() == (b"", b"")
    stop.unlink()

    stop.write_bytes(b"now\n")
    real_open = open

    def unreadable(path, *args, **kwargs):
        if str(path).endswith(".tdd/stop"):
            raise OSError(5, "Input/output error", str(path))
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", unreadable)
    assert stop_requested.main([]) == 2
    assert capsysbinary.readouterr() == refusal(b"")


def test_main_clear_removes_whatever_is_at_tdd_stop_without_reading_it_as_rm_f_does(
        monkeypatch, tmp_path, capsysbinary, stop_requested):
    monkeypatch.chdir(tmp_path)
    stop = tmp_path / ".tdd" / "stop"

    assert stop_requested.main(["--clear"]) == 0
    assert capsysbinary.readouterr() == (b"", b"")
    assert not (tmp_path / ".tdd").exists()

    stop.parent.mkdir()
    stop.write_bytes(b"bogus\n")
    real_open = open

    def unreadable(path, *args, **kwargs):
        if str(path).endswith(".tdd/stop"):
            raise AssertionError(f"--clear read {path}")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", unreadable)
    assert stop_requested.main(["--clear"]) == 0
    assert capsysbinary.readouterr() == (b"", b"")
    assert not stop.exists()
    monkeypatch.setattr("builtins.open", real_open)

    stop.symlink_to(tmp_path / "nowhere")
    assert stop_requested.main(["--clear"]) == 0
    assert capsysbinary.readouterr() == (b"", b"")
    assert not stop.is_symlink()

    stop.mkdir()
    with pytest.raises(OSError):
        stop_requested.main(["--clear"])
    assert stop.is_dir()


def test_main_passes_non_utf8_bytes_in_the_first_line_through_to_stderr_unchanged(
        monkeypatch, tmp_path, capsysbinary, stop_requested):
    monkeypatch.chdir(tmp_path)
    stop = tmp_path / ".tdd" / "stop"
    stop.parent.mkdir()

    stop.write_bytes(b"n\xffow\n")
    assert stop_requested.main([]) == 2
    assert capsysbinary.readouterr() == (
        b"",
        "stop-requested: .tdd/stop must name a mode — at-ledger, at-leaf or now: '".encode()
        + b"n\xffow'\n")


def test_main_clear_and_a_refused_argument_answer_as_the_bash_cases_did(
        monkeypatch, tmp_path, capsysbinary, stop_requested):
    monkeypatch.chdir(tmp_path)
    stop = tmp_path / ".tdd" / "stop"
    stop.parent.mkdir()

    stop.write_bytes(b"at-ledger\n")
    assert stop_requested.main(["--clear"]) == 0
    assert not stop.exists()
    assert stop_requested.main(["--clear"]) == 0

    for argv in (["--bogus"], ["--clear", "--bogus"]):
        stop.write_bytes(b"at-ledger\n")
        assert stop_requested.main(argv) == 2, argv
        assert stop.read_bytes() == b"at-ledger\n", argv
