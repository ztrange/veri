before 40
4d3e354e862ecbfd27c419aafec0f8ff06a2fbf2
keep 56
skills/tdd/scripts/tests/py/unit/test_add_ledger_step.py
command 173
make test TESTS=skills/tdd/scripts/tests/py/unit/test_add_ledger_step.py::test_3314_a_batch_with_one_text_holding_the_refactor_pending_delimiter_exits_2_inserting_none_of_it

file 42
skills/tdd/scripts/veri/add_ledger_step.py
old 51
if is_repair(text) or planned else f" {ADDED_MARK}"
new 29
if True else f" {ADDED_MARK}"
command 200
make test TESTS=skills/tdd/scripts/tests/py/unit/test_add_ledger_step.py::test_3314_texts_without_the_refactor_pending_delimiter_are_inserted_with_exit_0_each_marked_added_and_counted_by_ledger_growth

