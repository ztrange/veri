file 40
skills/tdd/scripts/veri/pin_fast_tier.py
old 29
if len(output) <= BOUND_BYTES
new 28
if len(output) < BOUND_BYTES
command 179
make test TESTS=skills/tdd/scripts/tests/py/test_pin_fast_tier_process.py::test_a_failing_fast_command_with_output_exactly_at_the_bound_leaves_it_unchanged_in_the_reason_file_2909

