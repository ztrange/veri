### 📊 Metrics — issue 359

Wall time for the issue: 5040 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/394.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 11 | 5 | 0 | 0 | 706 | 641 | 103 | 192 | 52107 | 4677409 | 515413 | 8.80 |
| green | 12 | 6 | 0 | 0 | 1308 | 712 | 166 | 312 | 56760 | 8024775 | 574234 | 11.18 |
| refactor | 12 | 6 | 0 | 0 | 2010 | 1148 | 175 | 322 | 91535 | 8934073 | 632992 | 13.09 |
| pin | 1 | 1 | 0 | 0 | 22 | 16 | 6 | 10 | 1404 | 206526 | 38515 | 0.52 |

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
| refactor-owed.sh append writes only the structural CANDIDATES lines of a report to the file, under the named step | 6 | 3 | 0 | 0 | 0 | 0 | 499 | 82 | 164 | 39740 | 4298518 | 301475 | 6.16 | 686 | unknown | 1/5 | structural-owed |
| two append calls for different steps leave both steps' candidates in the file | 2 | 1 | 0 | 0 | 0 | 0 | 83 | 15 | 28 | 6883 | 649778 | 86210 | 1.36 | unknown | unknown | unknown | unknown |
| refactor-owed.sh render prints a "## Refactor owed" section listing every recorded candidate under its step | 6 | 3 | 0 | 0 | 0 | 0 | 413 | 68 | 122 | 30676 | 3150614 | 279130 | 5.13 | 533 | unknown | 2/5 | structural-owed |
| refactor-owed.sh render on an absent file, or one holding no candidate, exits 3 and prints nothing | 6 | 3 | 0 | 0 | 0 | 0 | 384 | 68 | 118 | 32176 | 3003160 | 281700 | 5.12 | 532 | unknown | 2/5 | structural-owed |
| SKILL.md's Refactor section runs append for each step and commits the file with that step's refactor-pending clear | 6 | 3 | 0 | 0 | 0 | 0 | 564 | 100 | 182 | 45593 | 5060468 | 326519 | 6.94 | 948 | unknown | 1/5 | structural-owed |
| SKILL.md's Draft PR section includes the render output in the PR body and omits it on exit 3 | 6 | 3 | 0 | 0 | 0 | 0 | 400 | 77 | 142 | 32709 | 3693454 | 293360 | 5.60 | 1043 | unknown | 0/5 | nothing-left |
| repair: CLAUDE.md's stated suite count matches the tree after step 5 added a suite | 4 | 2 | 0 | 0 | 0 | 0 | 174 | 40 | 80 | 14029 | 1986791 | 192760 | 3.27 | 687 | unknown | 0/5 | nothing-left |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 20 | 21 | 0 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 28 | 0 | 0 | 0 | 50 | 58 | 52 | 49 | 50 | 0 | 0 | 50 | 59 | 202 | 21 | 23 | 0 | 195 |
| fast | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 195 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 450 | 836 | 201806 | 21842783 | 1761154 | 33.58 |
