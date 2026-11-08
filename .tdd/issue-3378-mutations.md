file 43
skills/tdd/scripts/veri/suite_red_resume.py
old 22
if candidates and all(
new 7
if all(
command 233
make test TESTS=skills/tdd/scripts/tests/py/unit/test_suite_red_resume.py::test_insert_still_adds_the_suite_repair_step_before_the_first_of_two_separated_pending_skill_edit_steps_when_a_branch_red_suite_is_red_for_another_reason_3378

file 43
skills/tdd/scripts/veri/suite_red_resume.py
old 44
    if covered_by(pending):
        return 0
new 30
    if False:
        return 0
command 225
make test TESTS=skills/tdd/scripts/tests/py/unit/test_suite_red_resume.py::test_insert_leaves_the_ledger_untouched_and_exits_0_when_two_adjacent_pending_skill_edit_steps_together_explain_a_red_of_both_stale_graded_suites_3378

