file 47
skills/tdd/scripts/veri/structural_predicate.py
old 36
    predicate = fields["PREDICATE"]

new 110
    predicate = fields["PREDICATE"]
    if report.split("PREDICATE:", 1)[1].count("\n") > 1:
        return 2

command 156
make test TESTS=skills/tdd/scripts/tests/py/test_structural_predicate.py::test_main_2881_blank_lines_after_a_single_line_predicate_do_not_make_it_multi_line

before 40
1bb2c3dc2da6bd86e77f50645313f8ec7a90bdc8
keep 56
skills/tdd/scripts/tests/py/test_structural_predicate.py
command 369
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpc4913toy/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_structural_predicate.py make test TESTS=skills/tdd/scripts/tests/py/test_structural_predicate.py::test_main_2881_a_trailing_backslash_continuation_predicate_exits_2_naming_the_multi_line_predicate_running_nothing_and_writing_no_record

before 40
1bb2c3dc2da6bd86e77f50645313f8ec7a90bdc8
keep 56
skills/tdd/scripts/tests/py/test_structural_predicate.py
command 362
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpc4913toy/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_structural_predicate.py make test TESTS=skills/tdd/scripts/tests/py/test_structural_predicate.py::test_main_2881_plain_prose_after_the_predicate_line_exits_2_naming_the_multi_line_predicate_running_nothing_and_writing_no_record

