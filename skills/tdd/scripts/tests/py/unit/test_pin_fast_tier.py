"""pin_fast_tier.bounded()'s bound on an over-long fast-tier output."""
import importlib


def test_a_line_over_the_cap_keeps_its_tail_2936():
    pin_fast_tier = importlib.import_module("pin_fast_tier")
    output = b"y" * pin_fast_tier.BOUND_BYTES + b"\n" + b"x" * 2000 + b" FAIL  src/a.test.ts"

    assert len(output) > pin_fast_tier.BOUND_BYTES
    assert b" FAIL  src/a.test.ts" in pin_fast_tier.bounded(output)
