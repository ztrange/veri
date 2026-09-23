### 📊 Metrics — issue 433

Wall time for the issue: 1060 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/438.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 3 | 1 | 0 | 0 | 220 | 197 | 41 | 74 | 15948 | 1941292 | 147296 | 2.84 |
| green | 2 | 1 | 0 | 0 | 124 | 101 | 27 | 52 | 8209 | 1270719 | 87297 | 1.71 |
| refactor | 2 | 1 | 0 | 0 | 200 | 183 | 25 | 44 | 14162 | 1191127 | 100089 | 1.95 |
| pin | 1 | 1 | 0 | 0 | 49 | 42 | 9 | 16 | 3675 | 374191 | 42900 | 0.71 |

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
| A PREDICTION verdict word carrying trailing punctuation is read as that verdict, for both verdicts and for comma, semicolon, colon and full stop | 6 | 3 | 0 | 0 | 0 | 0 | 393 | 77 | 140 | 30591 | 3559276 | 280107 | 5.35 | 567 | unknown | 2/5 | structural-owed |
| A first word that is not a verdict once its trailing punctuation is stripped is still exit 2 | 2 | 1 | 0 | 0 | 0 | 0 | 130 | 25 | 46 | 11403 | 1218053 | 97475 | 1.87 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 0 | 3 | 0 | 0 | 1 | 1 | 1 |
| fast | 3 | 2 | 2 |  |  |  |  |  |  |
| target | 1 | 0 | 1 | 0 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 102 | 186 | 41994 | 4777329 | 377582 | 7.22 |
