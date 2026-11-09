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
