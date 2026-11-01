file 39
skills/tdd/scripts/veri/tests_frozen.py
old 72
if head is None or _assertion_lines(head) != _assertion_lines(verified):
new 16
if head is None:
command 348
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpnt8mutq7/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tests_frozen_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_leaves_a_go_cases_record_when_the_refactor_deleted_its_t_fatal_line_without_moving_it_2837

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 91
not definition.group(1).startswith("Test") and not definition.group(1).startswith("test") \
new 6
True \
command 184
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_leaves_a_go_cases_record_when_its_t_fatal_lines_moved_into_another_test_function_2837

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 96
head_lines + _assertion_lines(_called_helpers("HEAD", name, head)) != _assertion_lines(verified)
new 5
False
command 355
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpoh1df7w0/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tests_frozen_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_leaves_a_go_cases_record_when_a_later_commit_deleted_a_t_fatal_line_from_the_helper_it_calls_2837

