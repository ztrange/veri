"""A mismatched emitted-text pin's failure output says what bytes the pin covers and how to reproduce its checksum."""
import pytest

import test_emitted_text as pins


def test_3368_mismatched_pin_failure_names_covered_bytes_and_reproducing_command(run_cli, monkeypatch):
    monkeypatch.setattr(pins, "USAGE", [("1 1", "tick-ledger.sh", [])])
    with pytest.raises(AssertionError) as raised:
        pins.test_usage_output_on_a_missing_argument_is_unchanged(run_cli)
    message = str(raised.value)
    assert "exit 2" in message
    assert "newline" in message
    assert "printf" in message
    assert "cksum" in message


def test_3368_pin_of_the_bare_usage_bytes_still_fails(run_cli, monkeypatch):
    text = pins.emitted(run_cli, "tick-ledger.sh", [])
    bare = text[len("exit 2\n"):].rstrip("\n")
    monkeypatch.setattr(pins, "USAGE", [(pins.cksum(bare.encode("utf-8", "surrogateescape")), "tick-ledger.sh", [])])
    with pytest.raises(AssertionError):
        pins.test_usage_output_on_a_missing_argument_is_unchanged(run_cli)
