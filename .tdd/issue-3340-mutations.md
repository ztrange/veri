before 40
abff088bc7a81b83db60b5468f4ffa6a3baaa51e
keep 61
skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py
command 360
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpfc6y63ke/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py make test TESTS=skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py::test_3340_criterion_2_a_tests_list_mixing_a_dashboard_case_and_a_veri_case_runs_each_under_its_own_runner_and_exits_0
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
abff088bc7a81b83db60b5468f4ffa6a3baaa51e
keep 61
skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py
command 348
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpfc6y63ke/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py make test TESTS=skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py::test_3340_criterion_2_a_tests_list_mixing_a_passing_dashboard_case_and_a_failing_veri_case_exits_non_zero
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
abff088bc7a81b83db60b5468f4ffa6a3baaa51e
keep 61
skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py
command 169
make test TESTS=skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py::test_3340_criterion_3_a_failing_dashboard_case_named_alone_in_tests_makes_make_test_exit_1
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 8
Makefile
old 57
$(MAKE) -C projects/dashboard test < /dev/null || fail=1;
new 55
$(MAKE) -C projects/dashboard test < /dev/null || true;
command 169
make test TESTS=skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py::test_3340_criterion_3_a_failing_dashboard_case_named_alone_in_tests_makes_make_test_exit_1
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 8
Makefile
old 30
test < /dev/null || fail=1; fi
new 20
test < /dev/null; fi
command 176
make test TESTS=skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py::test_3340_criterion_3_a_failing_dashboard_case_named_alone_in_tests_makes_make_test_exit_non_zero
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

