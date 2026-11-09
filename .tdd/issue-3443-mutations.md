file 39
skills/tdd/scripts/veri/tests_frozen.py
old 67
if name in _guard_subjects(step):
                            added
new 83
if any(s in name for s in _guard_subjects(step)):
                            added
context 57
                        if name in _guard_subjects(step):
command 179
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_check_earlier_exits_1_naming_a_changed_case_in_a_file_whose_path_only_ends_with_a_guard_subject_3443

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 33
if name in _guard_subjects(step):
new 56
if any(s.endswith(name) for s in _guard_subjects(step)):
context 57
                        if name in _guard_subjects(step):
command 179
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_check_earlier_exits_1_naming_a_changed_case_in_a_file_whose_path_is_a_suffix_of_a_guard_subject_3443

