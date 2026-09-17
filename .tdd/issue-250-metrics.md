### 📊 Metrics — issue 250

Wall time for the issue: 3398 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/263.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 3 | 1 | 0 | 0 | 1051 | 212 | 40 | 74 | 16761 | 2073352 | 154170 | 2.18 |
| green | 2 | 1 | 0 | 0 | 950 | 105 | 23 | 46 | 6254 | 1215659 | 78505 | 0.88 |
| refactor | 2 | 1 | 0 | 0 | 462 | 85 | 8 | 16 | 2719 | 341418 | 36102 | 1.06 |
| pin | 1 | 1 | 0 | 0 | 817 | 132 | 1 | 2 | 49 | 88909 | 299 | 0.88 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| SKILL.md's Refactor phase records stopped=nothing-structural for refactor-triage.sh exit 3 and stopped=structural-owed for exit 0, with no stopped=triage left, while stopped=malformed, stopped=nothing-left and stopped=budget stay unchanged | 6 | 3 | 0 | 0 | 0 | 0 | 348 | 61 | 118 | 21028 | 3188720 | 217591 | 3.27 | 2478 | unknown | 2/5 | nothing-structural |
| A metrics.test.sh case feeds two refactor marks, one stopped=nothing-structural and one stopped=structural-owed, and asserts each step's row shows its own value | 2 | 1 | 0 | 0 | 0 | 0 | 186 | 11 | 20 | 4755 | 530618 | 51485 | 1.74 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 72 | 138 | 25783 | 3719338 | 269076 | 5.00 |
