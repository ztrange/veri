before 40
58855a40b58832d399de0a90ccf1ee2038ed676d
keep 47
skills/tdd/scripts/tests/py/unit/test_growth.py
command 313
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpukohdusu/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_growth.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_growth.py::test_growth_skips_records_with_no_usage_so_a_later_one_leaves_the_context_at_the_last_usage_record

file 33
skills/tdd/scripts/veri/growth.py
old 64
usage = record.get("message", {}).get("usage")
        if usage:
new 151
usage = record.get("message", {}).get("usage") or {"input_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
        if usage:
command 163
make test TESTS=skills/tdd/scripts/tests/py/unit/test_growth.py::test_growth_skips_records_with_no_usage_so_a_later_one_leaves_the_context_at_the_last_usage_record

