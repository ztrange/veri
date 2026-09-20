### 📊 Metrics — issue 343

Wall time for the issue: 3884 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/375.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 8 | 3 | 0 | 0 | 700 | 552 | 107 | 200 | 45032 | 5336745 | 401172 | 7.81 |
| green | 6 | 3 | 0 | 0 | 1357 | 307 | 80 | 148 | 20555 | 3639291 | 263549 | 4.97 |
| refactor | 6 | 3 | 0 | 0 | 961 | 496 | 89 | 166 | 39942 | 4749877 | 300067 | 6.37 |
| pin | 2 | 2 | 0 | 0 | 167 | 96 | 23 | 42 | 7837 | 972807 | 83135 | 1.51 |

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
| status.sh prints exactly one run for a run directory, identified by that directory's own issue number, ignoring other issues' committed ledgers | 6 | 3 | 0 | 0 | 0 | 0 | 252 | 56 | 102 | 19910 | 2363736 | 250091 | 4.18 | 557 | unknown | 2/5 | structural-owed |
| With two run directories each also holding the other's committed ledger, status.sh --json prints exactly two objects, each carrying only its own directory's events totals | 2 | 1 | 0 | 0 | 0 | 0 | 173 | 27 | 52 | 12164 | 1359814 | 97523 | 1.96 | unknown | unknown | unknown | unknown |
| A run directory holding no ledger for its own issue number contributes no run and does not make status.sh exit non-zero | 2 | 1 | 0 | 0 | 0 | 0 | 122 | 24 | 46 | 10066 | 1124982 | 88922 | 1.70 | unknown | unknown | unknown | unknown |
| /api/metrics keys exactly one entry per run directory by that directory's issue number, and runs metrics.sh at most once per live run directory | 6 | 3 | 0 | 0 | 0 | 0 | 435 | 100 | 186 | 35337 | 5176428 | 309279 | 6.57 | 1377 | unknown | 2/5 | structural-owed |
| /api/events answers by the run directory's own issue number, so an issue present only as a committed ledger copy inside another run returns the empty list | 6 | 3 | 0 | 0 | 0 | 0 | 469 | 92 | 170 | 35889 | 4673760 | 302108 | 6.26 | 1166 | unknown | 1/5 | structural-owed |

#### Test-command seconds, by tier

| tier |
| --- |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 299 | 556 | 113366 | 14698720 | 1047923 | 20.67 |
