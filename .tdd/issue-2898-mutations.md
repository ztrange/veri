file 39
skills/tdd/scripts/veri/tests_frozen.py
old 31
startswith(("assert", "expect("
new 21
startswith(("expect("
command 72
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 42
                != sorted(verified_lines):
new 52
                != sorted(verified_lines) and False:
command 236
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_names_a_go_case_on_a_skipped_line_and_check_earlier_exits_1_when_a_refactor_moved_its_assertions_into_assert_refused_and_dropped_one_2898

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 37
if head_lines != verified_lines and \
new 14
if False and \
command 241
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_names_a_go_case_on_a_skipped_line_and_check_earlier_exits_1_when_a_refactor_moved_its_assertions_into_assert_refused_and_deleted_the_call_2898

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 32
if handle.read().strip() != "0":
new 9
if False:
command 226
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_exits_3_and_check_earlier_exits_1_when_a_refactor_moved_a_go_cases_assertions_into_assert_refused_and_the_verdict_is_not_0_2898

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 33
if l.split("(")[0] not in called]
new 8
if True]
command 230
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_re_records_a_python_case_without_a_skipped_line_and_check_earlier_exits_0_when_a_refactor_moved_its_assert_into_assert_refused_2898

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 53
                helper_digests[(name, case)] = digest
new 20
                pass
command 212
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_leaves_check_earlier_at_exit_1_when_an_assertion_is_deleted_from_assert_refused_after_a_successful_re_record_2898

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 59
or any(d not in held for d, held in zip(digests, accepted))
new 8
or False
command 208
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_check_earlier_exits_1_when_the_case_body_is_edited_after_a_successful_re_record_into_assert_refused_with_no_second_re_record_2898

