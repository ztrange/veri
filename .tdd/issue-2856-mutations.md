file 42
skills/tdd/scripts/veri/skill_edit_step.py
old 19
    return rows[2:]
new 13
    return []
command 364
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpeylo18nv/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py::test_a_well_formed_unit_heading_under_requirements_keeps_the_step_exiting_0_with_its_rows_applied_and_an_author_attempt_passed_2856

file 42
skills/tdd/scripts/veri/skill_edit_step.py
old 41
return heading in (unit, unit + " (new)")
new 12
return False
command 364
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpeylo18nv/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py::test_a_well_formed_unit_heading_under_requirements_keeps_the_step_exiting_0_with_its_rows_applied_and_an_author_attempt_passed_2856

file 42
skills/tdd/scripts/veri/skill_edit_step.py
old 75
any(l.strip() == "## Requirements" for l in requirements.read_lines(issue))
new 4
True
command 318
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpeylo18nv/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py::test_a_change_only_step_on_an_issue_with_no_requirements_section_keeps_exiting_0_2856

