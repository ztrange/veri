file 8
Makefile
old 39
$(if $(filter $(DASH_PATH),$(t)),,$(t))
new 4
$(t)
command 183
make test TESTS=skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py::test_3392_make_unit_with_one_veri_path_and_two_dashboard_paths_runs_the_pytest_leg_on_the_veri_path_only

