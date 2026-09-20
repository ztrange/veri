### 📊 Metrics — issue 358

Wall time for the issue: 3414 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/393.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 6 | 3 | 0 | 0 | 421 | 369 | 80 | 140 | 30113 | 3577769 | 294670 | 5.49 |
| green | 6 | 3 | 0 | 0 | 1613 | 388 | 94 | 178 | 30773 | 4500567 | 281521 | 5.84 |
| refactor | 6 | 3 | 0 | 0 | 797 | 369 | 62 | 120 | 26534 | 2819611 | 260481 | 4.68 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| The refactor developer prompt permits a transform in a file outside the touched-files list only when it removes duplication between that file and code this cycle wrote | 6 | 3 | 0 | 0 | 0 | 0 | 332 | 77 | 148 | 26207 | 3642015 | 274922 | 5.23 | 1083 | unknown | 0/5 | nothing-structural |
| The refactor developer prompt tells the leaf to run the suites covering every file a transform touched, the out-of-list file included | 6 | 3 | 0 | 0 | 0 | 0 | 497 | 84 | 158 | 36859 | 4100508 | 298560 | 5.96 | 1037 | unknown | 1/5 | nothing-structural |
| The refactor verifier prompt derives the cycle's files as `git diff --name-only <base-sha>^ <base-sha>` and REJECTs a changed file outside that list unless its hunk removes duplication with code in it | 6 | 3 | 0 | 0 | 0 | 0 | 297 | 75 | 132 | 24354 | 3155424 | 263190 | 4.82 | 1043 | unknown | 0/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 195 | 193 | 194 | 1 | 1 | 1 | 194 | 194 | 1 | 1 | 2 | 2 | 2 | 194 | 195 | 194 |
| fast | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 | 1 | 1 |  |  |  |  |  |  |  |  |
| target | 1 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 236 | 438 | 87420 | 10897947 | 836672 | 16.00 |
