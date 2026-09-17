### 📊 Metrics — issue 242

Wall time for the issue: 4251 s, from the first event of the log to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/254.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 4 | 2 | 0 | 0 | 571 | 259 | 36 | 70 | 22474 | 1784247 | 180733 | 2.39 |
| green | 4 | 2 | 0 | 0 | 2441 | 251 | 39 | 78 | 10584 | 2169751 | 132377 | 2.40 |
| refactor | 4 | 2 | 0 | 0 | 1107 | 191 | 40 | 80 | 12715 | 2306160 | 171313 | 1.84 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| push-branch.test.sh completes in under 5 s of wall time on an unreachable origin: every case that pushes to a missing origin sets VERI_PUSH_BACKOFF=0 | 6 | 3 | 0 | 0 | 0 | 321 | 55 | 110 | 17870 | 3046803 | 213204 | 3.52 | 2184 | unknown | 0/5 | nothing-left |
| hermetic-suites.test.sh fails when a suite invokes push-branch.sh without VERI_PUSH_BACKOFF in its environment, naming the suite and line | 6 | 3 | 0 | 0 | 0 | 380 | 60 | 118 | 27903 | 3213355 | 271219 | 3.12 | 2058 | unknown | 1/5 | triage |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 115 | 228 | 45773 | 6260158 | 484423 | 6.63 |
