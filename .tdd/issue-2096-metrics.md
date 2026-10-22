### 📊 Metrics — issue 2096

Wall time for the issue: 2214 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2128.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.58 over 54 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 86114 |
| 2 | $0.03 | 87457 |
| 3 | $0.03 | 88695 |
| 4 | $0.13 | 102251 |
| 5 | $0.04 | 104187 |
| 6 | $0.02 | 104550 |
| 7 | $0.02 | 104986 |
| 8 | $0.02 | 105283 |
| 9 | $0.02 | 105666 |
| 10 | $0.03 | 106217 |
| 11 | $0.02 | 106654 |
| 12 | $0.02 | 107043 |
| 13 | $0.03 | 107658 |
| 14 | $0.03 | 108441 |
| 15 | $0.05 | 111482 |
| 16 | $0.07 | 116958 |
| 17 | $0.05 | 119676 |
| 18 | $0.09 | 127920 |
| 19 | $0.03 | 128387 |
| 20 | $0.03 | 128989 |
| 21 | $0.03 | 129564 |
| 22 | $0.03 | 130653 |
| 23 | $0.03 | 130962 |
| 24 | $0.03 | 131842 |
| 25 | $0.03 | 132315 |
| 26 | $0.03 | 132860 |
| 27 | $0.04 | 134649 |
| 28 | $0.03 | 135009 |
| 29 | $0.05 | 137997 |
| 30 | $0.04 | 139110 |
| 31 | $0.03 | 139491 |
| 32 | $0.03 | 140229 |
| 33 | $0.08 | 147291 |
| 34 | $0.04 | 148324 |
| 35 | $0.03 | 148819 |
| 36 | $0.03 | 149243 |
| 37 | $0.03 | 149758 |
| 38 | $0.04 | 150396 |
| 39 | $0.04 | 151104 |
| 40 | $0.04 | 151935 |
| 41 | $0.04 | 152630 |
| 42 | $0.04 | 153558 |
| 43 | $0.04 | 154860 |
| 44 | $0.05 | 157322 |
| 45 | $0.04 | 158041 |
| 46 | $0.03 | 158328 |
| 47 | $0.04 | 159158 |
| 48 | $0.03 | 159544 |
| 49 | $0.03 | 159837 |
| 50 | $0.04 | 160383 |
| 51 | $0.04 | 160805 |
| 52 | $0.04 | 161229 |
| 53 | $0.03 | 161572 |
| 54 | $0.04 | 162144 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 9 | 1 | 2 | 1263 | 0 | 44725 | 0.12 |
| prose | 2 | 0 | 0 | 0 | 109 | 103 | 2 | 4 | 16916 | 1298 | 171877 | 0.60 |
| diff | 16 | 6 | 2 | 0 | 904 | 399 | 96 | 190 | 34011 | 3831067 | 531505 | 2.33 |
| red | 1 | 0 | 0 | 0 | 179 | 75 | 13 | 26 | 6419 | 613271 | 38722 | 0.22 |
| pin | 1 | 1 | 0 | 0 | 57 | 23 | 4 | 6 | 1200 | 100671 | 27030 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 8 | 2 | 0 | 467 | 178 | 39 | 76 | 13719 | 1325860 | 294655 | 1.01 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 440 | 211 | 46 | 90 | 18815 | 2029887 | 201767 | 0.90 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 247 | 117 | 29 | 58 | 10359 | 1189262 | 145560 | 0.87 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| diff | 458 | 1.29 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `unit/test_skill_suite_runs.py` deletes skill_md_s_green_entry_says_develop_green_keeps_the_fast_tier_plus_the_affected_suites_green_not_the_full_suite (CY35) and test_1568 skill_md_runs_suite_reported_sh_develop_green_between_the_leaf_s_wait_and_verify_green_s_launch (CY37, CY38), and skill_md_names_no_full_suite_run_inside_a_step_s_cycle loses only its check of the Green text (CY51), keeping every other check; the test_698 and test_991 helper cases stay; helpers nothing calls any more are removed; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 9 | 18 | 2979 | 321258 | 75187 | 0.25 | 156 | n/a | n/a | n/a |  |  | full |
| `unit/test_skill_tests_frozen.py` deletes green_routes_a_wrong_test_report_through_wrong_test_route_by_exit_code (CY39–CY42), green_wrong_test_repair_route_launches_red_repair (CY41), green_wrong_test_routing_carries_the_exit_3_and_exit_2_lines (CY43) and green_section_runs_tests_frozen_check_between_develop_green_and_verify_green_rejecting_on_exit_1 (CY44, CY45); revising_routes_a_revise_green_wrong_test_report (CY38), green_and_revising_send_a_missing_behaviour_answer_to_red_missing (CY42) and green_and_revising_handle_check_exit_2 (CY45) lose only their Green assertions and keep their REVISE.md halves; every_tests_frozen_record_and_check_names_the_record_by_path loses only Green's `check --step` line assertion (CY44), keeping the rest; helpers nothing calls any more are removed; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 100 | 21 | 42 | 7933 | 790123 | 135985 | 0.65 | 341 | 1/2 | unknown | unknown |  |  | full |
| `unit/test_skill_green_split.py` deletes skill_md_s_green_section_on_split_restores_the_tree_to_head (CY46–CY49); skill_md_s_green_section_bails_with_cause_step_too_big (CY50) keeps only its BAIL.md classification half; test_1281 three_split_add_ledger_step_calls_pass_no_criterion (CY47) and test_1379 every_add_ledger_step_sh_call_site_says_its_exit_2_bails_with_cause_step_add_refused (CY50) lose only their Green call-site assertions, keeping every other site and the BAIL.md half; `../test_skill_event_marks.py`'s skill_prescribes_an_event_sh_step_added_call_beside_every_add_ledger_step_insertion loses only its Green insertion record (CY48); helpers nothing calls any more are removed; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 101 | 27 | 54 | 8727 | 1103415 | 125116 | 0.63 | 322 | 1/2 | unknown | unknown |  |  | full |
| `unit/test_skill_green_split.py` deletes test_1406 runs_replaces_case_survivors_sh_before_the_verify_green_launch_command_not_after_it, test_1558 green_verify_line_that_runs_replaces_case_survivors_sh_before_the_launch_carries_a_replaces_case_qualifier (CY52), skill_md_s_replaces_case_green_paragraph_runs_replaces_case_survivors_before_verify_green and test_1406 replaces_case_green_paragraph_says_each_survivors_relaunch_spends_one_revise_budget_attempt (CY53), test_1431 green_section_judges_a_ci_repair_step_s_green and both test_1473 green_section ci-repair cases (CY61); test_1558 runs_every_replaces_case_survivors_sh_occurrence and test_1406 orders_the_unreplaced_cases_sh_check lose only their Green assertions (CY52), and test_1406 documents_build_develop_prompt_sh_green_s_8th_argument loses only its Green build-command assertion (CY55), keeping its SCRIPTS.md half; `unit/test_skill_refactor_kind.py`'s skill_md_accepts_a_replaces_case_group_step_s_green_only_once is deleted and draft_pr_step_puts_the_conductor_s_mutation_parity_sh_report loses only its `green_near` assertions (CY54); helpers nothing calls any more are removed; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 12 | 24 | 4961 | 515815 | 65722 | 0.27 | 151 | n/a | n/a | n/a |  |  | full |
| `unit/test_skill_stopping.py` deletes green_pass_branch_runs_stop_requested_immediately_after_the_atomic_green_commits_push (CY56, CY60), each_phases_leaf_exit_2_branch drops only its `green` parametrisation (CY36), and the_three_ledger_commit_checkpoints_send_stop_requested_exit_2 loses only its Green PASS branch assertions (CY60); `unit/test_skill_event_files.py`'s every_line_sending_the_run_to_stopping (CY60), every_line_launching_the_reconcile_leaf (CY57) and every_line_sending_the_run_into_the_revise_loop (CY62) lose only their Green sites; `unit/test_skill_push_reconcile.py`'s both_push_branch_call_sites loses only its Green `tick-ledger.sh --refactor-pending` site (CY57); helpers nothing calls any more are removed; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 15 | 28 | 5499 | 613195 | 66872 | 0.28 | 162 | n/a | n/a | n/a |  |  | full |
| `unit/test_skill_draft_pr.py` deletes green_pass_branch_updates_the_pr_body_with_the_ledgers_done_of_total_step_count and green_pass_branch_counts_the_pr_bodys_done_of_total_from_ledger_steps_shs_records (CY58), and green_pass_and_verify_refactor_pass_both_push loses only its Green PASS push assertion (CY57); `unit/test_skill_refactor_pending.py`'s skill_md_ticks_green_with_refactor_pending loses only its Green `--refactor-pending` tick assertion (CY56); `unit/test_skill_bug_fix_subject.py`'s skill_md_gives_a_bug_steps_green_commit_a_fix_subject loses only its Green `fix:` subject assertion (CY59), keeping its Draft PR title half; helpers nothing calls any more are removed; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 62 | 12 | 24 | 3912 | 487261 | 62623 | 0.24 | 178 | n/a | n/a | n/a |  |  | full |
| a case (marked `tree_audit`, in `skills/tdd/scripts/tests/py/test_skill_green_readers.py`, outside `unit/`) finds every remaining test case under `skills/tdd/scripts/tests/py/` that reads SKILL.md's `#### Green — minimum implementation (developer leaf), then verify-green (blind)` subsection by its content — the heading, a marker string only that subsection holds, or any phrase of three or more words found only in that subsection — and requires each to be one of the mechanical or document-wide cases the issue lists on a named allow-list giving why, failing on any other reader; it passes after the deletions above (a pin step: the behaviour already holds once they land); no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 98 | 17 | 32 | 7619 | 713942 | 65752 | 0.31 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 16 | 20 | 18 | 17 | 16 | 17 | 16 | 17 | 18 | 23 |
| affected | 7 | 9 | 9 | 8 | 9 | 7 | 7 | 7 | 7 | 8 |
| target | 14 | 16 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 116 | 228 | 59809 | 4546307 | 813859 | 3.37 |
