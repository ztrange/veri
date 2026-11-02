file 40
skills/tdd/scripts/veri/pin_fast_tier.py
old 26
FAIL_CAP_BYTES = 64 * 1024
new 34
FAIL_CAP_BYTES = 128 * 1024 - 1024
command 151
make test TESTS=skills/tdd/scripts/tests/py/unit/test_pin_fast_tier.py::test_many_fail_blocks_stay_within_the_fail_cap_plus_one_block_and_the_tail_2936

