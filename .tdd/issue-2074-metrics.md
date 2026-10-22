### 📊 Metrics — issue 2074

Wall time for the issue: 1042 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run bailed — untestable-criterion, a process failure.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.77 over 41 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 85828 |
| 2 | $0.03 | 87648 |
| 3 | $0.03 | 89524 |
| 4 | $0.02 | 89911 |
| 5 | $0.02 | 90208 |
| 6 | $0.02 | 90481 |
| 7 | $0.02 | 90750 |
| 8 | $0.02 | 91286 |
| 9 | $0.02 | 91768 |
| 10 | $0.02 | 92276 |
| 11 | $0.02 | 92757 |
| 12 | $0.02 | 93306 |
| 13 | $0.06 | 98389 |
| 14 | $0.03 | 100140 |
| 15 | $0.03 | 101122 |
| 16 | $0.03 | 102758 |
| 17 | $0.03 | 103919 |
| 18 | $0.02 | 104290 |
| 19 | $0.03 | 105042 |
| 20 | $0.02 | 105532 |
| 21 | $0.03 | 106186 |
| 22 | $0.03 | 107209 |
| 23 | $0.02 | 107563 |
| 24 | $0.03 | 108385 |
| 25 | $0.03 | 109121 |
| 26 | $0.06 | 114108 |
| 27 | $0.03 | 114740 |
| 28 | $0.03 | 115465 |
| 29 | $0.04 | 117942 |
| 30 | $0.03 | 118630 |
| 31 | $0.03 | 119466 |
| 32 | $0.03 | 120215 |
| 33 | $0.03 | 120607 |
| 34 | $0.03 | 121079 |
| 35 | $0.03 | 121662 |
| 36 | $0.04 | 123247 |
| 37 | $0.03 | 123584 |
| 38 | $0.04 | 124917 |
| 39 | $0.03 | 125574 |
| 40 | $0.03 | 126184 |
| 41 | $0.05 | 129806 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 909 | 0 | 31158 | 0.09 |
| prose | 1 | 0 | 0 | 0 | 25 | 20 | 1 | 2 | 3245 | 649 | 71294 | 0.21 |
| diff | 4 | 2 | 0 | 0 | 233 | 61 | 21 | 42 | 6293 | 584016 | 78151 | 0.32 |
| red | 1 | 0 | 0 | 0 | 69 | 12 | 4 | 8 | 1183 | 98395 | 36221 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 108 | 25 | 7 | 14 | 2730 | 150922 | 58563 | 0.19 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 204 | 55 | 19 | 38 | 5655 | 531489 | 86967 | 0.33 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 69 | 0.11 |
| develop-red | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skill-edit step for the unit `skills/tdd/SKILL.md`: `skill-edit-step.sh` adds PF27–PF30 to `skills/tdd/REQUIREMENTS.md` under `## skills/tdd/SKILL.md` exactly as the issue's table states them, grades `skills/tdd/SKILL.md` PASS against its whole list with no edit to the prose, and signs it in `GRADED` with a signature matching the unit's current text, so `prose-owed.sh` prints nothing for the unit ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 20 | 1 | 2 | 3245 | 649 | 71294 | 0.21 | 51 | unknown | unknown | unknown |  |  | full |
| `unit/test_skill_refactor_pending.py` deletes both 1611 cases (resume_preflight_describes_the_tree_before_rebase_onto_default_sh…, now PF28, and resume_preflight_paragraph_under_the_discard_block…, now PF29) and `unit/test_skill_commit.py`'s 1785 case skill_md_points_the_pinned_snapshot_and_the_leaf_launchable_exit_2_at_readme loses only its preflight step 2 exit-2 README-pointer and no-"above describes" assertions (now PF30; its SCRIPTS.md pinned-$S assertions stay); the three matching "no PF row covers it yet" entries leave `test_skill_preflight.py`'s MECHANICAL_READERS, helpers nothing calls any more are removed, and the Preflight readers guard stays green; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 11 | 22 | 3562 | 306627 | 50052 | 0.19 | 183 | n/a | n/a | n/a |  |  | full |
| `unit/test_skill_stopping.py`'s 987 case preflight_step_3_runs_stop_requested_clear_beside_the_tdd_conductor_pid_write… loses only its stale-request assertion (now PF27; its .tdd/conductor.pid and stop-requested.sh --clear assertions stay, and the case is renamed to drop the stale-request clause), its MECHANICAL_READERS entry loses the "no PF row covers it yet" remark (kept as a mechanical-fact entry only while the case still reads the Preflight section, removed otherwise), and the Preflight readers guard stays green with no reader of the Preflight section other than mechanical-fact cases; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 10 | 20 | 2731 | 277389 | 28099 | 0.13 | 173 | n/a | n/a | n/a |  |  | full |
| fix the full-suite failure: test_fast_tier_guard.py — FAILED test_1641_a_real_exemption_keyed_relative_to_tests_py_is_not_reported_stale_by_any_case_that_reads_the_real_table - Failed: Timeout (>30.0s); test_mutation_parity_process.py — FAILED test_a_row_whose_old_case_is_a_pytest_node_id_is_valid_when_the_node_goes_red_and_another_case_of_its_file_stays_green_and_owed_when_none_stays_green; test_recipe_one_pytest_process.py — FAILED test_make_test_and_make_unit_each_run_one_pytest_and_no_bash_suite_unit_the_small_cases_and_test_the_small_and_medium_cases; test_skill_preflight.py — FAILED test_every_remaining_case_that_reads_skill_md_s_preflight_section_is_a_named_mechanical_fact_case - Failed: Timeout (>30.0s) (machine load average 68–124 during the run) ⟦suite-repair⟧ ⟦criterion 2⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 12 | 4 | 8 | 1183 | 98395 | 36221 | 0.11 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| fast | 23 | 18 | 19 |
| affected | 23 | 19 | 20 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 27 | 54 | 11630 | 683060 | 216824 | 0.73 |
