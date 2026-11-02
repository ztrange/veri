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

