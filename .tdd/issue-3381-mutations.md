before 40
a0595920d04dcae5c0953a02523e7da54641c844
keep 61
skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py
command 180
make test TESTS=skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py::test_3381_criterion_2_make_profile_with_a_tests_list_of_two_dashboard_paths_starts_no_veri_pytest_leg

file 8
Makefile
old 39
$(if $(filter $(DASH_PATH),$(t)),,$(t))
new 4
$(t)
command 233
make test TESTS=skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py::test_3381_criterion_3_a_tests_list_of_one_veri_path_and_two_dashboard_paths_runs_the_pytest_leg_on_the_veri_path_only_and_the_dashboard_runner_on_the_rest

