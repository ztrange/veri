### 📊 Metrics — issue 1594

Wall time for the issue: 2008 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1595.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 37 | 26 | 4 | 8 | 3026 | 134901 | 89387 | 0.40 |
| red | 6 | 2 | 0 | 0 | 221 | 115 | 36 | 72 | 13801 | 1874413 | 309909 | 1.57 |
| green | 4 | 2 | 0 | 0 | 470 | 74 | 26 | 52 | 7912 | 1294123 | 186782 | 0.96 |
| refactor | 4 | 2 | 0 | 0 | 196 | 42 | 18 | 34 | 4074 | 776942 | 182443 | 0.85 |
| pin | 2 | 2 | 0 | 0 | 84 | 37 | 9 | 18 | 3428 | 410608 | 93001 | 0.45 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 9 | 1 | 0 | 549 | 155 | 46 | 90 | 16042 | 2071624 | 458843 | 2.20 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 459 | 139 | 47 | 94 | 16199 | 2419363 | 402679 | 2.01 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A row whose old suite holds exactly one case reads `proven` when, under the mutation, that suite runs to its count line (`0 passed, 1 failed`) with the named case failed and the replacement is caught ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 33 | 66 | 9678 | 1623558 | 288179 | 1.41 | 419 | unknown | 0/5 | nothing-left |  |  | full |
| A row whose old suite holds exactly one case reads `owed` when, under the mutation, that suite dies before its count line, instead of mutation-parity.sh stopping with no row ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 97 | 32 | 62 | 10580 | 1501467 | 284061 | 1.39 | 500 | unknown | 0/5 | nothing-left |  |  | full |
| A row whose old suite holds exactly one case reads `unproven` when, under the mutation, that suite runs to its count line with the named case failed but the replacement is not caught ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 12 | 24 | 4278 | 617157 | 99902 | 0.50 | unknown | unknown | unknown | unknown |  |  | pin |
| Regression pin, no production change (the behaviour already holds, so this step's test passes against the unmodified code and takes the pin path): a row whose old suite holds more than one case is judged as before the change: `proven` only when the named case fails, at least one other case passes and the replacement is caught, and `owed` when the mutation fails every case of that multi-case suite ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 12 | 24 | 4679 | 613904 | 99993 | 0.51 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A row whose old suite holds exactly one case reads `proven` when, under the mutation, that suite runs to its count line (`0 passed, 1 failed`) with the named case failed and the replacement is caught ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 101 | 0.43 |
| A row whose old suite holds exactly one case reads `owed` when, under the mutation, that suite dies before its count line, instead of mutation-parity.sh stopping with no row ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 95 | 0.42 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 8 | 0 | 9 | 3 | 1 | 0 | 9 | 10 | 9 | 9 | 10 |
| fast | 57 | 57 | 59 | 63 | 61 | 59 | 57 |  |  |  |  |
| target | 9 | 10 | 10 | 10 | 11 | 11 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 93 | 184 | 32241 | 4490987 | 861522 | 4.22 |
