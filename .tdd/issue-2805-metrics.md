### 📊 Metrics — issue 2805

Wall time for the issue: 5513 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2815.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.64 over 27 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87286 tokens, largest 141459 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87286 |
| 2 | $0.07 | 94286 |
| 3 | $0.07 | 100478 |
| 4 | $0.04 | 102554 |
| 5 | $0.03 | 103259 |
| 6 | $0.02 | 103761 |
| 7 | $0.02 | 104101 |
| 8 | $0.02 | 104452 |
| 9 | $0.07 | 110195 |
| 10 | $0.08 | 117776 |
| 11 | $0.05 | 121469 |
| 12 | $0.04 | 123784 |
| 13 | $0.06 | 127882 |
| 14 | $0.04 | 129134 |
| 15 | $0.03 | 130094 |
| 16 | $0.04 | 132307 |
| 17 | $0.05 | 135118 |
| 18 | $0.04 | 136765 |
| 19 | $0.03 | 137491 |
| 20 | $0.03 | 137758 |
| 21 | $0.03 | 138006 |
| 22 | $0.03 | 138617 |
| 23 | $0.03 | 139286 |
| 24 | $0.03 | 140023 |
| 25 | $0.03 | 140486 |
| 26 | $0.03 | 140737 |
| 27 | $0.03 | 141459 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 15 | 3 | 6 | 1853 | 65067 | 34221 | 0.11 |
| prose | 7 | 0 | 0 | 0 | 112 | 68 | 7 | 14 | 11081 | 17865 | 64400 | 0.27 |
| skill-edit | 1 | 0 | 0 | 0 | 36 | 19 | 11 | 14 | 2393 | 192415 | 35603 | 0.13 |
| red | 3 | 0 | 0 | 0 | 85 | 41 | 16 | 28 | 5358 | 407856 | 48360 | 0.22 |
| pin | 3 | 3 | 0 | 0 | 80 | 30 | 11 | 22 | 3537 | 292673 | 42471 | 0.17 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 100 | 45 | 14 | 28 | 5390 | 357740 | 76692 | 0.28 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 85 | 41 | 16 | 28 | 5358 | 407856 | 48360 | 0.22 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skills/vplan/SKILL.md satisfies VPL16, a sub-PRD holds at most one capability the human can use, graded PASS, the pin file skills/tdd/scripts/tests/py/unit/test_prd_015_prose_signed.py updated in the same commit for the longer VPL list ⟦skill-edit⟧ ⟦criterion 1⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 50 | 15 | 22 | 7201 | 206599 | 67636 | 0.26 | 119 | unknown | unknown | unknown |  |  | full |
| skills/vplan/SKILL.md satisfies VPL17, a sub-PRD holding more than one capability is split or states in the sub-PRD why it cannot be, graded PASS ⟦skill-edit⟧ ⟦criterion 2⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 12 | 1 | 2 | 1980 | 1516 | 10495 | 0.05 | 27 | unknown | unknown | unknown |  |  | full |
| skills/vplan/SKILL.md satisfies VPL18, an outline sub-PRD expected to hold more than one capability is split while it is still an outline, graded PASS ⟦skill-edit⟧ ⟦criterion 3⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 14 | 1 | 2 | 2329 | 1516 | 10490 | 0.05 | 28 | unknown | unknown | unknown |  |  | full |
| A case in skills/tdd/scripts/tests/py/unit/test_vplan_sub_prd_cap.py pins that skills/vplan/SKILL.md limits a sub-PRD to one capability the human can use; no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 10 | 20 | 3268 | 287262 | 30680 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| A case in skills/tdd/scripts/tests/py/unit/test_vplan_sub_prd_cap.py pins that skills/vplan/SKILL.md has a sub-PRD holding more than one capability split, or keeping its size only with the reason written in the sub-PRD; no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 9 | 16 | 2907 | 222136 | 30435 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |
| A case in skills/tdd/scripts/tests/py/unit/test_vplan_sub_prd_cap.py pins that skills/vplan/SKILL.md has an outline sub-PRD expected to hold more than one capability split at the outline stage; no production change ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 8 | 14 | 2720 | 191131 | 29716 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 5 | 3 |  |  |  |  |
| target | 6 | 6 | 5 | 5 | 3 | 3 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 48 | 84 | 24222 | 975876 | 225055 | 2.54 (estimate) |
