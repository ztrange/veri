file 59
skills/tdd/scripts/tests/py/test_ignored_signals_process.py
old 23
CHILD_SESSION_WAIT = 60
new 23
CHILD_SESSION_WAIT = 25
command 163
make test TESTS=skills/tdd/scripts/tests/py/test_ignored_signals_process.py::test_the_child_session_wait_outlasts_25_s_and_ends_inside_a_process_cases_timeout_2910

file 59
skills/tdd/scripts/tests/py/test_ignored_signals_process.py
old 46
pytest.fail("the HUP-order case did not finish
new 53
raise RuntimeError("the HUP-order case did not finish
command 161
make test TESTS=skills/tdd/scripts/tests/py/test_ignored_signals_process.py::test_the_hup_order_case_fails_naming_the_wait_when_its_child_outlives_the_bound_2910

