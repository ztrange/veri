### 📊 Metrics — issue 357

Wall time for the issue: 2483 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/392.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 4 | 2 | 0 | 0 | 326 | 275 | 60 | 108 | 22551 | 2811932 | 197630 | 3.95 |
| green | 4 | 2 | 0 | 0 | 1095 | 228 | 57 | 102 | 17070 | 2413516 | 170455 | 3.34 |
| refactor | 4 | 2 | 0 | 0 | 618 | 189 | 38 | 64 | 13512 | 1406870 | 165528 | 2.70 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| The green verifier prompt REJECTs production code no test requires — a branch, option, flag or parameter whose removal leaves every test green — and names that code in `REASON:` | 6 | 3 | 0 | 0 | 0 | 0 | 376 | 77 | 138 | 28608 | 3369639 | 271314 | 5.11 | unknown | unknown | 0/5 | nothing-structural |
| The green verifier prompt tells the verifier to establish that by removing the code and running the suite, then restoring the tree and confirming with `git diff --exit-code` before reporting | 6 | 3 | 0 | 0 | 0 | 0 | 316 | 78 | 136 | 24525 | 3262679 | 262299 | 4.87 | 1096 | unknown | 0/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 204 | 204 | 206 | 2 | 2 | 2 | 213 | 206 | 197 |
| fast | 0 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |
| target | 2 | 2 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 155 | 274 | 53133 | 6632318 | 533613 | 9.98 |
