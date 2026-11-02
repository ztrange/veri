### 📊 Metrics — issue 2782

Wall time for the issue: 27944 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 20 of 20 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2899.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $8.01 over 91 turns, in 3 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87100 tokens, largest 136241 tokens
Conductor context: first turn 87081 tokens, largest 147165 tokens
Conductor context: first turn 87205 tokens, largest 209183 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 87100 |
| 2 | $0.19 | 107109 |
| 3 | $0.05 | 107815 |
| 4 | $0.05 | 109829 |
| 5 | $0.04 | 110417 |
| 6 | $0.04 | 110762 |
| 7 | $0.04 | 111071 |
| 8 | $0.06 | 113920 |
| 9 | $0.06 | 116678 |
| 10 | $0.12 | 125693 |
| 11 | $0.09 | 132541 |
| 12 | $0.06 | 134866 |
| 13 | $0.05 | 136241 |
| 14 | $0.57 | 87081 |
| 15 | $0.20 | 107558 |
| 16 | $0.04 | 108328 |
| 17 | $0.12 | 118140 |
| 18 | $0.04 | 119153 |
| 19 | $0.05 | 119827 |
| 20 | $0.04 | 120198 |
| 21 | $0.04 | 120501 |
| 22 | $0.05 | 121148 |
| 23 | $0.04 | 121683 |
| 24 | $0.11 | 129985 |
| 25 | $0.12 | 140713 |
| 26 | $0.06 | 142640 |
| 27 | $0.07 | 144923 |
| 28 | $0.06 | 147165 |
| 29 | $0.56 | 87205 |
| 30 | $0.18 | 107452 |
| 31 | $0.04 | 109523 |
| 32 | $0.04 | 111401 |
| 33 | $0.05 | 115086 |
| 34 | $0.03 | 116010 |
| 35 | $0.03 | 116930 |
| 36 | $0.03 | 117281 |
| 37 | $0.03 | 117609 |
| 38 | $0.03 | 118849 |
| 39 | $0.05 | 121567 |
| 40 | $0.09 | 130027 |
| 41 | $0.05 | 133266 |
| 42 | $0.06 | 137005 |
| 43 | $0.15 | 151750 |
| 44 | $0.04 | 152828 |
| 45 | $0.04 | 154262 |
| 46 | $0.05 | 157039 |
| 47 | $0.04 | 158551 |
| 48 | $0.04 | 159421 |
| 49 | $0.06 | 162354 |
| 50 | $0.04 | 163625 |
| 51 | $0.04 | 164535 |
| 52 | $0.06 | 168365 |
| 53 | $0.04 | 169467 |
| 54 | $0.05 | 171654 |
| 55 | $0.05 | 173000 |
| 56 | $0.12 | 183165 |
| 57 | $0.06 | 185640 |
| 58 | $0.05 | 187103 |
| 59 | $0.05 | 188235 |
| 60 | $0.06 | 190537 |
| 61 | $0.05 | 191406 |
| 62 | $0.04 | 191708 |
| 63 | $0.04 | 192005 |
| 64 | $0.04 | 192268 |
| 65 | $0.04 | 192897 |
| 66 | $0.05 | 193876 |
| 67 | $0.05 | 195683 |
| 68 | $0.06 | 197948 |
| 69 | $0.05 | 199456 |
| 70 | $0.05 | 200190 |
| 71 | $0.04 | 200758 |
| 72 | $0.04 | 201007 |
| 73 | $0.04 | 201250 |
| 74 | $0.04 | 201680 |
| 75 | $0.05 | 202887 |
| 76 | $0.05 | 204184 |
| 77 | $0.04 | 204474 |
| 78 | $0.04 | 204710 |
| 79 | $0.04 | 205087 |
| 80 | $0.04 | 205521 |
| 81 | $0.05 | 206420 |
| 82 | $1.52 | 207168 |
| 83 | $0.04 | 207497 |
| 84 | $0.04 | 207864 |
| 85 | $0.05 | 208722 |
| 86 | $0.05 | 209183 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 14 | 1 | 2 | 1604 | 0 | 47344 | 0.13 |
| prose | 12 | 0 | 0 | 0 | 373 | 327 | 12 | 24 | 51117 | 16458 | 340142 | 1.36 |
| red | 7 | 1 | 0 | 0 | 473 | 210 | 37 | 72 | 29114 | 1398794 | 302430 | 1.40 |
| pin | 4 | 3 | 1 | 0 | 189 | 49 | 14 | 26 | 5744 | 424623 | 124766 | 0.41 |
| diff | 18 | 9 | 0 | 0 | 1769 | 323 | 109 | 212 | 36328 | 4265505 | 546175 | 2.16 |
| green | 2 | 1 | 0 | 0 | 2711 | 25 | 11 | 20 | 2756 | 332060 | 94003 | 0.30 |
| refactor | 1 | 0 | 0 | 0 | 8 | 4 | 2 | 4 | 192 | 41361 | 42299 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 16 | 15 | 1 | 0 | 3735 | 204 | 58 | 112 | 21124 | 1835774 | 545252 | 1.76 |
| developer | claude-sonnet-5-5 | 14 | 0 | 0 | 0 | 1221 | 313 | 100 | 192 | 41520 | 3963799 | 483436 | 2.02 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 212 | 108 | 16 | 32 | 13094 | 662770 | 128329 | 0.73 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 101 | 0.19 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skill-edit step for the unit `skills/tdd/SKILL.md`: `skill-edit-step.sh` adds the issue's rows SS1, SS2, SS3, PL63 and CY129, exactly as the issue's table gives them, to `skills/tdd/REQUIREMENTS.md` under `## skills/tdd/SKILL.md`, rewriting no existing row; the unit grades PASS against its whole list with no edit to its prose, and is signed in `skills/tdd/GRADED`, so `prose-owed.sh` prints nothing for it ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 76 | 1 | 2 | 12629 | 649 | 111309 | 0.40 | 102 | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/tdd/PREFLIGHT.md`: `skill-edit-step.sh` adds the issue's rows PF36, PF37 and PF38, exactly as the issue's table gives them, to `skills/tdd/REQUIREMENTS.md` under `## skills/tdd/PREFLIGHT.md`, rewriting no existing row; the unit grades PASS against its whole list with no edit to its prose, and is signed in `skills/tdd/GRADED`, so `prose-owed.sh` prints nothing for it ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 20 | 1 | 2 | 3261 | 1516 | 17584 | 0.08 | 30 | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/tdd/REFACTOR-KIND.md`: `skill-edit-step.sh` adds the issue's row PL64, exactly as the issue's table gives it, to `skills/tdd/REQUIREMENTS.md` under `## skills/tdd/REFACTOR-KIND.md`, rewriting no existing row; the unit grades PASS against its whole list with no edit to its prose, and is signed in `skills/tdd/GRADED`, so `prose-owed.sh` prints nothing for it ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 10 | 1 | 2 | 1795 | 1516 | 9638 | 0.04 | 21 | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/tdd/scripts/prompts/develop-revise.md`: `skill-edit-step.sh` adds the issue's row DV5, exactly as the issue's table gives it, to `skills/tdd/scripts/prompts/REQUIREMENTS.md` under `## skills/tdd/scripts/prompts/develop-revise.md`, rewriting no existing row; the unit grades PASS against its whole list with no edit to its prose, and is signed in `skills/tdd/GRADED`, so `prose-owed.sh` prints nothing for it ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 9 | 1 | 2 | 1309 | 1516 | 9465 | 0.04 | 20 | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/vdev/SKILL.md`: `skill-edit-step.sh` adds the issue's row D22, exactly as the issue's table gives it, to `skills/vdev/REQUIREMENTS.md` under `## skills/vdev/SKILL.md`, rewriting no existing row; the unit grades PASS against its whole list with no edit to its prose, and is signed in `skills/vdev/GRADED`, so `prose-owed.sh` prints nothing for it ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 15 | 1 | 2 | 2221 | 1516 | 11473 | 0.05 | 27 | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/vcoord/SKILL.md`: `skill-edit-step.sh` adds the issue's row C19, exactly as the issue's table gives it, to `skills/vcoord/REQUIREMENTS.md` under `## skills/vcoord/SKILL.md`, rewriting no existing row; the unit grades PASS against its whole list with no edit to its prose, and is signed in `skills/vcoord/GRADED`, so `prose-owed.sh` prints nothing for it ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 12 | 1 | 2 | 1726 | 1516 | 10728 | 0.04 | 23 | unknown | unknown | unknown |  |  | full |
| Once all six units are signed, a case in `skills/tdd/scripts/tests/py/test_prose_owed_process.py` (process-marked and tree_audit-marked, like `test_2684_the_four_interface_phase_verify_units_are_listed_signed_and_owe_no_grade` beside it) asserts that each of the twelve row IDs (SS1, SS2, SS3, PL63, CY129, PF36, PF37, PF38, PL64, DV5, D22, C19) is a row under its unit's heading in that unit's `REQUIREMENTS.md`, and that `prose-owed.sh` run on the repository prints nothing, exiting 0; no production change (pin: already holds) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 9 | 18 | 4285 | 314772 | 93833 | 0.31 | unknown | unknown | unknown | unknown |  |  | pin |
| Test-only, no production change and no prose edit: in `skills/tdd/scripts/tests/py/unit/test_skill_event_files.py` the four cases `test_skill_md_no_longer_carries_the_stopping_or_reconciling_sections_1716`, `test_the_revise_section_lives_in_revise_md_not_skill_md_1855`, `test_the_moved_sections_distinctive_lines_are_absent_from_skill_md_and_present_in_their_files_2218` and `test_the_pin_section_lives_in_pin_md_not_skill_md_1852` are deleted whole, with any helper or local only they used and the `test_the_moved_sections…` entry in `test_skill_phased_readers.py`'s `ALLOWED`; every KEEP case in that file is unchanged and the affected suites stay green ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 9 | 16 | 2385 | 288148 | 55515 | 0.19 | 238 | n/a | n/a | n/a |  |  | full |
| Test-only, no production change and no prose edit: in `skills/tdd/scripts/tests/py/unit/test_skill_commit.py` the five cases `test_skill_md_documents_the_skill_snapshot_veri_new_skill_and_issue_n_skill_commit_and_claude_md_cross_references_them`, `test_skill_md_s_s_paragraph_no_longer_says_nothing_pins_it_and_says_the_skill_snapshot_pins_the_commit_a_run_executes_under`, `test_1785_launching_the_conductor_lives_in_readme_after_install_and_not_in_skill_md`, `test_1785_skill_md_points_the_pinned_snapshot_at_readme` and `test_skill_md_says_what_a_change_to_the_skill_means_for_a_running_conductor_and_that_the_event_log_records_each_leaf_s_commit` are deleted whole, with any helper or local only they used; the affected suites stay green ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 12 | 24 | 2523 | 463003 | 52600 | 0.20 | 257 | n/a | n/a | n/a |  |  | full |
| Test-only, no production change and no prose edit: these eight SKILL.md cases are deleted whole, with any helper or local only they used, and a module left with no case removed: `unit/test_skill_stopping.py::test_each_phases_leaf_exit_2_branch_points_back_to_launching_a_leaf_where_stop_requested_is_asked_before_the_exit_2_is_read_as_killed_stuck` and `::test_skill_md_carries_none_of_the_bailing_sections_lines`, `unit/test_skill_draft_pr.py::test_worktree_step_no_longer_says_the_draft_pr_is_opened_once_every_step_is_green`, `unit/test_skill_resume_pointers.py::test_resume_section_lives_in_resume_md_and_skill_md_carries_none_of_its_lines`, `unit/test_skill_suite_runs.py::test_skill_md_names_no_full_suite_run_inside_a_step_s_cycle`, `unit/test_skill_modes_reference_2433.py::test_2433_skill_never_promises_modes_below_and_print_mode_aside_cites_readme`, `unit/test_skill_push_reconcile.py::test_both_push_branch_call_sites_branch_exit_1_to_a_supervised_develop_reconcile_leaf_and_exit_2_to_a_bail_the_reconcile_re_pushes_and_checks_the_ledger_or_bails_reconcile_failed_and_exits_0_either_way_is_gone` and `unit/test_skill_refactor_leaf.py::test_skill_md_grows_the_plan_from_the_refactor_leaf_s_flags_classes_alone_reading_no_new_step_or_candidates_line_of_the_leaf_s_into_it`; with them go the allow-list entries the issue names for them in `test_skill_phased_readers.py`, `unit/test_skill_plan_readers.py`, `test_skill_refactor_readers.py` and `unit/test_skill_draft_pr_readers.py`; the affected suites stay green ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 18 | 36 | 7439 | 837482 | 75639 | 0.35 | 318 | n/a | n/a | n/a |  |  | full |
| Test-only, no production change and no prose edit: these four cases are deleted whole, with any helper or local only they used, and a module left with no case removed: `test_skill_preflight.py::test_skill_md_s_worktree_guard_prose_says_the_lock_is_taken_in_preflight_step_3_before_the_baseline_and_never_in_step_1_2`, `unit/test_skill_never_asks_2433.py::test_2433_never_asks_rule_is_discharged_by_a_needs_user_bail_beside_both_asks`, `unit/test_skill_detach_test_command.py::test_skill_md_says_what_detach_command_sh_wait_answers_0_passed_1_red_2_died_3_still_running` and `unit/test_skill_refactor_kind.py::test_skill_md_says_a_diff_checked_step_in_a_refactor_kind_run_runs_develop_diff_then_verify_diff_and_never_cover_or_transform_1915`; with them go the three `MECHANICAL_READERS` entries in `test_skill_preflight.py` and the entries in `unit/test_skill_plan_readers.py`'s `ALLOWED` the issue names for them; the affected suites stay green ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 10 | 20 | 4828 | 388870 | 65259 | 0.25 | 260 | n/a | n/a | n/a |  |  | full |
| Test-only, no production change and no prose edit: the four lane cases `unit/test_veri_coord_lane.py::test_1778_veri_coord_states_its_lane_in_its_first_line_and_names_it_in_every_dev_message`, `::test_1778_veri_coord_takes_an_optional_lane_word_in_its_invocation_line_and_c1_row`, `unit/test_veri_dev_lane.py::test_1778_veri_dev_states_its_lane_in_its_first_line_of_output` and `::test_1778_veri_dev_takes_an_optional_lane_word_in_its_invocation_line_and_d1_row` are deleted whole, with any helper or local only they used, and a module left with no case removed; the affected suites stay green ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 10 | 20 | 2522 | 370712 | 55592 | 0.20 | 283 | n/a | n/a | n/a |  |  | full |
| Test-only, no production change and no prose edit: `unit/test_build_develop_prompt.py::test_cli_verify_green_prompt_asks_a_missing_test_reject_for_a_missing_test_line_and_revise_green_asks_it_of_an_impossible_with_no_test_edit_1808` and `unit/test_build_verify_prompt.py::test_a_diff_prompt_tells_the_verifier_the_wrapper_hands_the_test_commands_exit_status_straight_back` are deleted whole, with any helper or local only they used; every KEEP case in those two files is unchanged and the affected suites stay green ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 9 | 18 | 2297 | 326238 | 51569 | 0.18 | 308 | n/a | n/a | n/a |  |  | full |
| Test-only, no production change and no prose edit: these eight SKILL.md cases are reduced to the STAY half the issue's table names for each, the GO assertions removed with any helper or local only they used, their names kept: `test_skill_event_marks.py::test_skill_prescribes_an_event_sh_call_for_each_of_the_conductors_seven_marks_beside_the_issue_comment_it_mirrors`, `unit/test_skill_green_split.py::test_1281_skill_md_s_three_split_add_ledger_step_calls_pass_no_criterion_and_say_a_split_keeps_its_anchor_s_criterion_the_uncovered_spec_call_passes_criterion_k_read_from_the_issue_s_numbered_acceptance_criteria_one_call_per_criterion_bailing_on_exit_2` and `::test_1379_skill_md_s_every_add_ledger_step_sh_call_site_says_its_exit_2_bails_with_cause_step_add_refused`, `unit/test_skill_green_superseded.py::test_2254_a_green_report_naming_a_superseded_case_alone_goes_through_wrong_test_route_to_a_free_red_contradicted_reroute`, `unit/test_skill_reference_usage.py::test_skill_md_points_at_scripts_md_and_carries_no_catalogue_entry_and_scripts_md_keeps_every_moved_entry_1715`, `unit/test_skill_suite_runs.py::test_1568_skill_md_runs_suite_reported_sh_develop_transform_after_the_refactor_kind_transform_leaf_and_before_its_blind_transform_verifier`, `unit/test_skill_tests_frozen.py::test_every_reroute_re_record_in_green_passes_the_steps_own_red_case_and_routes_its_refusal_to_verify_red_reason` and `unit/test_skill_guard_subject_paragraph.py::test_skill_md_guard_subject_paragraph_names_a_pytest_guard_suite_and_conftest_and_says_the_path_is_matched_exactly_1775`; the affected suites stay green ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 64 | 22 | 44 | 7694 | 998113 | 67342 | 0.35 | 358 | n/a | n/a | n/a |  |  | full |
| Test-only, no production change and no prose edit: these five cases are reduced to the STAY half the issue's table names for each, the GO assertions removed with any helper or local only they used, their names kept: `unit/test_skill_resume_pointers.py::test_1967_preflight_step_3_resumed_run_block_is_one_resume_clean_sh_call_and_its_exit_2_bails_as_a_system_failure`, `test_wait_leaf.py::test_skill_md_tells_the_conductor_to_call_detach_command_sh_wait_with_no_max_seconds_and_the_bash_maximum_timeout_never_a_fixed_500_1708`, `test_solvable_issues.py::test_skill_preflight_never_writes_the_conductor_lock_itself_leaving_it_to_run_conductor_2249`, `unit/test_skill_revise_same_reject.py::test_revise_md_names_same_reject_and_both_branches` and `unit/test_build_develop_prompt.py::test_main_renders_a_revise_red_prompt_for_a_replaces_case_step_without_an_instruction_to_add_a_single_case_and_one_without_the_mark_unchanged_1537`; the affected suites stay green ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 10 | 16 | 3882 | 286739 | 54810 | 0.20 | 333 | n/a | n/a | n/a |  |  | full |
| A tree_audit-marked case in a new module `skills/tdd/scripts/tests/py/test_wording_case_dispositions_2782.py` asserts, reading the test modules under `skills/tdd/scripts/tests/py/` by `ast` and excluding itself, that none of the issue's 27 DELETE case names is defined any more and that every one of its 23 KEEP and 13 REDUCE case names is still defined; no production change (pin: already holds) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 68 | 11 | 18 | 11597 | 353860 | 63599 | 0.31 | unknown | unknown | unknown | unknown |  |  | pin |
| A case in `skills/tdd/scripts/tests/py/unit/test_skill_plan_readers.py` or a new tree_audit-marked module asserts that every entry of the allow-lists of `test_skill_phased_readers.py`, `test_skill_refactor_readers.py`, `unit/test_skill_plan_readers.py`, `unit/test_skill_draft_pr_readers.py` and `test_skill_preflight.py`'s `MECHANICAL_READERS` names a case that exists; no production change (pin: already holds) ⟦criterion 3⟧ | 5 | 1 | 1 | 0 | 0 | 0 | 134 | 23 | 46 | 16242 | 903373 | 181309 | 0.92 | unknown | 1/2 | unknown | unknown |  |  | pin |
| Test-only, no production change and no prose edit: the four allow-list entries naming no existing case are removed: from `test_skill_phased_readers.py` `ALLOWED`, `unit/test_skill_refactor_kind.py::test_skill_md_puts_mutation_parity_sh_s_report_into_the_pr_body_as_the_pairs_table_and_each_row_it_reports_owed_under_owed_by_a_human` and `unit/test_skill_refactor_kind.py::test_skill_md_s_draft_pr_step_puts_the_conductor_s_mutation_parity_sh_report_into_the_pr_body_template_…`; from `test_skill_preflight.py` `MECHANICAL_READERS`, `test_skill_edit_md_runs_skill_edit_step_ticks_on_exit_0_or_3_bails_on_1_and_handles_2_as_no_answer_1871` and `test_skill_preflight_writes_the_long_lived_ppid_not_the_shells_pid`; nothing else changes and the reader audits stay green ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 9 | 18 | 2758 | 306200 | 67849 | 0.23 | 228 | n/a | n/a | n/a |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_fast_tier_guard.py — FAIL - test_every_guard_clean_pytest_file_lives_under_tests_py_unit_and_every_file_the_guard_names_stays_outside_it and test_1641_a_real_exemption_keyed_relative_to_tests_py_is_not_reported_stale_by_any_case_that_reads_the_real_table: test_wording_case_dispositions_2782.py: guard-clean, outside the tier ⟦suite-repair⟧ ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 53 | 21 | 40 | 5682 | 624833 | 224757 | 0.68 | 2923 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_fast_tier_guard.py — FAIL - test_every_guard_clean_pytest_file_lives_under_tests_py_unit_and_every_file_the_guard_names_stays_outside_it and test_1641_a_real_exemption_keyed_relative_to_tests_py_is_not_reported_stale_by_any_case_that_reads_the_real_table: test_wording_case_dispositions_2782.py: guard-clean, outside the tier ⟦suite-repair⟧ ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.11 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 17 | 9 | 7 | 18 | 17 | 12 | 15 | 11 | 9 | 19 | 18 | 8 | 11 | 18 | 23 | 7 | 20 | 11 |
| target | 8 | 8 | 19 | 18 | 13 | 7 | 7 | 15 | 21 | 18 |  |  |  |  |  |  |  |  |
| fast | 53 | 56 | 58 | 53 | 44 | 55 | 97 | 61 | 62 | 46 | 53 | 54 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 186 | 360 | 126855 | 6478801 | 1497159 | 13.88 (estimate) |
