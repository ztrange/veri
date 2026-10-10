### 📊 Metrics — issue 1387

Wall time for the issue: 2118 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1391.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 5 | 1 | 2 | 501 | 12489 | 30857 | 0.13 |
| red | 4 | 2 | 0 | 0 | 85 | 66 | 18 | 34 | 6909 | 691665 | 161998 | 1.23 |
| green | 8 | 2 | 2 | 0 | 375 | 157 | 44 | 88 | 15064 | 1886596 | 283727 | 2.30 |
| refactor | 4 | 2 | 0 | 0 | 135 | 66 | 20 | 38 | 5497 | 789050 | 158660 | 1.17 |
| predicate | 1 | 0 | 0 | 0 | 20 | 16 | 4 | 8 | 1250 | 152794 | 36874 | 0.35 |
| structural | 1 | 0 | 0 | 0 | 16 | 10 | 6 | 10 | 1025 | 201761 | 37609 | 0.36 |
| transform | 1 | 1 | 0 | 0 | 14 | 8 | 4 | 8 | 968 | 152330 | 36550 | 0.17 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 8 | 2 | 0 | 310 | 112 | 42 | 82 | 12549 | 1635575 | 342388 | 1.66 |
| developer | claude-opus-5-5 | 10 | 0 | 0 | 0 | 343 | 216 | 55 | 106 | 18665 | 2251110 | 403887 | 4.06 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 418 | 2.60 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| For an interface `<name>.sh`, lines in `veri/<name_with_underscores>.py` (the script's own module) are not reported as callers, while a line naming it in any other product file still is ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 110 | 31 | 60 | 10119 | 1260921 | 238034 | 1.82 | 308 | unknown | 1/5 | structural-owed |  |  | full |
| Files under any `__pycache__/` directory, and any `*.pyc` file, are never scanned: a stale compiled file naming the interface is not reported as a caller ⟦criterion 2⟧ | 13 | 4 | 2 | 0 | 0 | 0 | 213 | 65 | 126 | 20594 | 2613275 | 477384 | 3.76 | 493 | 2/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| For an interface `<name>.sh`, lines in `veri/<name_with_underscores>.py` (the script's own module) are not reported as callers, while a line naming it in any other product file still is ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 80 | 0.63 |
| Files under any `__pycache__/` directory, and any `*.pyc` file, are never scanned: a stale compiled file naming the interface is not reported as a caller ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 55 | 0.55 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 0 | 0 |
| fast | 28 | 28 | 30 | 27 | 30 | 27 | 28 | 26 |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 97 | 188 | 31214 | 3886685 | 746275 | 5.71 |
