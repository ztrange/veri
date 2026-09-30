### 📊 Metrics — issue 565

Wall time for the issue: 5148 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 8 of 18 planned.
Outcome: the run was stopped — mode at-ledger, at green.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 27 | 22 | 4 | 8 | 1930 | 145310 | 34748 | 0.35 |
| red | 18 | 9 | 0 | 0 | 766 | 562 | 146 | 282 | 46046 | 6015560 | 702398 | 7.74 |
| green | 20 | 9 | 1 | 0 | 3257 | 950 | 217 | 424 | 81032 | 10222393 | 897148 | 10.84 |
| refactor | 16 | 8 | 0 | 0 | 584 | 354 | 89 | 176 | 28891 | 3464669 | 603141 | 6.10 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 92 | 0.83 |
| green | 2136 | 2.82 | 128 | 0.96 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| comment-class.sh --sweepable omits a tab-indented `#!` line that opens a `<<-` heredoc's body, since bash strips the tabs before writing it ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 156 | 37 | 72 | 12725 | 1437359 | 217222 | 2.28 | 319 | unknown | 0/5 | nothing-left |  |  | full |
| comment-class.sh classifies every `#` line of a file and drops none after a `"$(cmd 'a "b')"` shape (a `"` inside a single-quoted argument inside `"$(…)"`) ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 431 | 88 | 168 | 37026 | 4134723 | 358920 | 4.44 | 2432 | 1/2 | 1/5 | nothing-left |  |  | full |
| The sweepable report is empty for every shell file under `tests/unit/` whose name starts with c through e, other than `comment-class.test.sh` ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 234 | 57 | 112 | 18899 | 2533372 | 252720 | 2.91 | 381 | unknown | 0/5 | nothing-left |  |  | full |
| The sweepable report is empty for `tests/unit/ledger.test.sh`, the one unit suite starting with a letter no criterion names | 6 | 3 | 0 | 0 | 0 | 0 | 147 | 43 | 86 | 13328 | 1783329 | 226484 | 2.44 | 280 | unknown | 0/5 | nothing-left |  |  | full |
| The sweepable report is empty for every shell file under `tests/unit/` whose name starts with m through p ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 239 | 57 | 114 | 20803 | 2673458 | 265701 | 3.08 | 376 | unknown | 0/5 | nothing-left |  |  | full |
| The sweepable report is empty for `tests/unit/red-divergence.test.sh` ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 166 | 44 | 88 | 13386 | 1866459 | 237009 | 2.54 | 303 | unknown | 0/5 | nothing-left |  |  | full |
| The sweepable report is empty for `tests/unit/run-affordable.test.sh` ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 153 | 42 | 78 | 12745 | 1654425 | 237133 | 2.48 | 285 | unknown | 0/5 | nothing-left |  |  | full |
| The sweepable report is empty for `tests/unit/step-budget.test.sh` and `tests/unit/step-cost.test.sh` ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 200 | 49 | 96 | 16125 | 2126098 | 248246 | 2.73 | 393 | unknown | 0/5 | nothing-left |  |  | full |
| The sweepable report is empty for `tests/unit/stop-requested.test.sh` ⟦criterion 6⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 140 | 35 | 68 | 10932 | 1493399 | 159252 | 1.79 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| comment-class.sh --sweepable omits a tab-indented `#!` line that opens a `<<-` heredoc's body, since bash strips the tabs before writing it ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 70 | 0.70 |
| comment-class.sh classifies every `#` line of a file and drops none after a `"$(cmd 'a "b')"` shape (a `"` inside a single-quoted argument inside `"$(…)"`) ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 103 | 0.80 |
| The sweepable report is empty for every shell file under `tests/unit/` whose name starts with c through e, other than `comment-class.test.sh` ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 86 | 0.86 |
| The sweepable report is empty for `tests/unit/ledger.test.sh`, the one unit suite starting with a letter no criterion names | 1 | 0/5 | nothing-left | PASS | 0 | 60 | 0.72 |
| The sweepable report is empty for every shell file under `tests/unit/` whose name starts with m through p ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 88 | 0.88 |
| The sweepable report is empty for `tests/unit/red-divergence.test.sh` ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 63 | 0.72 |
| The sweepable report is empty for `tests/unit/run-affordable.test.sh` ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 53 | 0.67 |
| The sweepable report is empty for `tests/unit/step-budget.test.sh` and `tests/unit/step-cost.test.sh` ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 61 | 0.74 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 2 | 3 | 3 | 0 | 3 | 3 | 3 | 0 | 65 | 0 | 68 | 0 | 67 | 4 | 4 | 3 | 3 | 3 | 4 | 7 | 0 | 0 | 7 | 0 | 0 | 6 | 4 | 4 | 4 | 4 | 4 | 0 | 3 | 4 | 3 | 6 | 0 | 0 | 6 | 0 | 0 | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 4 | 4 | 4 | 5 | 5 | 4 | 4 | 4 | 5 | 4 | 3 | 3 | 4 | 0 | 13 | 50 | 5 | 3 | 4 | 4 | 4 | 4 |
| fast | 11 | 10 | 10 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 12 | 11 | 10 | 11 | 10 | 10 | 11 | 10 | 10 | 11 | 10 | 10 | 11 | 10 | 11 | 10 | 10 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 3 | 0 | 4 | 3 | 3 | 3 | 0 | 4 | 3 | 3 | 4 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 742 | 742 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 456 | 890 | 157899 | 19847932 | 2237435 | 25.03 |
