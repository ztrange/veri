### 📊 Metrics — issue 256

Wall time for the issue: 3906 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/274.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 3 | 0 | 0 | 0 | 1027 | 242 | 32 | 58 | 20434 | 1416969 | 149834 | 2.73 |
| pin | 3 | 3 | 0 | 0 | 955 | 330 | 56 | 104 | 27545 | 3216584 | 155593 | 1.55 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| run-conductor.test.sh case 4 passes with an uncommitted edit to skills/tdd/SKILL.md in the tree under test, comparing against the committed SKILL.md | 2 | 1 | 0 | 0 | 0 | 0 | 216 | 31 | 60 | 18927 | 1636199 | 98890 | 1.45 | unknown | unknown | unknown | unknown |
| case 4 still fails when what reaches the binary differs from the committed SKILL.md | 4 | 2 | 0 | 0 | 0 | 0 | 356 | 57 | 102 | 29052 | 2997354 | 206537 | 2.83 | unknown | 1/2 | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 88 | 162 | 47979 | 4633553 | 305427 | 4.28 |
