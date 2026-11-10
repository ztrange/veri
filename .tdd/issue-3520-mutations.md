file 35
skills/tdd/scripts/veri/dispatch.py
old 33
        or not argv[1].isdigit()

new 0

context 32
        or not argv[1].isdigit()
command 182
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_with_a_negative_or_non_integer_target_prints_the_usage_on_stderr_and_exits_2_launching_nothing_issue_3520

before 40
8514dd9e40a9f57deae9ebfc8bd6a410b2c5ba8d
keep 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
command 172
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_with_target_0_an_empty_queue_and_no_live_run_prints_no_queue_empty_and_keeps_waiting_issue_3520

before 40
8514dd9e40a9f57deae9ebfc8bd6a410b2c5ba8d
keep 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
command 178
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_with_target_0_and_a_live_run_that_exits_prints_its_done_line_and_exits_0_launching_nothing_issue_3520

