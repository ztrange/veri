file 38
skills/tdd/scripts/veri/pin_recheck.py
old 35
and not is_go_test_failure(mutated)
new 45
and not is_go_test_failure(mutated) and False
command 331
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmphga4dvoe/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_pin_recheck_process.py make test TESTS=skills/tdd/scripts/tests/py/test_pin_recheck_process.py::test_2875_a_go_build_failure_on_the_mutated_run_still_needs_a_look_and_exits_1_and_restores_the_file

