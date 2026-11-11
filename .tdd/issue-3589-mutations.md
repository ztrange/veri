before 40
332a4d8f4a93f385340a2489e91d81200a26664e
keep 56
skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py
command 179
make test TESTS=skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py::test_apply_run_twice_on_one_prefix_next_row_leaves_the_section_byte_identical_to_after_the_first_run_3589

file 42
skills/tdd/scripts/veri/skill_edit_step.py
old 30
and _full_text(r) not in held]
new 13
and not held]
context 83
    new = [r for r in rows if _row_id(r) not in have and _full_text(r) not in held]
command 195
make test TESTS=skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py::test_apply_still_appends_a_prefix_next_row_whose_requirement_text_differs_from_every_held_row_under_the_next_free_id_3589

file 42
skills/tdd/scripts/veri/skill_edit_step.py
old 41
tuple(requirements.split_cells(row)[2:4])
new 41
tuple(requirements.split_cells(row)[2:3])
context 52
    return tuple(requirements.split_cells(row)[2:4])
command 207
make test TESTS=skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py::test_apply_still_appends_a_prefix_next_row_whose_requirement_text_equals_a_held_row_but_whose_why_differs_under_the_next_free_id_3589

