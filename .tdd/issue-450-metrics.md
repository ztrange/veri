### 📊 Metrics — issue 450

Wall time for the issue: 2177 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/478.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 5 | 1 | 2 | 440 | 11207 | 34491 | 0.29 |
| red | 13 | 5 | 0 | 0 | 622 | 511 | 109 | 210 | 51526 | 5296715 | 620563 | 7.06 |
| green | 10 | 5 | 0 | 0 | 463 | 312 | 86 | 168 | 30384 | 3846051 | 418015 | 4.72 |
| refactor | 10 | 5 | 0 | 0 | 277 | 192 | 56 | 112 | 17836 | 2390446 | 408496 | 4.10 |
| pin | 3 | 3 | 0 | 0 | 107 | 75 | 19 | 38 | 7283 | 812055 | 120533 | 1.27 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `build-develop-prompt.sh over-budget <spec> <step> <cmd> <spent> <budget>` renders a prompt carrying the step text, the spent figure, the budget figure and the issue spec ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 156 | 40 | 80 | 15111 | 1854369 | 257586 | 2.73 | 294 | unknown | 0/5 | structural-owed |
| The rendered over-budget prompt asks for the same two report shapes the exhausted phase asks for (SPLIT: lines or the needs-user answer), so exhausted-outcome.sh reads it unchanged ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 202 | 55 | 106 | 20683 | 2497817 | 261385 | 3.00 | 324 | unknown | 0/5 | nothing-structural |
| The rendered over-budget prompt states that a crossing is not a verdict and that "one behaviour, simply expensive" is an available answer ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 148 | 40 | 76 | 14375 | 1631636 | 237243 | 2.51 | 263 | unknown | 0/5 | nothing-structural |
| The over-budget prompt gives the "neither — one behaviour, simply expensive" answer its own report shape, telling the leaf to print no SPLIT: and no NEEDS_USER: line when it chooses it ⟦added⟧ ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 144 | 40 | 78 | 14182 | 1701566 | 244345 | 2.58 | 247 | unknown | 0/5 | structural-owed |
| A spent or budget figure that is not a non-negative decimal number exits 2 and renders nothing, both validated before any template is read ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 183 | 48 | 94 | 17104 | 2281493 | 275753 | 3.00 | 286 | unknown | 0/5 | nothing-structural |
| over-budget with fewer than five arguments after the phase exits 2 ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 69 | 15 | 30 | 7054 | 710803 | 87177 | 0.98 | unknown | unknown | unknown | unknown |
| The over-budget prompt names no rejection reason and no verdict, and the phase takes no parameter that could carry one ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 82 | 15 | 30 | 7882 | 731000 | 95554 | 1.07 | unknown | unknown | unknown | unknown |
| Every other phase renders byte-identically to before this change ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 106 | 17 | 34 | 10638 | 936583 | 108564 | 1.27 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 0 | 2 | 1 | 2 | 2 | 2 | 2 | 0 | 2 | 2 | 2 | 0 | 2 | 2 | 2 | 2 | 2 | 0 | 2 | 2 | 2 | 2 | 0 | 2 | 2 | 2 |
| fast | 4 | 3 | 3 | 3 | 3 | 4 | 4 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 271 | 530 | 107469 | 12356474 | 1602098 | 17.44 |
