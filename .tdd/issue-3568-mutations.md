file 43
skills/tdd/scripts/veri/skill_edit_guard.py
old 7
pr-body
new 7
prXbody
context 72
LEDGER = re.compile(r"\.tdd/issue-\d+(-added|-mutations|-pr-body)?\.md")
command 182
make test TESTS=skills/tdd/scripts/tests/py/test_skill_edit_guard_process.py::test_skill_edit_guard_3568_untracked_stray_file_beside_the_pr_body_prints_only_the_stray_file_and_exit_1

before 40
89f83b88dd46050e32b30ab80b4135c0ae739b79
keep 60
skills/tdd/scripts/tests/py/test_skill_edit_guard_process.py
command 182
make test TESTS=skills/tdd/scripts/tests/py/test_skill_edit_guard_process.py::test_skill_edit_guard_3568_untracked_stray_file_beside_the_pr_body_prints_only_the_stray_file_and_exit_1

