before 40
71622ef896461325d6468d0d57b6943ee1e14c85
keep 57
skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py
command 169
make test TESTS=skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py::test_main_3367_prints_a_file_qualified_contradicted_id_as_given_without_resolving_a_file_again

file 43
skills/tdd/scripts/veri/wrong_test_route.py
old 50
if case is not None and "::" not in case else None
new 29
if case is not None else None
context 83
    where = _defining_file(case) if case is not None and "::" not in case else None
command 169
make test TESTS=skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py::test_main_3367_prints_a_file_qualified_contradicted_id_as_given_without_resolving_a_file_again

before 40
4e442fc6e1761901c23ff78d6f66363392e8dc08
keep 57
skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py
command 177
make test TESTS=skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py::test_main_3367_exits_2_printing_no_route_and_no_file_for_a_bare_contradicted_case_no_test_file_defines

file 43
skills/tdd/scripts/veri/wrong_test_route.py
old 52
if case is None and not rerouted and any(not _is_own
new 62
if False and case is None and not rerouted and any(not _is_own
context 121
    if case is None and not rerouted and any(not _is_own(c, argv[1]) and not _exists(c) for c in _contradicted(argv[0])):
command 177
make test TESTS=skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py::test_main_3367_exits_2_printing_no_route_and_no_file_for_a_bare_contradicted_case_no_test_file_defines

