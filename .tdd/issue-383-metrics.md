### 📊 Metrics — issue 383

Wall time for the issue: 5858 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/405.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 8 | 4 | 0 | 0 | 590 | 485 | 115 | 194 | 39410 | 5330725 | 409272 | 7.74 |
| green | 8 | 4 | 0 | 0 | 2060 | 549 | 131 | 232 | 44869 | 6244885 | 400329 | 8.25 |
| refactor | 8 | 4 | 0 | 0 | 2526 | 1031 | 154 | 294 | 84431 | 9530327 | 477876 | 11.66 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| timed-test-run.sh records the test command's exit status on its `test-run` event, so a reader can say whether that run passed | 6 | 3 | 0 | 0 | 0 | 0 | 398 | 76 | 138 | 33183 | 3683248 | 288971 | 5.56 | 608 | unknown | 3/5 | nothing-structural |
| /api/tests lists one entry per `test-run` mark in the selected run's event log, rather than per leaf Bash call matching the spec's command | 6 | 3 | 0 | 0 | 0 | 0 | 605 | 113 | 208 | 49721 | 6586383 | 344340 | 7.98 | 1509 | unknown | 2/5 | structural-owed |
| each /api/tests entry names the suites that test run covered and whether it passed | 6 | 3 | 0 | 0 | 0 | 0 | 507 | 103 | 184 | 41153 | 5236144 | 316825 | 6.82 | 1600 | unknown | 2/5 | structural-owed |
| a run whose event log holds no `test-run` mark answers an empty tests list, and a run's entries never include another run's test runs | 6 | 3 | 0 | 0 | 0 | 0 | 555 | 108 | 190 | 44653 | 5600162 | 337341 | 7.29 | 1884 | unknown | 3/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 6 | 7 | 1 | 1 | 1 | 13 | 1 | 1 | 1 | 8 | 8 | 222 | 220 | 7 | 7 | 7 | 7 | 222 | 8 | 9 | 221 | 222 | 8 | 9 | 221 | 222 | 8 | 8 | 8 | 223 | 222 | 9 | 222 |
| fast | 2 | 1 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 2 | 1 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 8 | 9 | 8 | 7 | 222 | 222 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 400 | 720 | 168710 | 21105937 | 1287477 | 27.65 |
