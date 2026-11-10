before 40
18d5d2c05e6824522de639f4f8e3b0225c4db3e6
keep 63
skills/tdd/scripts/tests/py/unit/test_requirements_preflight.py
command 191
make test TESTS=skills/tdd/scripts/tests/py/unit/test_requirements_preflight.py::test_3567_a_ledger_line_with_the_skill_edit_marker_that_is_not_a_checkbox_is_ignored_by_the_unit_heading_check

before 40
18d5d2c05e6824522de639f4f8e3b0225c4db3e6
keep 63
skills/tdd/scripts/tests/py/unit/test_requirements_preflight.py
command 164
make test TESTS=skills/tdd/scripts/tests/py/unit/test_requirements_preflight.py::test_3567_a_missing_unit_heading_prints_no_clash_line_while_a_real_clashing_id_does

file 49
skills/tdd/scripts/veri/requirements_preflight.py
old 17
if len(argv) > 1:
new 9
if False:
context 21
    if len(argv) > 1:
command 164
make test TESTS=skills/tdd/scripts/tests/py/unit/test_requirements_preflight.py::test_3567_a_missing_unit_heading_prints_no_clash_line_while_a_real_clashing_id_does

before 40
7b4f34417143dc7a5cf5e181ba677dbf35238407
keep 63
skills/tdd/scripts/tests/py/unit/test_requirements_preflight.py
command 180
make test TESTS=skills/tdd/scripts/tests/py/unit/test_requirements_preflight.py::test_3567_two_missing_skill_edit_units_and_two_clashing_ids_in_one_unit_are_all_named_in_one_exit_2

file 49
skills/tdd/scripts/veri/requirements_preflight.py
old 24
    for unit in missing:
new 28
    for unit in missing[:1]:
context 24
    for unit in missing:
command 180
make test TESTS=skills/tdd/scripts/tests/py/unit/test_requirements_preflight.py::test_3567_two_missing_skill_edit_units_and_two_clashing_ids_in_one_unit_are_all_named_in_one_exit_2

file 49
skills/tdd/scripts/veri/requirements_preflight.py
old 27
    for row_id in clashing:
new 31
    for row_id in clashing[:1]:
context 27
    for row_id in clashing:
command 180
make test TESTS=skills/tdd/scripts/tests/py/unit/test_requirements_preflight.py::test_3567_two_missing_skill_edit_units_and_two_clashing_ids_in_one_unit_are_all_named_in_one_exit_2

