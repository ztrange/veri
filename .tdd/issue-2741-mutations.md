file 39
skills/tdd/scripts/veri/failed_cases.py
old 17
if report.failed:
new 25
if report.when == 'call':
command 309
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmps4qso8o5/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_pytest_leg.py make test TESTS=skills/tdd/scripts/tests/py/test_pytest_leg.py::test_2741_a_leg_cut_short_by_an_internalerror_names_only_the_cases_that_failed_not_a_passing_one

file 37
skills/tdd/scripts/veri/pytest_leg.py
old 35
for nodeid in failed_cases.NODEIDS:
new 17
for nodeid in []:
command 309
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmps4qso8o5/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_pytest_leg.py make test TESTS=skills/tdd/scripts/tests/py/test_pytest_leg.py::test_2741_a_leg_cut_short_by_an_internalerror_names_only_the_cases_that_failed_not_a_passing_one

