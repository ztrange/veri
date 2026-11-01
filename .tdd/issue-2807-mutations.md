file 43
skills/tdd/scripts/veri/wrong_test_route.py
old 35
go_file = name.endswith("_test.go")
new 30
go_file = name.endswith(".go")
command 343
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpplldoej3/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py::test_main_2807_prints_revise_for_a_superseded_line_naming_a_go_func_defined_only_in_a_file_not_named_test_go

file 43
skills/tdd/scripts/veri/wrong_test_route.py
old 35
go_file = name.endswith("_test.go")
new 15
go_file = False
command 332
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpplldoej3/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py::test_main_2807_prints_supersede_naming_both_go_cases_two_superseded_lines_name_from_go_test_files

file 43
skills/tdd/scripts/veri/wrong_test_route.py
old 124
        if not _is_own(case, own_id):
            found = _exists(case)
            if found and not _is_own(found, own_id):
new 72
        if True:
            found = _exists(case)
            if found:
command 313
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpplldoej3/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py::test_main_2807_prints_revise_when_a_wrong_test_names_only_the_step_own_go_case

file 43
skills/tdd/scripts/veri/wrong_test_route.py
old 40
    if case == tail:
        return True
new 41
    if case == tail:
        return False
command 313
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpplldoej3/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py::test_main_2807_prints_revise_when_a_wrong_test_names_only_the_step_own_go_case

