### 📊 Metrics — issue 305

Wall time for the issue: 1991 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/376.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 2 | 0 | 0 | 0 | 1184 | 617 | 63 | 118 | 49656 | 4911378 | 189679 | 5.59 |
| pin | 2 | 2 | 0 | 0 | 502 | 286 | 38 | 70 | 21546 | 2010441 | 119790 | 2.74 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| run-conductor.test.sh is green when VERI_NEW_SKILL=1 and VERI_SKILL_COMMIT=<any sha> are set in the ambient environment | 2 | 1 | 0 | 0 | 0 | 0 | 485 | 59 | 106 | 40958 | 4188303 | 166424 | 4.78 | unknown | unknown | unknown | unknown |
| hermetic-suites.test.sh fails, naming the suite, when a suite's answer changes with an ambient VERI_SKILL_COMMIT | 2 | 1 | 0 | 0 | 0 | 0 | 418 | 42 | 82 | 30244 | 2733516 | 143045 | 3.55 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier |
| --- |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 101 | 188 | 71202 | 6921819 | 309469 | 8.34 |
