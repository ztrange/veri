before 40
68afd4298b463ca5e975968457bf3844acb25704
keep 56
skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py
command 382
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpe7ro6cbz/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py::test_a_step_whose_issue_row_id_cell_is_id_reword_naming_a_listed_row_with_different_text_rewords_it_under_its_bare_id_and_exits_as_a_reword_does_3320

file 42
skills/tdd/scripts/veri/skill_edit_step.py
old 53
               and _row_text(r) != texts[_row_id(r)]]
new 44
               and _row_text(r) is not None]
command 208
make test TESTS=skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py::test_a_step_whose_issue_row_is_identical_to_the_listed_row_of_the_same_bare_id_refuses_nothing_and_leaves_the_list_byte_identical_3320

