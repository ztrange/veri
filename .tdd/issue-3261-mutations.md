before 40
696fa4959ff21b0d5150d2c66e6646898d641f80
keep 51
skills/tdd/scripts/tests/py/unit/test_prd_report.py
command 309
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmp900vgvli/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_prd_report.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_report.py::test_report_left_line_waiting_count_is_the_distinct_open_children_with_an_open_blocker

file 37
skills/tdd/scripts/veri/prd_report.py
old 28
len({n for n, _ in waiting})
new 12
len(waiting)
command 155
make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_report.py::test_report_left_line_waiting_count_is_the_distinct_open_children_with_an_open_blocker

before 40
696fa4959ff21b0d5150d2c66e6646898d641f80
keep 51
skills/tdd/scripts/tests/py/unit/test_prd_report.py
command 146
make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_report.py::test_report_left_line_names_a_blocker_shared_by_several_waiting_children_once

file 37
skills/tdd/scripts/veri/prd_report.py
old 41
for b in sorted({b for _, b in waiting}))
new 48
for _, b in sorted(waiting, key=lambda w: w[1]))
command 146
make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_report.py::test_report_left_line_names_a_blocker_shared_by_several_waiting_children_once

