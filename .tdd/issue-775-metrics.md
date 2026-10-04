### 📊 Metrics — issue 775

Wall time for the issue: 355 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 6 planned.
Outcome: the run bailed — killed-stuck, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 48 | 37 | 6 | 12 | 3423 | 229275 | 83444 | 0.78 |
| red | 9 | 4 | 0 | 0 | 637 | 341 | 84 | 160 | 29976 | 4447998 | 469708 | 5.25 |
| pin | 1 | 1 | 0 | 0 | 34 | 23 | 6 | 12 | 2032 | 274875 | 44707 | 0.45 |
| green | 5 | 1 | 0 | 1 | 445 | 132 | 35 | 68 | 11877 | 1742748 | 198275 | 2.17 |
| refactor | 2 | 1 | 0 | 0 | 79 | 28 | 10 | 20 | 2684 | 443602 | 86688 | 0.84 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 9 | 8 | 1 | 0 | 437 | 205 | 50 | 96 | 18228 | 2149151 | 391885 | 3.93 |
| developer | claude-opus-5-5 | 10 | 0 | 0 | 1 | 806 | 356 | 91 | 176 | 31764 | 4989347 | 490937 | 5.56 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 406 | 2.22 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 251 | 0.55 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| develop-green | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| tick-issue-criterion.sh, when gh fails on the body edit with any non-zero status (1, 3 and 5 alike), exits 2 and the issue body is left unchanged ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 90 | 21 | 42 | 7941 | 1172082 | 102097 | 1.21 | unknown | unknown | unknown | unknown |  |  | pin |
| refactor-overflow.sh, when gh fails filing the issue with any non-zero status (1, 3 and 5 alike), exits 2 ⟦criterion 2⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 233 | 69 | 134 | 22566 | 3545226 | 445953 | 4.73 | 416 | unknown | 0/5 | nothing-left |  |  | full |
| wait-ci.sh given a non-numeric slice or a non-numeric total exits 2 and names the bad argument on stderr, never 1 ⟦criterion 3⟧ | 6 | 2 | 0 | 1 | 0 | 0 | 201 | 45 | 84 | 16062 | 2191915 | 251328 | 2.77 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| refactor-overflow.sh, when gh fails filing the issue with any non-zero status (1, 3 and 5 alike), exits 2 ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 79 | 0.84 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 42 | 41 | 50 | 47 |
| target | 2 | 3 | 2 |  |  |  |  |  |  |  |  |  |
| fast | 37 | 37 | 36 | 38 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 141 | 272 | 49992 | 7138498 | 882822 | 9.49 |
