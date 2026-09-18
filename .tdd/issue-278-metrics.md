### 📊 Metrics — issue 278

Wall time for the issue: 6005 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/302.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 2 | 1 | 0 | 0 | 1285 | 118 | 23 | 46 | 9912 | 1224632 | 89516 | 1.05 |
| green | 2 | 1 | 0 | 0 | 3674 | 84 | 24 | 48 | 4879 | 1210353 | 40962 | 1.03 |
| refactor | 2 | 1 | 0 | 0 | 929 | 95 | 7 | 14 | 1965 | 335023 | 35576 | 1.05 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| a finished run's status line reports the attempt count its last step's launches reached, not attempt 0, when the trailing done event carries an empty step | 6 | 3 | 0 | 0 | 0 | 0 | 297 | 54 | 108 | 16756 | 2770008 | 166054 | 3.13 | 5991 | unknown | 1/5 | nothing-structural |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 54 | 108 | 16756 | 2770008 | 166054 | 3.13 |
