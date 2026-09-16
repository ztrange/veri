### 📊 Metrics — issue 228

Wall time for the issue: unknown s, from the first event of the log to the mark that ended the run.
Steps done: 1 of 3 planned.
Outcome: unknown — the log carries no mark ending the run.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 4 | 1 | 0 | 0 | 711 | 178 | 39 | 74 | 16380 | 1687194 | 173478 | 2.68 |
| green | 2 | 1 | 0 | 0 | 848 | 84 | 23 | 42 | 7240 | 1089198 | 87248 | 1.00 |
| refactor | 2 | 1 | 0 | 0 | 440 | 130 | 10 | 20 | 4695 | 567285 | 40537 | 0.95 |
| pin | 2 | 2 | 0 | 0 | 319 | 126 | 24 | 44 | 8925 | 1152810 | 75344 | 0.63 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 507 | 1.45 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 319 | 0.63 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A leaf log whose last result record has no VERDICT: line, but an earlier result record does, yields that verdict and its reason — exit 0 on PASS, 1 on REJECT — not exit 2 | 6 | 3 | 0 | 0 | 0 | 301 | 53 | 100 | 19077 | 2561113 | 219287 | 3.18 | 1553 | unknown | unknown | unknown |
| A leaf log with no VERDICT: line in any result record still exits 2 with the same diagnostic | 2 | 1 | 0 | 0 | 0 | 139 | 25 | 50 | 12477 | 1262050 | 88489 | 1.27 | unknown | unknown | unknown | unknown |
| The newest VERDICT: wins when more than one result record carries one | 2 | 1 | 0 | 0 | 0 | 78 | 18 | 30 | 5686 | 673324 | 68831 | 0.80 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 96 | 180 | 37240 | 4496487 | 376607 | 5.26 |
