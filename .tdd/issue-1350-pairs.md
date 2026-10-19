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

## Step 3 — red-divergence.test.sh (6/6, exit 0)

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| DIVERGED report exits 0 and prints its PREDICTED_FAILURE, FAIL_OUTPUT and PREDICTION_NOTE | `unit/test_red_divergence.py::test_main_reads_its_report_through_report_read_and_returns_each_exit_code_inside_0_to_3_with_its_stdout_and_stderr_ignoring_arguments` | the reason prints PREDICTED_FAILURE where FAIL_OUTPUT belongs | proven |
| MATCHED report exits 3 and prints nothing | same | MATCHED returns 0 instead of 3 | proven |
| report with no PREDICTION: line, or an unrecognised value, exits 2 | same | an unreadable verdict returns 3 instead of 2 | proven |
| every verdict the leaf prompts offer on their PREDICTION: line is one the parser reads | `unit/test_red_divergence.py::test_cli_reads_every_verdict_the_leaf_prompts_offer_on_their_prediction_line` | the parser no longer reads `MATCHED` | proven |
| report with no PREDICTION: line exits 2 with nothing on stdout and nothing on stderr | `unit/test_red_divergence.py::test_main_reads_its_report_…_ignoring_arguments` | an unreadable verdict writes `no verdict` on stderr | proven |
| run through a symlink to the skill directory and from another working directory, it answers as in place | `test_red_divergence_process.py::test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_answers_as_it_does_in_place` | the shim exits 5 when run through a linked skill directory | proven |

## Step 4 — comment-class.test.sh (9/9, exit 0)

The six header-block rows mutate a suite's header (a test file), the one thing those audits read.

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| a comment in code outside any heredoc is reported as class 1 with its file and line | `test_comment_class.py::test_cli_reports_a_comment_in_code_outside_any_heredoc_as_class_1_with_its_file_and_line` | a comment in code is reported as class 4 | proven |
| comment-class.sh with no argument, and with --sweepable alone, exits 2 with empty stdout and only its usage line on stderr | `test_comment_class.py::test_cli_with_no_argument_and_with_sweepable_alone_exits_2_with_empty_stdout_and_only_its_usage_line_on_stderr` | the usage line drops `[--sweepable]` | proven |
| comment-class.sh, run through a symlink to the skill directory and from another working directory, prints the same lines and exit code as when run in place | `test_comment_class_process.py::test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_prints_the_same_lines_and_exit_code_as_in_place` | the shim exits 5 when run through a linked skill directory | proven |
| no line of the leading header block of a top-level tests/*.sh whose name starts with a through e cites an issue number | `test_comment_class.py::test_cli_no_header_line_of_a_top_level_suite_from_a_through_e_cites_an_issue_number` | `affected-suites.test.sh`'s header gains `# Seen in #123.` | proven |
| the leading header block of a top-level tests/*.sh whose name starts with a through e holds only a description, its Contract under test block and its Run: line | `test_comment_class.py::test_cli_a_top_level_suite_header_from_a_through_e_holds_only_a_description_its_contract_block_and_its_run_line` | `affected-suites.test.sh`'s header gains a stray note paragraph | proven |
| the leading header block of a top-level tests/*.sh whose name starts with f through p carries only its contract, and no line of it cites an issue number | `test_comment_class.py::test_cli_a_top_level_suite_header_from_f_through_p_carries_only_its_contract_and_cites_no_issue_number` | `harness-fixtures.test.sh`'s header gains `# Seen in #123.` | proven |
| the leading header block of a top-level tests/*.sh whose name starts with q through z, other than the skill-* files, carries only its contract, and no line of it cites an issue number | `test_comment_class.py::test_cli_a_top_level_suite_header_from_q_through_z_other_than_skill_files_carries_only_its_contract_and_cites_no_issue_number` | `recipe-unit-tier-guard.test.sh`'s header gains `# Seen in #123.` | proven |
| the leading header block of every tests/skill-*.test.sh whose name after skill- starts with m through z carries only its contract, and no line of it cites an issue number | `test_comment_class.py::test_cli_a_skill_suite_header_from_m_through_z_carries_only_its_contract_and_cites_no_issue_number` | `skill-tests-frozen.test.sh`'s header gains `# Seen in #123.` | proven |
| the leading header block of every shell file under tests/unit/, tests/fixtures/, tests/unit-guard/ and tests/offline/ carries only its contract, and no line of it cites an issue number | `test_comment_class.py::test_cli_a_header_under_unit_fixtures_unit_guard_and_offline_carries_only_its_contract_and_cites_no_issue_number` | `unit/candidate-line.test.sh`'s header gains `# Seen in #123.` | proven |
