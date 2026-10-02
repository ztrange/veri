### 📊 Metrics — issue 660

Wall time for the issue: 2350 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/674.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 14 | 2 | 4 | 995 | 58432 | 36562 | 0.32 |
| red | 8 | 3 | 0 | 0 | 305 | 241 | 63 | 116 | 23676 | 2789801 | 359767 | 3.91 |
| green | 6 | 3 | 0 | 0 | 416 | 209 | 56 | 108 | 18529 | 2523553 | 258130 | 2.94 |
| refactor | 6 | 3 | 0 | 0 | 266 | 140 | 40 | 80 | 12918 | 1823576 | 251220 | 2.63 |
| pin | 2 | 2 | 0 | 0 | 48 | 33 | 7 | 14 | 3228 | 257912 | 78213 | 0.74 |
| structural | 2 | 0 | 0 | 0 | 55 | 39 | 12 | 24 | 3308 | 513348 | 76782 | 0.78 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 12 | 12 | 0 | 0 | 534 | 284 | 72 | 140 | 26038 | 3004969 | 483779 | 4.99 |
| developer | claude-opus-5-5 | 13 | 0 | 0 | 0 | 575 | 392 | 108 | 206 | 36616 | 4961653 | 576895 | 6.34 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| a step line whose description quotes the added mark mid-text, but whose text does not end in that mark before any criterion mark, is not counted against VERI_STEP_GROWTH: with the budget at 1 and such a step in the ledger, inserting one step still exits 0 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 148 | 44 | 88 | 13683 | 2010690 | 249879 | 2.68 | 351 | unknown | 0/5 | nothing-left |  |  | full |
| a ticked step carrying the added mark whose line also ends in the refactor-pending mark is still counted against VERI_STEP_GROWTH: with the budget at 1 and one such step in the ledger, inserting one more exits 1 ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 201 | 52 | 96 | 17852 | 2266955 | 261711 | 2.90 | 384 | unknown | 1/5 | structural-owed |  |  | full |
| a step line whose text ends in the added mark, before its criterion mark, is still counted against VERI_STEP_GROWTH: with the budget at 1 and one such step in the ledger, inserting one more exits 1 and files it under Owed steps ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 14 | 26 | 5599 | 606636 | 85893 | 0.92 | unknown | unknown | unknown | unknown |  |  | pin |
| steps carrying the ci-repair or suite-repair mark are still not counted against VERI_STEP_GROWTH, whether inserted or already in the ledger ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 61 | 13 | 24 | 5883 | 571398 | 89757 | 0.95 | unknown | unknown | unknown | unknown |  |  | pin |
| lines outside the step checklist that quote the added mark, a bullet under the Owed steps heading and a prose line, are never counted against VERI_STEP_GROWTH ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 157 | 43 | 84 | 15334 | 1939163 | 260090 | 2.78 | 339 | unknown | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| a step line whose description quotes the added mark mid-text, but whose text does not end in that mark before any criterion mark, is not counted against VERI_STEP_GROWTH: with the budget at 1 and such a step in the ledger, inserting one step still exits 0 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 81 | 0.84 |
| a ticked step carrying the added mark whose line also ends in the refactor-pending mark is still counted against VERI_STEP_GROWTH: with the budget at 1 and one such step in the ledger, inserting one more exits 1 ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 96 | 0.92 |
| lines outside the step checklist that quote the added mark, a bullet under the Owed steps heading and a prose line, are never counted against VERI_STEP_GROWTH ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 89 | 0.87 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| fast | 25 | 27 | 26 | 24 | 25 | 27 | 29 | 27 | 27 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 180 | 346 | 62654 | 7966622 | 1060674 | 11.33 |
