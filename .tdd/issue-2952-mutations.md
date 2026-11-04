before 40
3958d8e9db77c96490d6a1b1cf21458896b95413
keep 52
skills/tdd/scripts/tests/py/unit/test_tick_ledger.py
command 224
make test TESTS=skills/tdd/scripts/tests/py/unit/test_tick_ledger.py::test_main_refuses_a_tick_of_a_step_naming_a_go_red_control_file_with_regex_metacharacters_when_the_record_names_a_file_the_unescaped_name_would_match_2952
green 40
99321212db3e22a4b62737f8f8b9e03eac45ddcd

file 38
skills/tdd/scripts/veri/tick_ledger.py
old 25
    if before or control:
new 58
    if before or control or "go-red control" in step_line:
command 182
make test TESTS=skills/tdd/scripts/tests/py/unit/test_tick_ledger.py::test_main_ticks_a_step_mentioning_go_red_control_bare_with_neither_wording_and_no_mutation_record_exiting_0_2952

