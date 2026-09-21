### 📊 Metrics — issue 194

Wall time for the issue: 3826 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/400.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 7 | 3 | 0 | 0 | 879 | 831 | 124 | 224 | 61889 | 6984246 | 442372 | 9.46 |
| green | 6 | 3 | 0 | 0 | 994 | 456 | 104 | 190 | 36647 | 5426780 | 337050 | 7.00 |
| refactor | 6 | 3 | 0 | 0 | 1358 | 724 | 138 | 268 | 56776 | 8495145 | 373632 | 9.40 |
| pin | 1 | 1 | 0 | 0 | 44 | 38 | 11 | 18 | 3239 | 448485 | 48051 | 0.79 |

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
| Resume resets a dirty worktree before it asks for a pending refactor, so a resume with no step carrying the refactor-pending mark still discards the stray work | 6 | 3 | 0 | 0 | 0 | 0 | 530 | 106 | 200 | 42791 | 5860822 | 345666 | 7.46 | 921 | unknown | 2/5 | structural-owed |
| Resume captures the dirty paths before the reset and names them in the `### ▶️ Resuming` comment | 6 | 3 | 0 | 0 | 0 | 0 | 740 | 126 | 222 | 53157 | 6999688 | 367382 | 8.50 | 1445 | unknown | 3/5 | nothing-structural |
| The Draft PR step's refusal names a remedy that applies with a dirty tree, no pending step and no unchecked step, and the run reaches the PR after it | 6 | 3 | 0 | 0 | 0 | 0 | 568 | 110 | 216 | 45319 | 6632037 | 373923 | 8.19 | 961 | unknown | 2/5 | nothing-structural |
| The Resume section states that a killed Red or Green leaf leaves the same stray work a killed refactor leaf does | 2 | 1 | 0 | 0 | 0 | 0 | 211 | 35 | 62 | 17284 | 1862109 | 114134 | 2.50 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 59 | 60 | 53 | 53 | 1 | 0 | 0 | 53 | 205 | 52 | 52 | 53 | 59 | 0 | 0 | 51 | 58 | 51 | 52 | 51 | 0 | 1 | 0 |
| fast | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 377 | 700 | 158551 | 21354656 | 1201105 | 26.66 |
