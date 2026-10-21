### 📊 Metrics — issue 2028

Wall time for the issue: 3515 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2056.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.36 over 51 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 85468 |
| 2 | $0.07 | 91498 |
| 3 | $0.02 | 92007 |
| 4 | $0.03 | 94005 |
| 5 | $0.02 | 94426 |
| 6 | $0.02 | 95128 |
| 7 | $0.02 | 95434 |
| 8 | $0.02 | 95990 |
| 9 | $0.02 | 96319 |
| 10 | $0.03 | 97268 |
| 11 | $0.06 | 102799 |
| 12 | $0.06 | 107486 |
| 13 | $0.04 | 109370 |
| 14 | $0.03 | 110673 |
| 15 | $0.03 | 111167 |
| 16 | $0.03 | 111842 |
| 17 | $0.03 | 112327 |
| 18 | $0.03 | 112668 |
| 19 | $0.03 | 113461 |
| 20 | $0.03 | 114248 |
| 21 | $0.03 | 114818 |
| 22 | $0.03 | 115432 |
| 23 | $0.03 | 116213 |
| 24 | $0.04 | 118319 |
| 25 | $0.03 | 119001 |
| 26 | $0.03 | 119832 |
| 27 | $0.08 | 126985 |
| 28 | $0.03 | 127795 |
| 29 | $0.03 | 128006 |
| 30 | $0.03 | 128831 |
| 31 | $0.03 | 129533 |
| 32 | $0.03 | 130493 |
| 33 | $0.04 | 131729 |
| 34 | $0.03 | 132613 |
| 35 | $0.04 | 134536 |
| 36 | $0.04 | 135694 |
| 37 | $0.03 | 136156 |
| 38 | $0.03 | 136960 |
| 39 | $0.07 | 142557 |
| 40 | $0.04 | 143517 |
| 41 | $0.04 | 144726 |
| 42 | $0.03 | 145025 |
| 43 | $0.03 | 145274 |
| 44 | $0.03 | 145986 |
| 45 | $0.04 | 146782 |
| 46 | $0.05 | 148875 |
| 47 | $0.04 | 149872 |
| 48 | $0.08 | 155530 |
| 49 | $0.03 | 155941 |
| 50 | $0.03 | 156238 |
| 51 | $0.04 | 156783 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 14 | 1 | 2 | 1474 | 0 | 35167 | 0.10 |
| prose | 2 | 0 | 0 | 0 | 51 | 45 | 2 | 4 | 6438 | 1298 | 141254 | 0.42 |
| diff | 14 | 5 | 2 | 0 | 1260 | 269 | 80 | 158 | 27321 | 2623890 | 392978 | 1.89 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 6 | 2 | 0 | 255 | 109 | 27 | 54 | 10433 | 762543 | 166967 | 0.60 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 809 | 73 | 23 | 44 | 6885 | 703078 | 164952 | 0.92 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 212 | 101 | 31 | 62 | 11477 | 1158269 | 96226 | 0.47 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| diff | 1750 | 1.93 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skill-edit step for the unit `skills/tdd/SKILL.md`: `skill-edit-step.sh` adds PF1–PF26 to `skills/tdd/REQUIREMENTS.md` under `## skills/tdd/SKILL.md` exactly as the issue's table states them, grades `skills/tdd/SKILL.md` PASS against them with no edit to the prose, and signs it in `GRADED`, so `prose-owed.sh` prints nothing for the unit ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 26 | 1 | 2 | 3490 | 649 | 70553 | 0.21 | 60 | unknown | unknown | unknown |  |  | full |
| `test_skill_preflight.py` deletes every Preflight-text case the issue lists (runs_leaf_launchable_before_baseline, refuses_bad_VERI_STEP_GROWTH, calls_step_budget_beside_refactor_budget, checks_GitHub_with_gh_api_user, runs_fast_tier_baseline_inside_worktree, stops_on_red_baseline, takes_conductor_pid_lock, 1485_empty_or_whitespace_read_as_unset, and the 1297 cases resumed_run_rebases_new_branch_not, exit_3_1_2_branching, publishes_with_lease_push_never_bare_force, resets_red_rebased_tip_to_pre_rebase_sha, captures_and_resets_dirty_worktree_and_pre_rebase_sha_first_line, says_never_a_bare_force_negation_on_bare_force), and 1297_marks_resume_rebase_event loses only its Preflight half; full_tier_measured_on_baseline_commit is kept unchanged, as are the four 1420 discard-block cases that run against real git and the cases reading other sections (the resumed-run baseline case and the step 1.2 worktree-guard prose case); helpers nothing calls any more are removed; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 6 | 1 | 2 | 0 | 0 | 0 | 124 | 37 | 72 | 11820 | 1136820 | 229181 | 1.17 | 1075 | 2/2 | unknown | unknown |  |  | full |
| `unit/test_skill_test_command.py` deletes baseline_runs_and_times_tier_fast, and its detects_from_issue_body case loses only its assertions on the Preflight section (its other sections' assertions stay); the 1037 helper cases stay; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 10 | 20 | 2365 | 305193 | 35153 | 0.14 | 105 | n/a | n/a | n/a |  |  | full |
| `unit/test_skill_timeout.py` deletes 954_names_run_state_file, and its times_baseline and times_full_tier cases lose only their assertions on the Preflight section (their other sections' assertions, such as the plan comment's, stay); the step 1.2 recording case and the 1037 helper case stay; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 8 | 16 | 1957 | 237930 | 37199 | 0.14 | 101 | n/a | n/a | n/a |  |  | full |
| `unit/test_leaf_model.py`'s skill_md_preflight_runs_leaf_model case loses its text half (which names it calls and the exit-2 wording) and keeps only the check that every `leaf-model.sh <name>` call in the Preflight section names a leaf `leaf-role.sh` accepts; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 9 | 18 | 2541 | 270959 | 34875 | 0.14 | 109 | n/a | n/a | n/a |  |  | full |
| a case lists every remaining test case under `skills/tdd/scripts/tests/py/` that reads SKILL.md's Preflight section (`### 0. Preflight — baseline checks (bail before any cycle)`) and requires each to be one of a named allow-list of mechanical-fact cases (a script it names exists, a heading a parser reads exists, a code block run against a stub or real git, or the kept full_tier_measured_on_baseline_commit structural check), failing on any other reader; it passes after the deletions above; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 74 | 16 | 32 | 8638 | 672988 | 56570 | 0.30 | 189 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 15 | 14 | 15 | 16 | 15 | 15 | 15 |
| affected | 3 | 674 | 3 | 2 | 1 | 2 | 5 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 83 | 164 | 35233 | 2625188 | 569399 | 2.41 |
