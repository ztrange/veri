file 39
skills/tdd/scripts/veri/tests_frozen.py
old 72
if head is None or _assertion_lines(head) != _assertion_lines(verified):
new 106
if head is None or not _assertion_lines(verified) or _assertion_lines(head) != _assertion_lines(verified):
command 345
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpacai1c0_/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tests_frozen_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_re_records_a_case_with_no_assertion_line_when_the_refactor_only_changed_whitespace_2809

