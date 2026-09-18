### 📊 Metrics — issue 262

Wall time for the issue: 4778 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/293.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 4 | 2 | 0 | 0 | 153 | 129 | 22 | 40 | 8883 | 802665 | 129535 | 1.40 |
| green | 4 | 2 | 0 | 0 | 3047 | 166 | 22 | 44 | 6447 | 936349 | 102458 | 1.66 |
| refactor | 4 | 2 | 0 | 0 | 1290 | 181 | 40 | 78 | 13904 | 1875321 | 151215 | 1.88 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| refactor-touched.sh exits 2 with a stderr diagnostic naming the commit when the commit cannot be resolved | 6 | 3 | 0 | 0 | 0 | 0 | 260 | 42 | 80 | 14519 | 1808017 | 174749 | 2.58 | 2461 | unknown | 0/5 | nothing-left |
| refactor-touched.sh exits 3 and prints nothing on stdout when the commit touches only .tdd/ | 6 | 3 | 0 | 0 | 0 | 0 | 216 | 42 | 82 | 14715 | 1806318 | 208459 | 2.35 | 2287 | unknown | 2/5 | nothing-structural |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 84 | 162 | 29234 | 3614335 | 383208 | 4.93 |
