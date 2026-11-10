## mutation: sed 's/for row_id in clashing:/for row_id in clashing[:1]:/' skills/tdd/scripts/veri/requirements_preflight.py
command: make test TESTS="skills/tdd/scripts/tests/py/unit/test_requirements_preflight.py"
```
FAILED skills/tdd/scripts/tests/py/unit/test_requirements_preflight.py::test_3567_an_issue_with_rows_clashing_across_tables_exits_2_naming_every_clashing_id - AssertionError: (2, '', 'Requirement r...
FAILED skills/tdd/scripts/tests/py/unit/test_requirements_preflight.py::test_3567_two_missing_skill_edit_units_and_two_clashing_ids_in_one_unit_are_all_named_in_one_exit_2 - AssertionError: (2, '',...
===================================================================================== 2 failed, 6 passed in 0.11s ======================================================================================
```
restored (git checkout -- skills/tdd/scripts/veri/requirements_preflight.py): 
========================================================================================== 8 passed in 0.10s ===========================================================================================

## mutation: sed 's/for unit in missing:/for unit in missing[:1]:/' skills/tdd/scripts/veri/requirements_preflight.py
command: make test TESTS="skills/tdd/scripts/tests/py/unit/test_requirements_preflight.py"
```
FAILED skills/tdd/scripts/tests/py/unit/test_requirements_preflight.py::test_3567_two_missing_skill_edit_units_and_two_clashing_ids_in_one_unit_are_all_named_in_one_exit_2 - AssertionError: (2, '',...
===================================================================================== 1 failed, 7 passed in 0.09s ======================================================================================
```
restored (git checkout -- skills/tdd/scripts/veri/requirements_preflight.py): 
========================================================================================== 8 passed in 0.09s ===========================================================================================

