### 📊 Metrics — issue 297

Wall time for the issue: 4825 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/429.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 6 | 2 | 0 | 0 | 1460 | 725 | 96 | 160 | 56468 | 4917823 | 389848 | 7.77 |
| green | 4 | 2 | 0 | 0 | 1249 | 520 | 78 | 136 | 40439 | 4264094 | 256504 | 5.71 |
| refactor | 4 | 2 | 0 | 0 | 1512 | 411 | 65 | 130 | 32119 | 3900507 | 226940 | 5.02 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A launch that writes no completion file under the leaf name the probe derived is reported as a failing launch line, naming that line, instead of being read back from the stub's file and passed | 8 | 3 | 0 | 0 | 0 | 0 | 927 | 134 | 230 | 72058 | 7143839 | 502893 | 10.40 | 2301 | unknown | 1/5 | structural-owed |
| The probe stops waiting on a launch once that launch's supervisor is no longer running, rather than waiting out its whole fixed wait budget, so a derived name no launch writes is answered promptly | 6 | 3 | 0 | 0 | 0 | 0 | 729 | 105 | 196 | 56968 | 5938585 | 370399 | 8.10 | 1805 | unknown | 2/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 9 | 70 | 72 | 72 | 75 | 72 | 72 | 72 | 73 | 132 | 132 | 132 | 12 | 13 | 13 | 13 | 13 |
| fast | 3 | 2 | 2 | 2 | 3 | 2 |  |  |  |  |  |  |  |  |  |  |  |
| target | 73 | 13 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 239 | 426 | 129026 | 13082424 | 873292 | 18.50 |
