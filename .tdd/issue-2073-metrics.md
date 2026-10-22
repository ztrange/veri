### 📊 Metrics — issue 2073

Wall time for the issue: 1570 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2084.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.10 over 48 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 85802 |
| 2 | $0.02 | 86294 |
| 3 | $0.05 | 89961 |
| 4 | $0.03 | 92004 |
| 5 | $0.02 | 92296 |
| 6 | $0.02 | 92707 |
| 7 | $0.02 | 92993 |
| 8 | $0.02 | 93405 |
| 9 | $0.02 | 93726 |
| 10 | $0.02 | 94322 |
| 11 | $0.02 | 94960 |
| 12 | $0.04 | 97452 |
| 13 | $0.02 | 97918 |
| 14 | $0.04 | 100700 |
| 15 | $0.05 | 103844 |
| 16 | $0.05 | 107238 |
| 17 | $0.06 | 112101 |
| 18 | $0.05 | 115123 |
| 19 | $0.03 | 116112 |
| 20 | $0.03 | 116709 |
| 21 | $0.03 | 117923 |
| 22 | $0.03 | 118738 |
| 23 | $0.03 | 119198 |
| 24 | $0.03 | 119827 |
| 25 | $0.03 | 120409 |
| 26 | $0.03 | 121376 |
| 27 | $0.03 | 122174 |
| 28 | $0.04 | 123500 |
| 29 | $0.03 | 124589 |
| 30 | $0.03 | 125517 |
| 31 | $0.03 | 126212 |
| 32 | $0.03 | 127326 |
| 33 | $0.03 | 128189 |
| 34 | $0.03 | 129129 |
| 35 | $0.03 | 129967 |
| 36 | $0.03 | 130381 |
| 37 | $0.04 | 132511 |
| 38 | $0.03 | 132976 |
| 39 | $0.03 | 133857 |
| 40 | $0.04 | 134978 |
| 41 | $0.05 | 137421 |
| 42 | $0.03 | 138082 |
| 43 | $0.03 | 138422 |
| 44 | $0.03 | 139317 |
| 45 | $0.03 | 139608 |
| 46 | $0.03 | 139883 |
| 47 | $0.03 | 140400 |
| 48 | $0.03 | 140900 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 23 | 17 | 2 | 4 | 2257 | 33048 | 34816 | 0.11 |
| prose | 1 | 0 | 0 | 0 | 31 | 29 | 1 | 2 | 4470 | 649 | 72075 | 0.22 |
| diff | 6 | 3 | 0 | 0 | 637 | 107 | 32 | 64 | 11529 | 978371 | 124159 | 0.52 |
| red | 1 | 0 | 0 | 0 | 181 | 70 | 13 | 26 | 9432 | 599393 | 45425 | 0.27 |
| pin | 1 | 1 | 0 | 0 | 49 | 18 | 4 | 6 | 1465 | 80763 | 16643 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 5 | 1 | 0 | 546 | 81 | 21 | 40 | 8091 | 550611 | 106730 | 0.40 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 344 | 131 | 30 | 60 | 16592 | 1140964 | 114313 | 0.57 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skill-edit step for the unit `skills/tdd/SKILL.md`: `skill-edit-step.sh` adds CY1–CY13 and CY63–CY66 to `skills/tdd/REQUIREMENTS.md` under `## skills/tdd/SKILL.md` exactly as the issue's table states them, grades `skills/tdd/SKILL.md` PASS against its whole list with no edit to the prose, and signs it in `GRADED`, so `prose-owed.sh` prints nothing for the unit ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 29 | 1 | 2 | 4470 | 649 | 72075 | 0.22 | 65 | unknown | unknown | unknown |  |  | full |
| `unit/test_skill_revise_exhausted.py` deletes the cost-heading cases the issue lists (runs_only_once_the_leaf_has_exited, fires_at_most_once_per_step, step_cost_sh_exit_3, builds_the_over_budget_prompt, over_budget_split_restores_the_tree, add_ledger_step_sh_exit_1_on_the_over_budget_split, parks_the_step_on_the_over_budget_leaf_s_exit_1, records_the_crossing_and_continues_the_step_on_the_over_budget_leaf_s_exit_3, states_once_why_a_crossing_is_not_a_failure, supervisor_exit_2_on_the_over_budget_leaf); checks_step_cost_sh_after_develop_red_verify_red_each_revise_attempt loses only its develop-red, verdict-red, develop-green and verdict-green checks (its revise-attempt check, which reads REVISE.md, stays); checks_step_cost_sh_after_neither_develop_refactor_nor_verify_refactor loses only its cost-heading sentence check (its after-wait check on the refactor leaves stays); the revise-heading cases stay; helpers nothing calls any more are removed; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 9 | 18 | 3252 | 274190 | 46755 | 0.18 | 180 | n/a | n/a | n/a |  |  | full |
| `test_skill_event_marks.py` deletes writes_one_event_sh_step_over_budget_carrying_spent_and_budget, writes_step_over_budget_on_every_crossing_before_the_branch, over_budget_exit_1_branch_writes_step_escalated and over_budget_exit_3_branch_writes_no_event_mark; over_budget_exit_0_branch_writes_step_split loses only its cost-check (`at=over-budget`) half and keeps its `at=exhausted` half reading REVISE.md; the kept planted-mark case (the_exit_3_case_still_names_a_mark_planted_in_the_exit_3_branch_by_its_line) keeps planting a mark in a copy of SKILL.md and checking it is named by its line, now calling the exit-3 check directly rather than the deleted case; helpers nothing calls any more are removed; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 9 | 18 | 3951 | 267080 | 39196 | 0.16 | 142 | n/a | n/a | n/a |  |  | full |
| `unit/test_skill_green_split.py`'s test_1281 three_split_add_ledger_step_calls_pass_no_criterion case and test_1379 every_add_ledger_step_sh_call_site_says_its_exit_2_bails case each stop checking the cost check's `add-ledger-step.sh instead-of` call (the over-budget split) and keep checking every other call site exactly as before; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 14 | 28 | 4326 | 437101 | 38208 | 0.18 | 513 | n/a | n/a | n/a |  |  | full |
| a case (marked `tree_audit`, in a suite under `skills/tdd/scripts/tests/py/` outside `unit/`) finds every remaining test case under `skills/tdd/scripts/tests/py/` that reads SKILL.md's `#### The step's cost check` subsection by its content — the heading or any string found only in that subsection, such as `develop-over-budget` or `step-over-budget` — not only by its heading, and requires each to be a mechanical-fact case or on a named allow-list giving why (such as `test_skill_leaf_env.py`'s launch-line cases and the planted-mark case), failing on any other reader; it passes after the deletions above (a pin step: the behaviour already holds once they land); no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 88 | 17 | 32 | 10897 | 680156 | 62068 | 0.33 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 14 | 14 | 14 | 14 | 19 | 14 |  |  |  |  |
| affected | 14 | 11 | 10 | 11 | 13 | 158 | 12 | 39 | 16 | 13 |
| target | 13 | 15 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 52 | 102 | 29153 | 1692224 | 293118 | 1.19 |
