before 40
57b4449cfe5526412f566f2233b7bc24b65dc8b2
keep 43
skills/tdd/scripts/tests/py/test_metrics.py
command 270
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpeg5rhwsr/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_metrics.py make test TESTS=skills/tdd/scripts/tests/py/test_metrics.py::test_refactor_totals_sum_every_pass_of_a_step_not_just_the_last

before 40
6b82c14c15027e3bd3618a806dd1679dc476fb32
keep 43
skills/tdd/scripts/tests/py/test_metrics.py
command 326
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmp2ignadtb/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_metrics.py make test TESTS=skills/tdd/scripts/tests/py/test_metrics.py::test_issue_row_counts_a_structural_pass_that_landed_transforms_as_a_pass_with_its_transforms_and_not_as_landing_nothing

file 34
skills/tdd/scripts/veri/metrics.py
old 52
every + [structural] if structural_marked else every
new 74
every + [dict(structural, transforms="0")] if structural_marked else every
command 180
make test TESTS=skills/tdd/scripts/tests/py/test_metrics.py::test_issue_row_counts_a_structural_pass_that_landed_transforms_as_a_pass_with_its_transforms_and_not_as_landing_nothing

file 34
skills/tdd/scripts/veri/metrics.py
old 35
    if passes or structural_marked:
new 12
    if True:
command 157
make test TESTS=skills/tdd/scripts/tests/py/test_metrics.py::test_a_run_with_no_refactor_event_and_no_structural_pass_event_prints_no_refactor_totals_section

