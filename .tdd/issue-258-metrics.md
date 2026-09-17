### 📊 Metrics — issue 258

Wall time for the issue: 5230 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/283.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 4 | 1 | 0 | 0 | 1914 | 309 | 38 | 74 | 28888 | 1866282 | 199771 | 3.14 |
| green | 2 | 1 | 0 | 0 | 1513 | 275 | 35 | 62 | 22342 | 1835441 | 105851 | 1.51 |
| refactor | 2 | 1 | 0 | 0 | 614 | 78 | 11 | 20 | 3426 | 522499 | 41417 | 1.09 |
| pin | 2 | 2 | 0 | 0 | 1031 | 295 | 47 | 94 | 23129 | 3134556 | 129958 | 1.38 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| Cases 1–5 of run-conductor.test.sh pass with origin unreachable and regardless of what origin/main holds, because they launch from a fixture clone whose origin the case controls | 6 | 3 | 0 | 0 | 0 | 0 | 469 | 64 | 118 | 35977 | 3279638 | 238876 | 3.72 | 2426 | unknown | 2/5 | nothing-structural |
| No suite under skills/tdd/scripts/tests launches run-conductor.sh against this repository's own origin; every fetch-and-pin launch uses a fixture clone | 2 | 1 | 0 | 0 | 0 | 0 | 199 | 37 | 72 | 17601 | 2109954 | 105964 | 1.66 | unknown | unknown | unknown | unknown |
| make test passes with network fetches made unreachable for the duration of the run | 2 | 1 | 0 | 0 | 0 | 0 | 289 | 30 | 60 | 24207 | 1969186 | 132157 | 1.75 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 131 | 250 | 77785 | 7358778 | 476997 | 7.13 |
