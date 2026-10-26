### 📊 Metrics — issue 2314

Wall time for the issue: 2473 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2485.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $5.60 over 90 turns, in 3 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88504 tokens, largest 120272 tokens
Conductor context: first turn 88507 tokens, largest 137859 tokens
Conductor context: first turn 88645 tokens, largest 166457 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 88504 |
| 2 | $0.04 | 89810 |
| 3 | $0.04 | 91177 |
| 4 | $0.20 | 112895 |
| 5 | $0.04 | 113666 |
| 6 | $0.07 | 118209 |
| 7 | $0.04 | 119198 |
| 8 | $0.04 | 120272 |
| 9 | $0.58 | 88507 |
| 10 | $0.04 | 89846 |
| 11 | $0.10 | 98512 |
| 12 | $0.06 | 102520 |
| 13 | $0.05 | 104566 |
| 14 | $0.03 | 105143 |
| 15 | $0.04 | 105674 |
| 16 | $0.04 | 105959 |
| 17 | $0.03 | 106303 |
| 18 | $0.04 | 106589 |
| 19 | $0.03 | 107224 |
| 20 | $0.04 | 107713 |
| 21 | $0.05 | 110288 |
| 22 | $0.05 | 111520 |
| 23 | $0.05 | 114103 |
| 24 | $0.04 | 115022 |
| 25 | $0.06 | 117661 |
| 26 | $0.03 | 118052 |
| 27 | $0.05 | 119148 |
| 28 | $0.04 | 119719 |
| 29 | $0.04 | 120189 |
| 30 | $0.04 | 120992 |
| 31 | $0.04 | 121369 |
| 32 | $0.04 | 122117 |
| 33 | $0.06 | 125591 |
| 34 | $0.05 | 126799 |
| 35 | $0.04 | 127875 |
| 36 | $0.07 | 132429 |
| 37 | $0.05 | 133488 |
| 38 | $0.06 | 136619 |
| 39 | $0.05 | 137859 |
| 40 | $0.57 | 88645 |
| 41 | $0.02 | 89106 |
| 42 | $0.03 | 90204 |
| 43 | $0.03 | 91349 |
| 44 | $0.19 | 113204 |
| 45 | $0.03 | 113862 |
| 46 | $0.04 | 115612 |
| 47 | $0.03 | 116311 |
| 48 | $0.03 | 116669 |
| 49 | $0.03 | 117533 |
| 50 | $0.03 | 118096 |
| 51 | $0.03 | 118748 |
| 52 | $0.03 | 119844 |
| 53 | $0.03 | 120921 |
| 54 | $0.03 | 121935 |
| 55 | $0.03 | 122591 |
| 56 | $0.03 | 122965 |
| 57 | $0.03 | 123217 |
| 58 | $0.03 | 123972 |
| 59 | $0.05 | 126864 |
| 60 | $0.03 | 127409 |
| 61 | $0.03 | 128015 |
| 62 | $0.03 | 128809 |
| 63 | $0.03 | 129429 |
| 64 | $0.03 | 130083 |
| 65 | $0.03 | 130641 |
| 66 | $0.03 | 131053 |
| 67 | $0.03 | 132073 |
| 68 | $0.04 | 133226 |
| 69 | $0.10 | 142760 |
| 70 | $0.04 | 143638 |
| 71 | $0.04 | 144969 |
| 72 | $0.05 | 147150 |
| 73 | $0.05 | 149411 |
| 74 | $0.03 | 150018 |
| 75 | $0.04 | 151382 |
| 76 | $0.06 | 154543 |
| 77 | $0.04 | 155271 |
| 78 | $0.05 | 157448 |
| 79 | $0.04 | 157974 |
| 80 | $0.04 | 159248 |
| 81 | $0.04 | 159741 |
| 82 | $0.04 | 161235 |
| 83 | $0.04 | 161754 |
| 84 | $0.04 | 162349 |
| 85 | $0.04 | 162907 |
| 86 | $0.04 | 163242 |
| 87 | $0.04 | 163996 |
| 88 | $0.04 | 165301 |
| 89 | $0.04 | 165675 |
| 90 | $0.04 | 166457 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 10 | 1 | 2 | 1286 | 0 | 53156 | 0.15 |
| prose | 4 | 0 | 0 | 0 | 96 | 86 | 4 | 8 | 12482 | 29624 | 104927 | 0.39 |
| diff | 12 | 6 | 0 | 0 | 673 | 282 | 65 | 128 | 24311 | 3018999 | 485620 | 1.76 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 297 | 118 | 25 | 50 | 9800 | 1018266 | 271662 | 0.88 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 389 | 174 | 41 | 80 | 15797 | 2000733 | 267114 | 1.03 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Add the issue's SC1–SC48 rows verbatim under `## skills/tdd/SCRIPTS.md` in skills/tdd/REQUIREMENTS.md, grade `skills/tdd/SCRIPTS.md` PASS against its whole list with no edit to the prose, and sign it in skills/tdd/GRADED, so prose-owed.sh prints nothing ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 37 | 1 | 2 | 5291 | 649 | 39849 | 0.15 | 70 | unknown | unknown | unknown |  |  | full |
| Delete the SCRIPTS.md prose cases of test_issue_worktree.py (the two `test_scripts_md_entry_says_…` cases, SC35) with their only-used helper `scripts_entry`, and only the closing SCRIPTS.md-reading block of test_over_budget.py's `test_cli_prints_one_clock_line_…` case (SC31), keeping its exit-code and one-line assertions; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 8 | 16 | 2695 | 325289 | 90276 | 0.29 | 131 | n/a | n/a | n/a |  |  | full |
| Delete add-ledger-step's catalogue prose cases: unit/test_add_ledger_step.py's `test_scripts_md_entry_documents_planted_and_its_exit_2_refusals_1579` (SC23), and in unit/test_skill_green_split.py the `test_1292_…` case (SC23), the `"--criterion" in add_ledger_step_entry()` assertion of `test_1281_…` (SC23) and the `catalogue_lines()` assertion of `test_1406_…` (SC7), with `catalogue_lines`, `add_ledger_step_entry` and `_bullet_body` if no remaining case calls them; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 9 | 18 | 3204 | 404768 | 76385 | 0.26 | 120 | n/a | n/a | n/a |  |  | full |
| Delete the model-knob, timeout and selection catalogue prose assertions: the SCRIPTS.md iteration of unit/test_skill_bash_timeouts.py's `test_1939_…` (SC5); in unit/test_model_knobs_recorded.py the SCRIPTS.md halves of the three supervise.sh bullet cases (SC2) and the whole `test_1037_bullet_…` case with the helpers `bullet`, `need_supervise_bullet` and `probe_skill_bullet_lists_the_tunables`; the SCRIPTS.md solvable-issues.sh bullet probe of unit/test_selection_order_recorded.py (SC37), and its `bullet` helper if uncalled; CLAUDE.md and CONTEXT.md halves stay; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 9 | 18 | 4343 | 401938 | 79408 | 0.28 | 139 | n/a | n/a | n/a |  |  | full |
| Delete the leaf-launch, stopping and plan-verify catalogue prose cases: unit/test_skill_leaf_launch.py's wait-leaf.sh entry case (SC4) with `wait_leaf_problems` and its `CHECKS` slot (`inventory_entry` too if uncalled; `fragment_problems` stays), unit/test_skill_stopping.py's stop-requested entry case (SC27), and unit/test_skill_plan_verify.py's verifier-scripts plan-phase case (SC8, SC9, SC12), the SCRIPTS.md lines and `unchecked`/`plan:`/`operator` words of its reorder-ledger-steps case (SC19) and `SCRIPTS_MD`; SKILL.md assertions stay; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 9 | 18 | 3782 | 405475 | 78120 | 0.27 | 122 | n/a | n/a | n/a |  |  | full |
| Delete unit/test_skill_refactor_pending.py's five catalogue prose cases (SC18, SC20, SC22, and the two probe-on-planted-text cases that carry no row) with `scripts_records`, `planted_records`, `entry_of`, `entry_says`, `says_removal_verb`, `says_exit_codes`, `removal_verb_probe`, `reference_list_probes`, `SCRIPTS_HEADING`, `REMOVAL_VERB`, `PLANTED_CLEAR_ONLY_BY_FILENAME` and `PLANTED_BARE_ENTRIES`, keeping any name another case still calls; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 13 | 24 | 3141 | 561635 | 74069 | 0.27 | 133 | n/a | n/a | n/a |  |  | full |
| After the deletions, only the mechanical and document-wide readers the issue names still read skills/tdd/SCRIPTS.md under skills/tdd/scripts/tests/py, no deleted helper is left behind uncalled, and the suites that read the unit stay green ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 85 | 17 | 34 | 7146 | 919894 | 87362 | 0.38 | 235 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 20 | 20 | 20 | 18 | 18 | 17 |  |  |
| affected | 4 | 1 | 2 | 1 | 2 | 1 | 0 | 26 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 70 | 138 | 38079 | 3048623 | 643703 | 2.30 |
