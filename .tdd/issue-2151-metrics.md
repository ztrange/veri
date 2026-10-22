### 📊 Metrics — issue 2151

Wall time for the issue: 1967 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2163.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.39 over 69 turns, in 2 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 86202 |
| 2 | $0.07 | 91685 |
| 3 | $0.05 | 93649 |
| 4 | $0.03 | 94141 |
| 5 | $0.03 | 94487 |
| 6 | $0.03 | 94840 |
| 7 | $0.03 | 95156 |
| 8 | $0.03 | 95765 |
| 9 | $0.03 | 96473 |
| 10 | $0.05 | 98280 |
| 11 | $0.04 | 99770 |
| 12 | $0.07 | 104710 |
| 13 | $0.04 | 106263 |
| 14 | $0.03 | 106636 |
| 15 | $0.04 | 107198 |
| 16 | $0.03 | 107731 |
| 17 | $0.04 | 108741 |
| 18 | $0.03 | 109170 |
| 19 | $0.05 | 111266 |
| 20 | $0.06 | 114901 |
| 21 | $0.05 | 117755 |
| 22 | $0.04 | 118454 |
| 23 | $0.56 | 86598 |
| 24 | $0.06 | 92303 |
| 25 | $0.03 | 94198 |
| 26 | $0.02 | 94571 |
| 27 | $0.03 | 95928 |
| 28 | $0.05 | 99500 |
| 29 | $0.02 | 99976 |
| 30 | $0.02 | 100501 |
| 31 | $0.02 | 100840 |
| 32 | $0.02 | 101329 |
| 33 | $0.02 | 101750 |
| 34 | $0.03 | 102461 |
| 35 | $0.05 | 105551 |
| 36 | $0.03 | 106109 |
| 37 | $0.03 | 107222 |
| 38 | $0.03 | 107815 |
| 39 | $0.03 | 108291 |
| 40 | $0.03 | 109137 |
| 41 | $0.03 | 109864 |
| 42 | $0.03 | 110322 |
| 43 | $0.03 | 110806 |
| 44 | $0.03 | 111569 |
| 45 | $0.02 | 111817 |
| 46 | $0.03 | 113193 |
| 47 | $0.03 | 114315 |
| 48 | $0.03 | 115197 |
| 49 | $0.03 | 115917 |
| 50 | $0.03 | 116758 |
| 51 | $0.03 | 117523 |
| 52 | $0.03 | 118912 |
| 53 | $0.03 | 119622 |
| 54 | $0.03 | 120444 |
| 55 | $0.03 | 121123 |
| 56 | $0.03 | 121729 |
| 57 | $0.04 | 124199 |
| 58 | $0.03 | 124868 |
| 59 | $0.03 | 125212 |
| 60 | $0.03 | 125924 |
| 61 | $0.03 | 126491 |
| 62 | $0.03 | 126740 |
| 63 | $0.03 | 127020 |
| 64 | $0.03 | 127503 |
| 65 | $0.03 | 128193 |
| 66 | $0.03 | 128570 |
| 67 | $0.03 | 129403 |
| 68 | $0.03 | 129757 |
| 69 | $0.03 | 130109 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 31 | 22 | 1 | 2 | 1117 | 0 | 34929 | 0.10 |
| prose | 3 | 0 | 0 | 0 | 219 | 203 | 3 | 6 | 32051 | 1947 | 268487 | 0.99 |
| diff | 4 | 2 | 0 | 0 | 288 | 114 | 20 | 40 | 5322 | 574658 | 109094 | 0.38 |
| red | 1 | 0 | 0 | 0 | 181 | 60 | 11 | 22 | 5678 | 416405 | 27117 | 0.17 |
| pin | 1 | 1 | 0 | 0 | 80 | 32 | 4 | 6 | 1320 | 85010 | 19442 | 0.07 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 258 | 100 | 14 | 26 | 4701 | 331869 | 105549 | 0.34 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 322 | 128 | 22 | 44 | 8736 | 744204 | 85033 | 0.37 |

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
| skill-edit step for the unit `skills/tdd/SKILL.md`: `skill-edit-step.sh` adds CY100–CY112 to `skills/tdd/REQUIREMENTS.md` under `## skills/tdd/SKILL.md`, after the CY rows of R3d (CY99), exactly as the issue's table states them, grades `skills/tdd/SKILL.md` PASS against its whole list with no edit to the prose, and signs it in `GRADED`, so `prose-owed.sh` prints nothing for the unit ⟦skill-edit⟧ ⟦criterion 1⟧ | 2 | 0 | 0 | 0 | 0 | 0 | 129 | 2 | 4 | 20513 | 1298 | 178798 | 0.65 | 578 | unknown | unknown | unknown |  |  | full |
| `unit/test_skill_refactor_kind.py` deletes plans_an_interface_change_as_one_step_listing_its_phases_and_runs_them_in_order (CY100, CY102; its plan half PL16 is already graded), rejects_an_expand_migrate_or_contract_b_phase_s_commit (CY107), starts_a_phased_step_s_contract_only_once_no_product_caller_sh (CY109, CY110), spends_one_refactor_of_the_budget_for_a_whole_phased_step (CY106), resets_a_phased_step_s_contract_phase_that_exhausts_revise_budget (CY111), accepts_a_phased_step_s_contract_a_phase_only_once (CY108) and marks_an_exhausted_contract_phase_owed (CY112), keeping the two mutation-parity PR-body cases; helpers and constants nothing calls any more are removed; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 11 | 22 | 2744 | 307901 | 74526 | 0.24 | 223 | n/a | n/a | n/a |  |  | full |
| `unit/test_skill_suite_runs.py` test_1300 runs_suite_reported_sh_before_the_verifier_after_develop_diff_revise_diff_k_and_each_phase_leaf loses only its phases step row (CY105), and is deleted with any helper or constant nothing then reads if no row is left; every remaining case still passes; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 71 | 9 | 18 | 2578 | 266757 | 34568 | 0.14 | 200 | n/a | n/a | n/a |  |  | full |
| a case (marked `tree_audit`, in `skills/tdd/scripts/tests/py/test_skill_phased_readers.py`, outside `unit/`) finds every remaining test case under `skills/tdd/scripts/tests/py/` that reads SKILL.md's `#### A ⟦phases: …⟧ step — each listed phase, a developer leaf then a blind verifier` subsection by its content — the heading, a marker string only that subsection holds, or any phrase of three or more words found only in that subsection — and requires each to be one of the mechanical or document-wide cases the issue lists under *Kept, mechanical* on a named allow-list giving why, failing on any other reader; it passes after the deletions above (a pin step: the behaviour already holds once they land); no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 92 | 15 | 28 | 6998 | 501415 | 46559 | 0.24 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| fast | 16 | 17 |  |
| affected | 11 | 13 | 21 |
| target | 21 | 20 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 39 | 76 | 45488 | 1078020 | 459069 | 1.71 |
