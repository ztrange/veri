### 📊 Metrics — issue 1467

Wall time for the issue: 3852 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1552.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 9 | 1 | 2 | 906 | 12193 | 42473 | 0.18 |
| red | 7 | 3 | 0 | 0 | 210 | 140 | 41 | 78 | 14231 | 1944339 | 336952 | 1.68 |
| green | 6 | 3 | 0 | 0 | 1489 | 129 | 45 | 88 | 12628 | 2244112 | 282329 | 1.48 |
| refactor | 6 | 3 | 0 | 0 | 319 | 73 | 21 | 42 | 5222 | 897602 | 267124 | 1.21 |
| pin | 1 | 1 | 0 | 0 | 21 | 16 | 4 | 8 | 1549 | 171866 | 44807 | 0.21 |
| predicate | 1 | 0 | 0 | 0 | 16 | 12 | 3 | 6 | 651 | 120923 | 42640 | 0.19 |
| structural | 1 | 0 | 0 | 0 | 18 | 12 | 3 | 6 | 645 | 120604 | 45139 | 0.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 11 | 0 | 0 | 1059 | 184 | 51 | 100 | 16504 | 2287673 | 494034 | 2.37 |
| developer | claude-sonnet-5-5 | 12 | 0 | 0 | 0 | 1027 | 207 | 67 | 130 | 19328 | 3223966 | 567430 | 2.79 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| SKILL.md's planning section requires each step's text to carry every constraint the issue attaches to the cases that step covers — the case size it must keep (medium / real process), "no production change", and any end-to-end path through real processes that must stay covered — pinned by a prose case on SKILL.md that goes red when that sentence is removed or reversed ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 106 | 35 | 68 | 9997 | 1663438 | 282663 | 1.40 | 1072 | unknown | 0/5 | structural-owed |  |  | full |
| SKILL.md's planning section requires a step that can be satisfied only by editing a test to be planned as a test-only (⟦diff-checked⟧ or pin) step, never as red/green — pinned by a prose case on SKILL.md that goes red when that sentence is removed or reversed ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 10 | 20 | 4117 | 476377 | 93414 | 0.46 | unknown | unknown | unknown | unknown |  |  | pin |
| A plan prompt built by `build-verify-prompt.sh plan` tells the plan verifier to REJECT a plan whose step drops a constraint the issue attaches to the cases that step covers (case size / real process, "no production change", an end-to-end path through real processes), the instruction living in skills/tdd/scripts/prompts/verify-plan.md — pinned by a case on `build-verify-prompt.sh plan` ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 107 | 34 | 66 | 9384 | 1612493 | 277940 | 1.37 | 619 | unknown | 0/5 | nothing-structural |  |  | full |
| A plan prompt built by `build-verify-prompt.sh plan` tells the plan verifier to REJECT a plan that plans a test-only change (one satisfiable only by editing a test) as a red/green step, the instruction living in skills/tdd/scripts/prompts/verify-plan.md — pinned by a case on `build-verify-prompt.sh plan` ⟦criterion 2⟧ | 8 | 3 | 0 | 0 | 0 | 0 | 133 | 38 | 74 | 11428 | 1747138 | 364974 | 1.75 | 565 | unknown | 0/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| SKILL.md's planning section requires each step's text to carry every constraint the issue attaches to the cases that step covers — the case size it must keep (medium / real process), "no production change", and any end-to-end path through real processes that must stay covered — pinned by a prose case on SKILL.md that goes red when that sentence is removed or reversed ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 93 | 0.40 |
| A plan prompt built by `build-verify-prompt.sh plan` tells the plan verifier to REJECT a plan whose step drops a constraint the issue attaches to the cases that step covers (case size / real process, "no production change", an end-to-end path through real processes), the instruction living in skills/tdd/scripts/prompts/verify-plan.md — pinned by a case on `build-verify-prompt.sh plan` ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 118 | 0.41 |
| A plan prompt built by `build-verify-prompt.sh plan` tells the plan verifier to REJECT a plan that plans a test-only change (one satisfiable only by editing a test) as a red/green step, the instruction living in skills/tdd/scripts/prompts/verify-plan.md — pinned by a case on `build-verify-prompt.sh plan` ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 108 | 0.39 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 1 | 7 | 6 | 5 | 0 | 0 | 6 | 5 | 13 | 12 | 11 |
| fast | 65 | 62 | 61 | 71 | 77 | 75 | 69 | 68 | 70 | 69 | 67 |  |  |
| target | 0 | 1 | 0 | 1 | 5 | 6 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 118 | 230 | 35832 | 5511639 | 1061464 | 5.16 |
