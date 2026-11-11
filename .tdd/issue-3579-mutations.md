before 40
89f83b88dd46050e32b30ab80b4135c0ae739b79
keep 57
skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py
command 154
make test TESTS=skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py::test_3579_release_by_the_owner_leaves_a_token_file_holding_another_owners_token

before 40
7c5c912c13193716a2818dcf41370ea2033d29ab
keep 57
skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py
command 143
make test TESTS=skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py::test_3579_failed_gate_removes_the_token_file_holding_its_owner_token

file 37
skills/tdd/scripts/veri/merge_lock.py
old 74
        if fields[3:4] != ([owner] if owner else []):
            return 1
new 70
        if fields[3:4] != ([owner] if owner else []):
            pass
context 53
        if fields[3:4] != ([owner] if owner else []):
command 159
make test TESTS=skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py::test_3579_release_by_a_different_owner_token_leaves_the_holders_token_file_untouched

