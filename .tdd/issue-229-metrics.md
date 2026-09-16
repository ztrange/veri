### 📊 Metrics — issue 229

Wall time for the issue: unknown s, from the first event of the log to the mark that ended the run.
Steps done: 1 of 4 planned.
Outcome: unknown — the log carries no mark ending the run.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 5 | 1 | 0 | 0 | 240 | 197 | 46 | 82 | 18123 | 1865191 | 208821 | 3.16 |
| pin | 3 | 3 | 0 | 0 | 250 | 212 | 51 | 98 | 17757 | 3000870 | 159895 | 1.43 |
| green | 2 | 1 | 0 | 0 | 904 | 47 | 18 | 36 | 3937 | 827642 | 65588 | 0.73 |
| refactor | 2 | 1 | 0 | 0 | 415 | 85 | 21 | 42 | 5584 | 976265 | 75130 | 0.95 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 167 | 2.41 |
| pin | 0 | 0.00 | 250 | 1.43 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A log carrying a `bail` mark followed by a `resume` and a `done` reports the run as landed, naming the PR, not as bailed. | 2 | 1 | 0 | 0 | 0 | 109 | 26 | 50 | 7948 | 1273570 | 80002 | 1.04 | unknown | unknown | unknown | unknown |
| On a log carrying a `bail`, then a `resume`, then a `done`, the issue wall runs from the last `resume` to the `done` mark, not from the log's first event. | 6 | 3 | 0 | 0 | 0 | 192 | 53 | 104 | 13943 | 2359961 | 208683 | 2.42 | 1451 | unknown | unknown | unknown |
| A log with no `resume` is unchanged: the wall still runs from its first event, and its single ending mark still decides the outcome. | 2 | 1 | 0 | 0 | 0 | 96 | 27 | 52 | 9081 | 1377847 | 89921 | 1.19 | unknown | unknown | unknown | unknown |
| Counts, times and costs stay accumulated across every run in the log — only the outcome and the wall are scoped to the last run. | 2 | 1 | 0 | 0 | 0 | 144 | 30 | 52 | 14429 | 1658590 | 130828 | 1.61 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 136 | 258 | 45401 | 6669968 | 509434 | 6.26 |
