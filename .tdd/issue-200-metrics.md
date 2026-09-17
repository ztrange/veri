### 📊 Metrics — issue 200

Wall time for the issue: 4067 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/272.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 8 | 3 | 0 | 0 | 4865 | 569 | 69 | 132 | 52609 | 3574828 | 335062 | 5.08 |
| pin | 1 | 1 | 0 | 0 | 184 | 87 | 11 | 22 | 5978 | 635295 | 45861 | 0.37 |
| green | 6 | 3 | 0 | 0 | 5919 | 398 | 77 | 148 | 29632 | 4235295 | 294924 | 3.90 |
| refactor | 6 | 3 | 0 | 0 | 2797 | 322 | 46 | 92 | 22331 | 2458710 | 214252 | 2.70 |

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
| The late-start check in `hermetic-suites.test.sh` (a leaf started 3 s late under a window short of 6 s) runs only the `supervise.test.sh` and `verify.test.sh` cases whose widened windows it protects, not a full second pass of either suite, so `make test` stays inside CI's `timeout-minutes: 3` | 6 | 3 | 0 | 0 | 0 | 0 | 466 | 63 | 122 | 36604 | 3372067 | 302228 | 3.89 | 4045 | unknown | 0/5 | nothing-left |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 203 | 394 | 110550 | 10904128 | 890099 | 12.05 |
