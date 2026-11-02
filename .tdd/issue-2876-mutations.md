file 38
skills/tdd/scripts/veri/pin_recheck.py
old 31
green = mutated.returncode == 0
new 12
green = True
command 336
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpyvaw57ez/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_pin_recheck_process.py make test TESTS=skills/tdd/scripts/tests/py/test_pin_recheck_process.py::test_2876_a_command_that_runs_its_test_passing_clean_and_failing_mutated_reports_the_pin_held_and_exits_0

file 38
skills/tdd/scripts/veri/pin_recheck.py
old 27
if control.returncode == 0:
new 27
if control.returncode >= 0:
command 346
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpyvaw57ez/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_pin_recheck_process.py make test TESTS=skills/tdd/scripts/tests/py/test_pin_recheck_process.py::test_2876_a_command_that_reads_its_file_and_passes_clean_and_mutated_still_reports_the_pin_stayed_green_and_exits_1

