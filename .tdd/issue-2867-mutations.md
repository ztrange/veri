file 39
skills/tdd/scripts/veri/tests_frozen.py
old 73
and _helper_digest(text, "\n".join(nows)) != helper_digests[(name, case)]
new 9
and False
command 362
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpbywfrn84/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tests_frozen_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_check_earlier_exits_1_for_a_python_case_after_an_assert_line_is_deleted_from_its_helper_above_it_following_the_rerecord_2867

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 71
startswith("Test") and re.search(r"\b%s\(" % definition.group(1), body)
new 18
startswith("Test")
command 351
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpbywfrn84/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tests_frozen_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_check_earlier_exits_0_for_a_go_case_after_a_helper_it_does_not_call_is_added_above_it_following_the_rerecord_2867

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 52
and re.search(r"\b%s\(" % definition.group(1), body)
new 8
and True
command 367
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpbywfrn84/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tests_frozen_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_check_earlier_exits_0_for_a_go_case_after_an_assertion_line_is_deleted_from_a_helper_it_does_not_call_following_the_rerecord_2867

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 53
"\n".join(_assertion_lines(_helpers_in(text, body))))
new 24
_helpers_in(text, body))
command 362
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpbywfrn84/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tests_frozen_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_check_earlier_exits_0_for_a_go_case_after_a_helper_it_calls_changes_keeping_every_assertion_line_following_the_rerecord_2867

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 68
not nows or any(d not in held for d, held in zip(digests, accepted))
new 8
not nows
command 360
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpbywfrn84/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tests_frozen_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_check_earlier_passes_a_record_written_without_helper_data_when_nothing_changed_and_exits_1_when_the_case_body_changes_2867

