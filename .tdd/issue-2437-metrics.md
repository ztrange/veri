### 📊 Metrics — issue 2437

Wall time for the issue: 3679 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2608.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.18 over 51 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89439 tokens, largest 139124 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 89439 |
| 2 | $0.02 | 89906 |
| 3 | $0.06 | 95620 |
| 4 | $0.03 | 97214 |
| 5 | $0.02 | 97550 |
| 6 | $0.03 | 98269 |
| 7 | $0.02 | 98886 |
| 8 | $0.02 | 99338 |
| 9 | $0.02 | 99564 |
| 10 | $0.02 | 100162 |
| 11 | $0.02 | 100456 |
| 12 | $0.03 | 101509 |
| 13 | $0.04 | 104242 |
| 14 | $0.06 | 108526 |
| 15 | $0.03 | 109977 |
| 16 | $0.04 | 111948 |
| 17 | $0.04 | 113795 |
| 18 | $0.03 | 114123 |
| 19 | $0.03 | 115077 |
| 20 | $0.03 | 115556 |
| 21 | $0.02 | 115737 |
| 22 | $0.04 | 117640 |
| 23 | $0.03 | 118148 |
| 24 | $0.03 | 118342 |
| 25 | $0.03 | 118845 |
| 26 | $0.03 | 119486 |
| 27 | $0.03 | 119794 |
| 28 | $0.03 | 120100 |
| 29 | $0.03 | 120781 |
| 30 | $0.07 | 126102 |
| 31 | $0.03 | 126708 |
| 32 | $0.03 | 127384 |
| 33 | $0.03 | 128365 |
| 34 | $0.03 | 128971 |
| 35 | $0.03 | 129620 |
| 36 | $0.03 | 130668 |
| 37 | $0.03 | 131258 |
| 38 | $0.03 | 131989 |
| 39 | $0.03 | 132469 |
| 40 | $0.03 | 132657 |
| 41 | $0.03 | 133133 |
| 42 | $0.03 | 133904 |
| 43 | $0.03 | 134516 |
| 44 | $0.04 | 135908 |
| 45 | $0.03 | 136341 |
| 46 | $0.03 | 136838 |
| 47 | $0.03 | 137130 |
| 48 | $0.03 | 137754 |
| 49 | $0.03 | 137948 |
| 50 | $0.03 | 138840 |
| 51 | $0.03 | 139124 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 11 | 2 | 4 | 1416 | 37345 | 38157 | 0.11 |
| prose | 2 | 0 | 0 | 0 | 216 | 210 | 2 | 4 | 33769 | 1298 | 211447 | 0.87 |
| diff | 6 | 3 | 0 | 0 | 348 | 94 | 32 | 62 | 8995 | 980774 | 141152 | 0.54 |
| rebase | 2 | 1 | 0 | 0 | 786 | 52 | 14 | 26 | 4308 | 386616 | 112101 | 0.36 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 873 | 65 | 17 | 30 | 5801 | 367964 | 168994 | 0.52 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 274 | 92 | 31 | 62 | 8918 | 1036771 | 122416 | 0.50 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skill-edit step for the unit `skills/tdd/SKILL.md`: `skill-edit-step.sh` appends the issue's twenty-three pre-approved rows GD1–GD23, exactly as the issue's table gives them, to the unit's one existing table under `### skills/tdd/SKILL.md` in `skills/tdd/REQUIREMENTS.md`, rewriting no other row and making no edit to the prose of `skills/tdd/SKILL.md`, then grades `skills/tdd/SKILL.md` PASS against its whole list and re-signs it in `skills/tdd/GRADED`, so `GRADED`'s line for the unit matches its current text and `prose-owed.sh` prints nothing ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 119 | 1 | 2 | 19321 | 649 | 109586 | 0.47 | 154 | unknown | unknown | unknown |  |  | full |
| Delete the two Guardrails cases of `skills/tdd/scripts/tests/py/unit/test_skill_draft_pr.py` (`test_guardrails_invariant_about_opening_the_pr_says_neither_exactly_once_nor_the_only_full_suite_gate` and `test_guardrails_invariant_about_opening_the_pr_names_the_branchs_own_full_run_again_after_each_suite_repair_step_and_the_extra_run_on_the_rebased_tip_when_sub_step_1_rebased_the_branch`, both GD16) with the helpers that served only them (`GUARDRAILS`, `_opening_the_pr_invariant`, `SUITE_REPAIR_MARK`, `_word`, and the `GUARDRAILS` branch of `_lines` if no other caller uses it), and the `ALLOWED` entry reading "reads the Guardrails, another unit" in `skills/tdd/scripts/tests/py/unit/test_skill_draft_pr_readers.py`; `_lines` keeps its other callers; every remaining case still passes; tests only, no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 21 | 9 | 18 | 3021 | 264899 | 57302 | 0.20 | 180 | n/a | n/a | n/a |  |  | full |
| Delete `skills/tdd/scripts/tests/py/unit/test_skill_stopping.py::test_1174_skill_md_tells_the_conductor_it_signals_only_processes_it_started_by_the_pid_it_recorded_when_it_started_them_never_by_name_or_pattern_pkill_killall_kill_pgrep_and_that_experiments_carry_the_exp_prefix_no_live_run_uses` (GD4, GD5) and any helper only it used, keeping every other case of that suite; every remaining case still passes; tests only, no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 18 | 9 | 18 | 1995 | 283281 | 38779 | 0.15 | 185 | n/a | n/a | n/a |  |  | full |
| Delete the two `test_1397_…` Guardrails cases of `skills/tdd/scripts/tests/py/unit/test_skill_criterion_finished.py` (GD11) with `guardrails_rec`, and — #2337 having already removed the `"## Resume"` call — `section_records` and `first_record` with their lookup table, keeping `records_of` and every other case; delete the whole module `skills/tdd/scripts/tests/py/unit/test_skill_plan_verify.py`, whose one remaining case is the GD13 reorder-ledger-steps case (its SCRIPTS.md half already gone with #2314) and whose `skill_lines` helper serves only it; every remaining case still passes; tests only, no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 107 | 28 | 52 | 8287 | 819210 | 157172 | 0.56 | 190 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| fast | 29 | 30 | 30 | 26 |  |
| affected | 8 | 7 | 3 | 3 | 2 |
| all | 27 | 695 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 50 | 96 | 48488 | 1406033 | 502857 | 4.06 (estimate) |
