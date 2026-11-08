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

before 40
d8c8d1eae1f096c0f1ca7a4ac644422c74562c5d
keep 51
skills/tdd/scripts/tests/py/unit/test_prd_report.py
command 333
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpti8uesfw/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_prd_report.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_report.py::test_report_eta_line_drops_no_rate_yet_at_three_issues_closed_in_the_last_7_days_and_counts_only_closed_issues

before 40
400f34c97c924e8dba790b9932ddfee5d4050201
keep 51
skills/tdd/scripts/tests/py/unit/test_prd_report.py
command 327
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpn36_8y3w/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_prd_report.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_report.py::test_report_eta_lower_bound_divides_the_left_count_by_the_highest_lane_rate_at_its_fastest_wall_quartile

file 37
skills/tdd/scripts/veri/prd_report.py
old 60
fastest = max(fastest, 86400 / walls[(len(walls) - 1) // 4])
new 67
fastest = min(fastest or 1e9, 86400 / walls[(len(walls) - 1) // 4])
command 173
make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_report.py::test_report_eta_lower_bound_divides_the_left_count_by_the_highest_lane_rate_at_its_fastest_wall_quartile

file 37
skills/tdd/scripts/veri/prd_report.py
old 28
walls[(len(walls) - 1) // 4]
new 22
walls[len(walls) // 2]
command 173
make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_report.py::test_report_eta_lower_bound_divides_the_left_count_by_the_highest_lane_rate_at_its_fastest_wall_quartile

file 37
skills/tdd/scripts/veri/prd_report.py
old 28
len(open_children) / fastest
new 11
1 / fastest
command 173
make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_report.py::test_report_eta_lower_bound_divides_the_left_count_by_the_highest_lane_rate_at_its_fastest_wall_quartile

before 40
81559b0229e2826274094d04deedfa63eccce9d3
keep 51
skills/tdd/scripts/tests/py/unit/test_prd_report.py
command 322
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpljn1ti6p/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_prd_report.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_report.py::test_report_eta_upper_bound_uses_the_slowest_lane_at_its_slowest_wall_quartile_not_its_maximum_wall

file 37
skills/tdd/scripts/veri/prd_report.py
old 33
walls[-1 - (len(walls) - 1) // 4]
new 9
walls[-1]
command 168
make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_report.py::test_report_eta_upper_bound_uses_the_slowest_lane_at_its_slowest_wall_quartile_not_its_maximum_wall

