# Mutation-parity pairs proven for #1350

Every row below is `proven` by the conductor's own `mutation-parity.sh` run against the step's pre-deletion tree with its new pytest file added.

## Step 1 — classify-bail.test.sh (4/4, exit 0)

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| killed-stuck is system | `unit/test_classify_bail.py::test_main_classifies_every_known_cause_as_system_or_process_with_0` | `killed-stuck` moved from the system causes to the process ones in `veri/classify_bail.py` | proven |
| unknown cause exits non-zero | `unit/test_classify_bail.py::test_main_prints_the_category_of_a_known_cause_and_refuses_an_unknown_or_missing_one_with_2` | an unknown cause returns 0 instead of 2 | proven |
| an unknown cause writes its refusal and the usage line on stderr, nothing on stdout, exit 2 | `unit/test_classify_bail.py::test_main_prints_the_category_of_a_known_cause_and_refuses_an_unknown_or_missing_one_with_2` | the refusal drops the usage line | proven |
| classify-bail.sh run through a symlink to the skill directory and from another working directory answers killed-stuck and an unknown cause as it does in place | `test_classify_bail_process.py::test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_answers_as_it_does_in_place` | the shim exits 5 unless its working directory holds `skills/` | proven |

## Step 2 — cover-outcome.test.sh (6/6, exit 0)

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| COVERED: yes exits 0 printing CAUGHT_BY, COVERED: no exits 1, neither exits 2 | `unit/test_cover_outcome.py::test_main_returns_each_exit_code_inside_0_to_3_with_its_stdout_and_stderr_ignoring_arguments` | `COVERED: no` returns 0 instead of 1 | proven |
| #679: COVERED: unreachable or type-only with a PROOF: line exits 3 printing '<kind>: <proof>' | `unit/test_cover_outcome.py::test_main_answers_each_proof_branch_of_unreachable_and_type_only` | a proved unreachable/type-only returns 0 instead of 3 | proven |
| a report with no COVERED: line exits 2, stdout empty, stderr exactly 'cover-outcome: no COVERED: line found' | `unit/test_cover_outcome.py::test_main_returns_each_exit_code_inside_0_to_3_with_its_stdout_and_stderr_ignoring_arguments` | the refusal reads `no COVERED line found` | proven |
| run through a symlink to the skill directory and from another working directory, it answers as in place | `test_cover_outcome_process.py::test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_answers_as_it_does_in_place` | the shim exits 5 when run through a linked skill directory | proven |
| #1089: a CAUGHT_BY: line of a NUL b under COVERED: yes prints ab and exits 0 | `unit/test_cover_outcome.py::test_cli_prints_a_caught_by_line_of_a_nul_b_under_covered_yes_as_ab_and_exits_0` | `report_read` no longer strips NULs | proven |
| #1089: a COVERED: line of y NUL es exits 0, as COVERED: yes does | `unit/test_cover_outcome.py::test_cli_exits_0_for_a_covered_line_of_y_nul_es_as_covered_yes_does` | `report_read` no longer strips NULs | proven |
