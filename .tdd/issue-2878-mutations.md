file 43
skills/tdd/scripts/veri/wrong_test_route.py
old 56
    if case is None:
        write(sys.stdout, "revise")
new 58
    if case is None:
        write(sys.stdout, "decision")
command 324
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp3_f3ut08/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py::test_main_2878_prints_revise_and_exits_3_for_a_green_report_whose_wrong_test_line_is_none

file 43
skills/tdd/scripts/veri/wrong_test_route.py
old 56
    if case is None:
        write(sys.stdout, "revise")
new 58
    if case is None:
        write(sys.stdout, "decision")
command 345
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp3_f3ut08/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py::test_main_2878_prints_revise_and_exits_3_for_an_unparseable_wrong_test_once_the_step_log_holds_a_reroute_event

file 43
skills/tdd/scripts/veri/wrong_test_route.py
old 41
yield from re.findall(r"`([^`]+)`", line)
new 4
pass
command 345
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp3_f3ut08/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py bash -c make test TESTS="skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py::test_main_2878_routes_a_wrong_test_naming_another_existing_case_in_backticks_to_a_red_over_that_case"

