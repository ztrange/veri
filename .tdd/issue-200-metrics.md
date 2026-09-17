### 📊 Metrics — issue 200

Wall time for the issue: 10016 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/272.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 6 | 2 | 0 | 0 | 3285 | 426 | 54 | 102 | 40878 | 2778113 | 230553 | 3.72 |
| pin | 1 | 1 | 0 | 0 | 184 | 87 | 11 | 22 | 5978 | 635295 | 45861 | 0.37 |
| green | 4 | 2 | 0 | 0 | 4340 | 206 | 47 | 92 | 16299 | 2631292 | 183128 | 2.26 |
| refactor | 4 | 2 | 0 | 0 | 1994 | 191 | 28 | 56 | 10791 | 1487361 | 128329 | 1.80 |

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
| The recovered attempt in `supervise-retry.test.sh` passes when the machine is loaded: a test runs it beside N busy-loop processes and asserts `1 passed` | 2 | 1 | 0 | 0 | 0 | 0 | 156 | 21 | 40 | 13072 | 1060021 | 94966 | 1.26 | unknown | unknown | unknown | unknown |
| The suite's heartbeat window leaves at least 5 s of margin over the recovered attempt's first output, without lengthening `make test` by more than that | 6 | 3 | 0 | 0 | 0 | 0 | 328 | 52 | 104 | 26000 | 2670213 | 246371 | 2.85 | 2319 | unknown | 0/5 | structural-owed |
| Any other suite under `make test` with the same collision shape (a 1 s heartbeat window a loaded CPU can miss, e.g. `supervise.test.sh`, `verify.test.sh`) is fixed alongside, or named as checked and clear | 7 | 3 | 0 | 0 | 0 | 0 | 426 | 67 | 128 | 34874 | 3801827 | 246534 | 4.05 | 7208 | unknown | 1/5 | structural-owed |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 140 | 272 | 73946 | 7532061 | 587871 | 8.16 |
