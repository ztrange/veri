### 📊 Metrics — issue 251

Wall time for the issue: 2028 s, from the first event of the log to the mark that ended the run.
Steps done: unknown of 7 planned.
Outcome: the run bailed — no-verdict, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 2 | 1 | 0 | 0 | 437 | 86 | 14 | 28 | 7996 | 680481 | 85145 | 0.93 |
| green | 2 | 1 | 0 | 0 | 1234 | 144 | 8 | 16 | 2371 | 369912 | 40931 | 1.08 |
| refactor | 2 | 0 | 0 | 0 | 282 | 79 | 21 | 42 | 7378 | 1039311 | 75673 | 0.95 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 437 | 0.93 |
| green | 0 | 0.00 | 1234 | 1.08 |
| refactor | 0 | 0.00 | 282 | 0.95 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A run launched by `run-conductor.sh` while the skill's clone is behind `origin/<default>` executes the skill at `origin/<default>`'s tip: a script changed only on the remote is the version in the base directory the conductor is handed | 6 | 2 | 0 | 0 | 0 | 309 | 43 | 86 | 17745 | 2089704 | 201749 | 2.96 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 43 | 86 | 17745 | 2089704 | 201749 | 2.96 |
