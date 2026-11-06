before 40
95b2e586a4addd93bf58fcf1e02fe99b9abe3986
keep 57
skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py
command 299
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp7hlqu029/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py make unit TESTS=skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py::test_3134_release_by_the_owner_token_that_took_the_lock_frees_it

file 37
skills/tdd/scripts/veri/merge_lock.py
old 17
split()[0] != pid
new 17
split()[0] == pid
command 73
make test TESTS=skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py

before 40
89cfe75a996015dc29b6648ba064d4dca97fbdbc
keep 57
skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py
command 319
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpvu5okj_n/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py::test_3134_failed_gate_under_another_owner_token_of_the_same_pid_leaves_the_lock_held

before 40
89cfe75a996015dc29b6648ba064d4dca97fbdbc
keep 57
skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py
command 164
make test TESTS=skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py::test_3134_take_under_another_owner_token_of_the_same_pid_keeps_waiting_with_the_lock_held

file 37
skills/tdd/scripts/veri/merge_lock.py
old 44
    if "--force" not in args:
        fields
new 27
    if True:
        fields
command 146
make test TESTS=skills/tdd/scripts/tests/py/unit/test_merge_lock_owner.py::test_3134_forced_release_frees_a_lock_taken_with_an_owner_by_a_dead_pid

