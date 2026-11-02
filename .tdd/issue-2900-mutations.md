file 41
skills/tdd/scripts/veri/mutation_probe.py
old 34
return 1 if returncode == 0 else 0
new 34
return 0 if returncode == 0 else 1
command 355
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpjmr40g3r/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_mutation_probe_process.py make test TESTS=skills/tdd/scripts/tests/py/test_mutation_probe_process.py::test_issue_2900_before_state_probe_exits_1_when_the_test_stays_green_on_the_branch_point_and_leaves_the_tree_unchanged

file 41
skills/tdd/scripts/veri/mutation_probe.py
old 25
if name and name != keep:
new 8
if name:
command 455
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpjmr40g3r/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_mutation_probe_process.py::test_issue_2900_before_state_probe_leaves_a_kept_file_that_differs_from_the_sha_as_it_is_in_the_working_tree make test TESTS=skills/tdd/scripts/tests/py/test_mutation_probe_process.py::test_issue_2900_before_state_probe_leaves_a_kept_file_that_differs_from_the_sha_as_it_is_in_the_working_tree

file 41
skills/tdd/scripts/veri/mutation_probe.py
old 25
name and name != keep and
new 8
name and
command 205
make test TESTS=skills/tdd/scripts/tests/py/test_mutation_probe_process.py::test_issue_2900_before_state_probe_keeps_a_test_path_that_is_new_since_the_sha_with_its_working_tree_bytes_while_the_command_runs

