before 40
8154d977edf8b56807db15db4e7766255677184a
keep 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
command 206
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_with_no_target_ignores_a_role_dev_state_override_naming_an_issue_not_among_the_solvable_ones_and_launches_the_next_override_issue

file 35
skills/tdd/scripts/veri/dispatch.py
old 35
if named and named.group() in free:
new 9
if named:
context 59
                        if named and named.group() in free:
command 206
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_with_no_target_ignores_a_role_dev_state_override_naming_an_issue_not_among_the_solvable_ones_and_launches_the_next_override_issue

before 40
8154d977edf8b56807db15db4e7766255677184a
keep 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
command 166
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_with_no_target_keeps_the_n_line_in_force_once_a_role_dev_state_timed_n_change_has_expired

file 35
skills/tdd/scripts/veri/dispatch.py
old 21
if clock() < datetime
new 29
if True or clock() < datetime
context 76
                    if clock() < datetime.fromisoformat(expiry).timestamp():
command 166
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_with_no_target_keeps_the_n_line_in_force_once_a_role_dev_state_timed_n_change_has_expired

