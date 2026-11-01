file 38
skills/tdd/scripts/veri/pin_recheck.py
old 66
green = subprocess.run(pin["command"], shell=True).returncode == 0
new 150
green = subprocess.run(pin["command"], shell=True).returncode == 0
        if not green:
            sys.stdout.write("needs a look: x\n"); status = 1
command 195
bash -c make test TESTS="skills/tdd/scripts/tests/py/test_pin_recheck_process.py::test_2827_a_mutated_run_that_exits_non_zero_and_still_prints_the_unmutated_result_line_counts_as_red_and_exits_0"

