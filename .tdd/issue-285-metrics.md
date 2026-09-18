### 📊 Metrics — issue 285

Wall time for the issue: 11732 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/306.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 5 | 2 | 0 | 0 | 1877 | 223 | 39 | 72 | 16034 | 1842080 | 186983 | 2.81 |
| green | 4 | 2 | 0 | 0 | 6611 | 208 | 27 | 54 | 7889 | 1454903 | 88118 | 1.75 |
| refactor | 4 | 2 | 0 | 0 | 2363 | 148 | 41 | 82 | 10570 | 2146146 | 154764 | 1.65 |
| pin | 1 | 1 | 0 | 0 | 651 | 80 | 22 | 38 | 7293 | 1229478 | 56658 | 0.55 |

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
| run-conductor.test.sh gives the same result with VERI_NEW_SKILL=1 ambient in its caller's environment as with it unset (22 passed, 0 failed both ways) | 6 | 3 | 0 | 0 | 0 | 0 | 250 | 50 | 100 | 14314 | 2692770 | 173811 | 2.31 | 6667 | unknown | 0/5 | nothing-left |
| run-conductor.sh does not hand VERI_NEW_SKILL to the nested claude -p conductor: a launch made with VERI_NEW_SKILL=1 re-pins as documented, yet the conductor process it starts sees no VERI_NEW_SKILL in its environment | 6 | 3 | 0 | 0 | 0 | 0 | 288 | 51 | 96 | 16389 | 2479678 | 209403 | 3.19 | 3528 | unknown | 0/5 | nothing-left |
| hermetic-suites.test.sh has a same_both_ways case that runs run-conductor.test.sh with and without an ambient VERI_NEW_SKILL=1 and fails if the two results differ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 121 | 28 | 50 | 11083 | 1500159 | 103309 | 1.25 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 129 | 246 | 41786 | 6672607 | 486523 | 6.76 |
