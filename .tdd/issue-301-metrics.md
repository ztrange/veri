### 📊 Metrics — issue 301

Wall time for the issue: 3477 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: unknown of 5 planned.
Outcome: the run bailed — no-verdict, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 2 | 1 | 0 | 0 | 116 | 96 | 16 | 28 | 7749 | 754035 | 100472 | 1.16 |
| green | 2 | 1 | 0 | 0 | 2917 | 172 | 23 | 48 | 5779 | 1353573 | 46467 | 2.33 |
| refactor | 2 | 0 | 0 | 0 | 323 | 12 | 4 | 8 | 1107 | 142697 | 35807 | 0.46 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 116 | 1.16 |
| green | 0 | 0.00 | 2917 | 2.33 |
| refactor | 0 | 0.00 | 323 | 0.46 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `make test` runs every suite under the offline shim with a per-suite reach log, so a suite that runs `git fetch` against a remote URL, `gh` or `curl` fails `make test`, naming the suite and what it tried ⟦criterion 3⟧ | 6 | 2 | 0 | 0 | 0 | 0 | 280 | 43 | 84 | 14635 | 2250305 | 182746 | 3.95 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 43 | 84 | 14635 | 2250305 | 182746 | 3.95 |
