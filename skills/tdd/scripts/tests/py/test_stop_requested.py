"""In-process cases for veri/stop_requested.py, the module stop-requested.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


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
