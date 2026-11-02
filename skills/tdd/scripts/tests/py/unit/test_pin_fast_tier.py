"""pin_fast_tier.bounded()'s bound on an over-long fast-tier output."""
import importlib


def test_a_line_over_the_cap_keeps_its_tail_2936():
    pin_fast_tier = importlib.import_module("pin_fast_tier")
    output = b"y" * pin_fast_tier.BOUND_BYTES + b"\n" + b"x" * 2000 + b" FAIL  src/a.test.ts"

    assert len(output) > pin_fast_tier.BOUND_BYTES
    assert b" FAIL  src/a.test.ts" in pin_fast_tier.bounded(output)


def test_a_clip_inside_a_multibyte_character_still_decodes_as_utf8_2936():
    pin_fast_tier = importlib.import_module("pin_fast_tier")
    output = b"y" * pin_fast_tier.BOUND_BYTES + b"\n" + "€".encode() * 2000

    assert len(output) > pin_fast_tier.BOUND_BYTES
    pin_fast_tier.bounded(output).decode("utf-8")


def test_many_fail_blocks_stay_within_the_fail_cap_plus_one_block_and_the_tail_2936():
    pin_fast_tier = importlib.import_module("pin_fast_tier")
    filler = b"f" * 1000
    block = [b" FAIL  src/a.test.ts"] + [filler] * (pin_fast_tier.FAIL_BLOCK_LINES - 1)
    tail = [b"z"] * pin_fast_tier.TAIL_LINES
    output = b"\n".join(block * 20 + tail)

    assert len(output) > pin_fast_tier.BOUND_BYTES
    one_block = sum(len(line) + 1 for line in block)
    tail_bytes = sum(len(line) + 1 for line in tail)
    limit = pin_fast_tier.FAIL_CAP_BYTES + one_block + tail_bytes
    assert len(pin_fast_tier.bounded(output)) <= limit < pin_fast_tier.BOUND_BYTES - 1024
