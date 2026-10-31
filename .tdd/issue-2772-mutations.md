file 33
skills/tdd/scripts/veri/verify.py
old 48
changed == [own_record] and not record_irregular
new 23
changed == [own_record]
command 334
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpq8d0qw0t/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_verify.py make test TESTS=skills/tdd/scripts/tests/py/test_verify.py::test_verify_sh_does_not_accept_a_pass_from_a_pin_verifier_leaf_that_replaced_a_directory_mutation_record_with_a_regular_file_2772

file 33
skills/tdd/scripts/veri/verify.py
old 60
return after is not None and after.startswith(before or b"")
new 76
return after is not None and before is not None and after.startswith(before)
command 314
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpq8d0qw0t/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_verify.py make test TESTS=skills/tdd/scripts/tests/py/test_verify.py::test_verify_sh_still_accepts_a_pass_from_a_pin_verifier_leaf_that_created_a_truly_absent_mutation_record_2772

