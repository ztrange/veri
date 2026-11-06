file 43
skills/tdd/scripts/veri/suite_red_resume.py
old 40
named = [unit for unit in listed if all(
new 40
named = [unit for unit in listed if any(
command 226
make test TESTS=skills/tdd/scripts/tests/py/unit/test_suite_red_resume.py::test_insert_with_reds_outside_the_grade_suites_naming_two_different_listed_units_across_the_reds_adds_the_suite_repair_step_and_no_skill_edit_step_3107

