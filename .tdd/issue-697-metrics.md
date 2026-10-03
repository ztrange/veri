### 📊 Metrics — issue 697

Wall time for the issue: 2507 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/752.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 12 | 2 | 4 | 1128 | 59863 | 40641 | 0.36 |
| red | 3 | 1 | 0 | 0 | 130 | 97 | 25 | 50 | 8183 | 1241420 | 134542 | 1.49 |
| green | 2 | 1 | 0 | 0 | 243 | 52 | 18 | 34 | 4988 | 791847 | 84415 | 0.93 |
| refactor | 2 | 1 | 0 | 0 | 83 | 42 | 10 | 20 | 3387 | 430818 | 84420 | 0.83 |
| pin | 1 | 1 | 0 | 0 | 29 | 20 | 4 | 8 | 1676 | 159493 | 39835 | 0.38 |
| diff | 2 | 1 | 0 | 0 | 35 | 23 | 6 | 12 | 1743 | 214955 | 74201 | 0.67 |
| predicate | 1 | 0 | 0 | 0 | 17 | 12 | 3 | 6 | 973 | 110595 | 39137 | 0.35 |
| structural | 1 | 0 | 0 | 0 | 44 | 28 | 6 | 12 | 2954 | 270961 | 42511 | 0.45 |
| transform | 1 | 1 | 0 | 0 | 32 | 18 | 5 | 10 | 1812 | 205012 | 38437 | 0.38 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 7 | 7 | 0 | 0 | 368 | 136 | 34 | 68 | 12205 | 1417347 | 279160 | 2.76 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 261 | 168 | 45 | 88 | 14639 | 2067617 | 298979 | 3.10 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| add-ledger-step.sh given a position word other than after, before or instead-of exits 2 and its stderr names that word ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 148 | 43 | 84 | 13187 | 1940611 | 255516 | 2.70 | 482 | unknown | 0/5 | structural-owed |  |  | full |
| after an unknown-position-word call the ledger is byte-identical and gains no ## Owed steps bullet, even when the batch would exceed VERI_STEP_GROWTH ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 63 | 14 | 28 | 5047 | 682967 | 87696 | 0.94 | unknown | unknown | unknown | unknown |  |  | pin |
| the branch leaves every existing case in add-ledger-step.test.sh unmodified, so after, before and instead-of keep today's behaviour ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 6 | 12 | 1743 | 214955 | 74201 | 0.67 | 60 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| add-ledger-step.sh given a position word other than after, before or instead-of exits 2 and its stderr names that word ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 83 | 0.83 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 2 | 0 | 57 | 2 | 2 | 2 | 2 | 8 | 2 | 5 |
| fast | 29 | 28 | 28 |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 79 | 156 | 26844 | 3484964 | 578139 | 5.86 |
