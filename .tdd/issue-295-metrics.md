### 📊 Metrics — issue 295

Wall time for the issue: 1947 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/404.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 3 | 1 | 0 | 0 | 339 | 289 | 61 | 112 | 23745 | 3604097 | 187500 | 4.27 |
| pin | 1 | 1 | 0 | 0 | 56 | 35 | 11 | 18 | 2982 | 407537 | 54295 | 0.82 |
| green | 2 | 1 | 0 | 0 | 667 | 184 | 35 | 66 | 12177 | 1723023 | 100504 | 2.17 |
| refactor | 2 | 1 | 0 | 0 | 486 | 219 | 33 | 60 | 18474 | 2052906 | 129207 | 2.78 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| a bailed run — its event log ending in a `bail` mark — reports its committed `.tdd/issue-<n>-metrics.md` verbatim on `/api/metrics`, the same as a `done` run does | 2 | 1 | 0 | 0 | 0 | 0 | 162 | 38 | 70 | 13316 | 2185775 | 127056 | 2.70 | 246 | unknown | unknown | unknown |
| an ended run whose committed `.tdd/issue-<n>-metrics.md` is missing reports a marker a viewer can tell apart from a real empty report, never the empty string | 6 | 3 | 0 | 0 | 0 | 0 | 565 | 102 | 186 | 44062 | 5601788 | 344450 | 7.35 | 1452 | unknown | 2/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 7 | 7 | 8 | 220 | 221 | 7 | 8 | 8 | 222 |
| target | 7 | 7 | 8 |  |  |  |  |  |  |
| fast | 2 | 2 | 2 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 140 | 256 | 57378 | 7787563 | 471506 | 10.04 |
