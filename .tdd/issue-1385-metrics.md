### 📊 Metrics — issue 1385

Wall time for the issue: 1534 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1422.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 7 | 5 | 1 | 2 | 674 | 12489 | 31536 | 0.13 |
| red | 10 | 5 | 0 | 0 | 219 | 188 | 51 | 100 | 18559 | 2186726 | 430634 | 3.32 |
| green | 11 | 4 | 0 | 0 | 553 | 227 | 74 | 142 | 22399 | 3235396 | 400328 | 3.39 |
| refactor | 8 | 4 | 0 | 0 | 234 | 93 | 31 | 62 | 8363 | 1221197 | 317952 | 2.22 |
| predicate | 1 | 0 | 0 | 0 | 15 | 13 | 3 | 6 | 890 | 104979 | 37296 | 0.34 |
| structural | 1 | 0 | 0 | 0 | 16 | 15 | 3 | 6 | 1375 | 106715 | 39649 | 0.37 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 16 | 14 | 0 | 0 | 421 | 161 | 61 | 116 | 18526 | 2270826 | 574350 | 2.71 |
| developer | claude-opus-5-5 | 16 | 0 | 0 | 0 | 623 | 380 | 102 | 202 | 33734 | 4596676 | 683045 | 7.06 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| tick-ledger.sh without --phase, whose matcher hits a step carrying ⟦phases: …⟧, exits 2 with a stderr line naming --phase and leaves the ledger byte-identical, while a step without phases still ticks [x] exactly as before ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 141 | 46 | 88 | 13982 | 2046474 | 253061 | 2.14 | 327 | unknown | 0/5 | nothing-left |  |  | full |
| tick-ledger.sh given both --phase <p> and --refactor-pending, in either order, is refused with exit 2 and a stderr line naming both flags, leaving the ledger byte-identical ⟦criterion 2⟧ | 11 | 4 | 0 | 0 | 0 | 1 | 160 | 45 | 86 | 15627 | 1776189 | 409270 | 3.05 | 258 | unknown | 0/5 | nothing-left |  |  | full |
| the usage line tick-ledger.sh prints on a bad argument names --phase <phase> ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 103 | 34 | 68 | 11198 | 1506620 | 246936 | 1.95 | 327 | unknown | 0/5 | nothing-left |  |  | full |
| the usage line ledger-steps.sh prints on a bad argument names next-phase ⟦criterion 3⟧ | 8 | 3 | 0 | 0 | 0 | 0 | 132 | 37 | 74 | 10779 | 1525730 | 316592 | 2.49 | 256 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tick-ledger.sh without --phase, whose matcher hits a step carrying ⟦phases: …⟧, exits 2 with a stderr line naming --phase and leaves the ledger byte-identical, while a step without phases still ticks [x] exactly as before ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 91 | 0.64 |
| tick-ledger.sh given both --phase <p> and --refactor-pending, in either order, is refused with exit 2 and a stderr line naming both flags, leaving the ledger byte-identical ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 43 | 0.52 |
| the usage line tick-ledger.sh prints on a bad argument names --phase <phase> ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 49 | 0.55 |
| the usage line ledger-steps.sh prints on a bad argument names next-phase ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 51 | 0.51 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 3 | 3 | 1 | 2 | 0 | 0 | 0 | 1 | 1 | 0 | 1 |
| fast | 24 | 24 | 24 | 22 | 23 | 22 | 23 | 23 | 23 | 23 | 23 | 23 | 24 | 24 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 163 | 318 | 52260 | 6867502 | 1257395 | 9.77 |
