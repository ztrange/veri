### 📊 Metrics — issue 949

Wall time for the issue: 2206 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/963.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 24 | 20 | 2 | 4 | 1585 | 63905 | 42266 | 0.38 |
| red | 3 | 1 | 0 | 0 | 204 | 140 | 27 | 54 | 13740 | 1625067 | 173438 | 1.99 |
| green | 2 | 1 | 0 | 0 | 368 | 80 | 21 | 42 | 7213 | 1129631 | 102174 | 1.19 |
| refactor | 2 | 1 | 0 | 0 | 164 | 41 | 11 | 22 | 3700 | 519695 | 92652 | 0.92 |
| pin | 1 | 1 | 0 | 0 | 57 | 34 | 7 | 12 | 3589 | 299252 | 52323 | 0.55 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 5 | 5 | 0 | 0 | 447 | 146 | 34 | 66 | 13544 | 1623645 | 236476 | 2.49 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 370 | 169 | 34 | 68 | 16283 | 2013905 | 226377 | 2.54 |

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
| A suite run by `make test` or by `make unit` sees neither `BASH_ENV` nor `ENV` in its environment, even when the caller exported both, pinned in `make-test-env.test.sh` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 195 | 47 | 94 | 17865 | 2501000 | 302965 | 3.28 | 750 | unknown | 0/5 | nothing-structural |  |  | full |
| A suite run by `make test` that sets `BASH_ENV` itself for one case still has it in that case: a bash child it starts with its own `BASH_ENV` sources that file ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 100 | 19 | 36 | 10377 | 1072645 | 117622 | 1.36 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A suite run by `make test` or by `make unit` sees neither `BASH_ENV` nor `ENV` in its environment, even when the caller exported both, pinned in `make-test-env.test.sh` ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 164 | 0.92 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 9 | 9 | 77 | 63 | 65 | 11 |
| fast | 51 | 47 | 46 |  |  |  |
| target | 8 | 8 | 9 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 68 | 134 | 29827 | 3637550 | 462853 | 5.03 |
