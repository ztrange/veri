### 📊 Metrics — issue 235

Wall time for the issue: 2177 s, from the first event of the log to the mark that ended the run.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/243.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 4 | 1 | 0 | 0 | 522 | 178 | 26 | 50 | 10618 | 1043890 | 116304 | 2.27 |
| green | 2 | 1 | 0 | 0 | 727 | 95 | 24 | 42 | 4687 | 1026565 | 68171 | 0.77 |
| refactor | 2 | 1 | 0 | 0 | 383 | 81 | 17 | 34 | 5540 | 857177 | 73923 | 0.75 |
| pin | 2 | 2 | 0 | 0 | 121 | 99 | 30 | 52 | 8489 | 1442552 | 85822 | 0.72 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A log carrying a `pin` mark for a step, and no `step-done` mark for that step, counts that step as done in the "Steps done: X of Y planned" line | 6 | 3 | 0 | 0 | 0 | 281 | 49 | 92 | 13604 | 2236234 | 184744 | 2.53 | 1602 | unknown | unknown | unknown |
| A log with two `pin` marks and one `step-done` mark for three different ledger steps reports "3 of 3 planned" | 2 | 1 | 0 | 0 | 0 | 67 | 20 | 40 | 5759 | 907655 | 67724 | 0.88 | unknown | unknown | unknown | unknown |
| A log whose steps end only in `step-done` (no `pin`) is unaffected | 2 | 1 | 0 | 0 | 0 | 105 | 28 | 46 | 9971 | 1226295 | 91752 | 1.11 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 97 | 178 | 29334 | 4370184 | 344220 | 4.52 |
