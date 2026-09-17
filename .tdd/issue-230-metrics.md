### 📊 Metrics — issue 230

Wall time for the issue: unknown s, from the first event of the log to the mark that ended the run.
Steps done: 1 of 3 planned.
Outcome: unknown — the log carries no mark ending the run.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 4 | 1 | 0 | 0 | 809 | 199 | 40 | 74 | 18655 | 1764770 | 174219 | 2.67 |
| green | 2 | 1 | 0 | 0 | 747 | 65 | 19 | 30 | 4148 | 687055 | 77021 | 0.82 |
| refactor | 2 | 1 | 0 | 0 | 985 | 112 | 6 | 12 | 1912 | 254656 | 35412 | 0.93 |
| pin | 2 | 2 | 0 | 0 | 133 | 121 | 30 | 56 | 7946 | 1549937 | 82439 | 0.72 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 120 | 1.62 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 133 | 0.72 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| SKILL.md's Refactor phase writes an `event.sh refactor` mark carrying the transforms applied, the budget and why the loop stopped | 6 | 3 | 0 | 0 | 0 | 268 | 45 | 80 | 13717 | 1861754 | 195412 | 2.80 | 2492 | unknown | 1/5 | triage |
| The refactor mark's transform count is the one `git rev-list --count` observed, and an overrun is recorded unclamped | 2 | 1 | 0 | 0 | 0 | 115 | 23 | 42 | 9073 | 1073521 | 79899 | 1.01 | unknown | unknown | unknown | unknown |
| A run's metrics report shows real `refactor` and `stopped` cells for a step whose refactor mark is present, and still `unknown` for one whose mark is absent | 2 | 1 | 0 | 0 | 0 | 114 | 27 | 50 | 9871 | 1321143 | 93780 | 1.33 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 95 | 172 | 32661 | 4256418 | 369091 | 5.14 |
