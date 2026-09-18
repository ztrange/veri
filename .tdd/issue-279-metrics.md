### 📊 Metrics — issue 279

Wall time for the issue: 6078 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/299.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 2 | 1 | 0 | 0 | 1040 | 116 | 19 | 36 | 7547 | 888495 | 79957 | 0.87 |
| green | 2 | 1 | 0 | 0 | 3981 | 93 | 24 | 48 | 6457 | 1087437 | 78077 | 1.10 |
| refactor | 2 | 1 | 0 | 0 | 926 | 86 | 16 | 32 | 6608 | 732314 | 77552 | 0.91 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| status.sh --json with a scope emits scope.solvable as a JSON number (the solvable issue count), like every other numeric field in the document | 6 | 3 | 0 | 0 | 0 | 0 | 295 | 59 | 116 | 20612 | 2708246 | 235586 | 2.87 | 6062 | unknown | 1/5 | structural-owed |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 59 | 116 | 20612 | 2708246 | 235586 | 2.87 |
