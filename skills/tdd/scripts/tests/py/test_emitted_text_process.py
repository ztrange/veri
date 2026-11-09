"""Cases for the emitted-text cksum pins that run a real shell."""
import importlib.util
import subprocess

import pytest

from conftest import SCRIPTS

UNIT = SCRIPTS / "tests" / "py" / "unit" / "test_emitted_text.py"


@pytest.mark.process("bash running the reproducing command a mismatched emitted-text pin prints")
def test_3368_reproducing_command_of_a_mismatched_pin_prints_the_cksum_the_test_computes(monkeypatch, run_cli):
    spec = importlib.util.spec_from_file_location("emitted_text_pins_under_test", UNIT)
    pins = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pins)
    monkeypatch.setattr(pins, "USAGE", [("1 1", "tick-ledger.sh", [])])

    with pytest.raises(AssertionError) as failure:
        pins.test_usage_output_on_a_missing_argument_is_unchanged(run_cli)

    message = "\n".join(failure.traceback[-1].frame.f_locals["problems"])
    command = [l.split("reproduce:", 1)[1].strip() for l in message.splitlines() if "reproduce:" in l][0]
    computed = pins.cksum(pins.emitted(run_cli, "tick-ledger.sh", []).encode("utf-8", "surrogateescape"))
    ran = subprocess.run(["bash", "-c", command], cwd=SCRIPTS.parents[2], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)
    assert ran.stdout.strip() == computed
