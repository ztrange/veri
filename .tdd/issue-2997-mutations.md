before 40
3d76eac8fdeeab3cf51cf78b0f475a7bc5c686fd
keep 56
skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py
command 205
make test TESTS=skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py::test_an_added_step_whose_issue_rewords_a_listed_row_on_a_unit_graded_pass_appends_a_skill_edit_no_author_event_naming_the_unit_2997
green 40
e1890a0cba2989d70333a680b05d9c83a8013cf9

file 42
skills/tdd/scripts/veri/skill_edit_step.py
old 70
if added is not None and graded == 0 and change is None and not fresh:
new 66
if added is not None and graded == 0 and change is None and False:
command 213
make test TESTS=skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py::test_an_added_step_on_a_unit_graded_pass_exits_2_naming_the_step_leaving_the_list_unchanged_when_every_issue_row_equals_its_listed_row_2997

