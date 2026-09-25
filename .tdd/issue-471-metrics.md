### 📊 Metrics — issue 471

Wall time for the issue: 3331 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/475.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 24 | 20 | 2 | 4 | 1740 | 55993 | 36038 | 0.33 |
| red | 7 | 1 | 0 | 0 | 743 | 416 | 78 | 146 | 41779 | 4023420 | 375679 | 4.65 |
| green | 4 | 1 | 1 | 0 | 1465 | 153 | 34 | 68 | 14809 | 1626832 | 141918 | 1.76 |
| refactor | 2 | 1 | 0 | 0 | 96 | 46 | 14 | 28 | 4196 | 628882 | 82097 | 0.87 |
| pin | 5 | 5 | 0 | 0 | 354 | 124 | 28 | 56 | 11873 | 1145337 | 197052 | 2.04 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1465 | 1.76 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A launch through supervise.sh under one name is refused while a stub leaf supervised under a different name is still alive in the same worktree — exit 2, no second leaf started, stderr naming the live leaf and its pid ⟦criterion 5⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 306 | 69 | 134 | 29379 | 3357887 | 333309 | 3.93 | 1867 | 1/2 | 1/5 | structural-owed |
| A launch through supervise.sh is refused the same way while a stub leaf supervised under the same name is still alive in the same worktree ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 76 | 15 | 30 | 7819 | 742353 | 91891 | 1.04 | unknown | unknown | unknown | unknown |
| The record the refusal reads survives the pre-launch rm -f .tdd/<name>.exit .tdd/<name>.pid, so the launch after that rm is still refused while the first leaf lives ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 116 | 20 | 38 | 11162 | 969410 | 93946 | 1.17 | unknown | unknown | unknown | unknown |
| A record left by a supervised leaf whose process is gone does not refuse the next launch ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 76 | 16 | 30 | 8067 | 703433 | 89661 | 1.02 | unknown | unknown | unknown | unknown |
| A launch after the previous supervised leaf finished runs as today — under a different name, and a revise relaunch under the same name ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 84 | 17 | 32 | 8544 | 798966 | 95011 | 1.09 | unknown | unknown | unknown | unknown |
| A supervised launch made from inside a live supervised leaf — verify.sh's own verify-<phase> leaf under a live verdict-<phase> wrapper — is not refused | 2 | 1 | 0 | 0 | 0 | 0 | 81 | 17 | 34 | 7686 | 852422 | 92928 | 1.07 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 18 | 19 | 18 | 19 | 18 | 18 | 18 | 19 | 18 | 19 | 20 | 20 | 21 |
| fast | 3 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |
| target | 18 | 19 | 18 | 19 | 19 | 20 | 20 | 19 | 15 | 21 | 16 | 21 | 21 |
| all | 342 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 156 | 302 | 74397 | 7480464 | 832784 | 9.65 |
