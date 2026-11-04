file 46
skills/tdd/scripts/veri/rebase_onto_default.py
old 25
if row != base.get(unit)}
new 9
if False}
command 78
make test TESTS=skills/tdd/scripts/tests/py/test_rebase_graded_only_process.py

file 46
skills/tdd/scripts/veri/rebase_onto_default.py
old 77
and git("diff", "--quiet", "HEAD", "REBASE_HEAD", "--", unit).returncode != 0
new 8
and True
command 190
make test TESTS=skills/tdd/scripts/tests/py/test_rebase_graded_only_process.py::test_3025_graded_only_takes_the_main_row_of_a_unit_whose_file_the_branch_never_changed_over_a_stale_branch_row

