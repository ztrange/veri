file 39
skills/tdd/scripts/veri/tests_frozen.py
old 12
"--reverse",
new 0

context 78
        revs = _git_out("log", "--reverse", "--format=%H", "--", path).split()
command 196
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_earlier_derives_the_step_base_from_its_own_commits_when_an_earlier_plan_commit_introduced_the_step_line_3468

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 33
if name in _guard_subjects(step):
new 58
if any(name.startswith(s) for s in _guard_subjects(step)):
context 57
                        if name in _guard_subjects(step):
command 181
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_check_earlier_exempts_a_guard_subjects_non_red_case_but_not_a_non_subject_whose_path_it_ends_with_3485

