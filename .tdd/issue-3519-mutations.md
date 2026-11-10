file 39
skills/tdd/scripts/veri/tests_frozen.py
old 25
and name not in subjects:
new 50
and not any(name.startswith(s) for s in subjects):
context 136
                if _digest(name) != expected and not (name == loose and _recorded_cases_intact(record, loose)) and name not in subjects:
command 181
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_check_earlier_exempts_a_guard_subjects_non_red_case_but_not_a_non_subject_whose_path_it_ends_with_3485

