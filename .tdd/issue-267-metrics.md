### 📊 Metrics — issue 267

Wall time for the issue: 1658 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/380.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 4 | 2 | 0 | 0 | 340 | 315 | 47 | 86 | 23864 | 2171844 | 191062 | 3.59 |
| green | 4 | 2 | 0 | 0 | 411 | 211 | 45 | 80 | 17398 | 1901758 | 171843 | 3.10 |
| refactor | 4 | 2 | 0 | 0 | 406 | 211 | 41 | 76 | 16602 | 1913321 | 187428 | 3.25 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| skill-metrics.test.sh no longer contains the commit_line -gt pr_line comparison or the comment describing it, and the suite still passes | 6 | 3 | 0 | 0 | 0 | 0 | 409 | 70 | 122 | 33352 | 3059390 | 284739 | 5.21 | 587 | unknown | 1/5 | structural-owed |
| skill-metrics.test.sh no longer contains the gh pr create + 📊 metrics record-level presence probe, and the suite still passes | 6 | 3 | 0 | 0 | 0 | 0 | 328 | 63 | 120 | 24512 | 2927533 | 265594 | 4.73 | 789 | unknown | 1/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 172 | 172 | 0 |
| fast | 0 | 0 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |
| target | 0 | 0 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 133 | 242 | 57864 | 5986923 | 550333 | 9.94 |
