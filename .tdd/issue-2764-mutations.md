file 33
skills/tdd/scripts/veri/verify.py
old 34
if tree_before and not tree_after:
new 9
if False:
command 328
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp1g8azw7l/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_verify.py make test TESTS=skills/tdd/scripts/tests/py/test_verify.py::test_verify_sh_does_not_accept_a_pass_from_a_pin_verifier_leaf_that_rewrote_its_mutation_record_and_made_it_unreadable_2764

file 33
skills/tdd/scripts/veri/verify.py
old 60
return after is not None and after.startswith(before or b"")
new 76
return after is not None and before is not None and after.startswith(before)
command 313
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp1g8azw7l/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_verify.py make test TESTS=skills/tdd/scripts/tests/py/test_verify.py::test_verify_sh_accepts_a_pass_from_a_pin_verifier_leaf_that_created_the_mutation_record_that_was_absent_2764

