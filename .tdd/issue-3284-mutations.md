file 39
skills/tdd/scripts/veri/tests_frozen.py
old 52
        except OSError:
            nows = olds = []
new 44
        except OSError:
            continue
command 178
make test TESTS=skills/tdd/scripts/tests/py/unit/test_tests_frozen.py::test_check_earlier_refuses_a_case_whose_test_file_is_deleted_with_no_counterpart_at_any_path_naming_it_3284

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 29
not nows or any(d not in held
new 17
any(d not in held
command 188
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_check_earlier_exits_1_naming_a_case_whose_test_file_was_git_mv_ed_with_its_assertion_changed_in_the_move_3284

