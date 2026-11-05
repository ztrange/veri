file 39
skills/tdd/scripts/veri/tests_frozen.py
old 73
return 0 if _rewrite_records(_earlier_records(lines, ""), rewrite) else 2
new 73
return 1 if _rewrite_records(_earlier_records(lines, ""), rewrite) else 2
command 171
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_exits_0_having_skipped_a_case_whose_record_is_already_at_heads_body_3051

