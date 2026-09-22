### 📊 Metrics — issue 409

Wall time for the issue: 2430 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/417.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 14 | 5 | 0 | 0 | 2030 | 1453 | 241 | 422 | 119120 | 13748674 | 882729 | 18.68 |
| green | 16 | 5 | 3 | 0 | 4254 | 1276 | 243 | 444 | 105599 | 12344362 | 795203 | 16.77 |
| refactor | 14 | 5 | 1 | 0 | 3154 | 1431 | 223 | 404 | 109137 | 11966417 | 743194 | 16.15 |
| pin | 4 | 4 | 0 | 0 | 476 | 230 | 59 | 106 | 18138 | 2875023 | 203429 | 3.93 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 76 | 0.93 |
| green | 4120 | 11.05 | 0 | 0.00 |
| refactor | 1917 | 5.30 | 0 | 0.00 |
| pin | 0 | 0.00 | 48 | 0.73 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| preserve-attempt.sh commits the worktree as it stands to a ref under refs/veri/attempts/ named by issue, step, phase and attempt, and git show reads that commit's tree back | 8 | 3 | 1 | 0 | 0 | 0 | 492 | 89 | 166 | 40340 | 4171165 | 376965 | 6.86 | 1023 | 1/2 | 2/5 | structural-owed |
| preserving leaves the work branch untouched: the branch's HEAD, index and git log output are the same before and after, so a rebase-merge of the branch carries none of the preserved commit | 2 | 1 | 0 | 0 | 0 | 0 | 104 | 23 | 44 | 8694 | 1086665 | 90051 | 1.66 | unknown | unknown | unknown | unknown |
| preserve-attempt.sh also copies the leaf's progress log and its final-output file to preserved names carrying the step, phase, attempt and the mark that triggered the preservation | 10 | 3 | 2 | 0 | 0 | 0 | 721 | 129 | 226 | 60532 | 5994790 | 457388 | 9.09 | 2872 | 2/2 | 5/5 | budget |
| a REJECT or a malformed verdict makes verify.sh preserve that attempt, and the preserved names pair with the verdict event | 6 | 3 | 0 | 0 | 0 | 0 | 757 | 131 | 236 | 59219 | 7718712 | 397342 | 9.31 | 1325 | unknown | 2/5 | structural-owed |
| a malformed verdict, the no-verdict half of the same criterion, preserves the verifier attempt under its own ref and copies | 2 | 1 | 0 | 0 | 0 | 0 | 188 | 34 | 62 | 15906 | 2006882 | 137456 | 2.78 | unknown | unknown | unknown | unknown |
| a killed-stuck leaf makes supervise.sh preserve that attempt, both on a retry and on the final killed-stuck exit | 6 | 3 | 0 | 0 | 0 | 0 | 805 | 132 | 224 | 66888 | 7543757 | 421435 | 9.66 | 1261 | unknown | 1/5 | structural-owed |
| a PASS verdict and a leaf that exits success or clean failure write no ref and no preserved copy | 2 | 1 | 0 | 0 | 0 | 0 | 304 | 59 | 112 | 24182 | 4006756 | 149893 | 4.11 | unknown | unknown | unknown | unknown |
| the conductor preserves the attempt on a bail and on a prediction-diverged mark, so those two conductor-side marks are covered like the leaf-side ones | 10 | 3 | 1 | 0 | 0 | 0 | 878 | 145 | 266 | 65557 | 7373767 | 496422 | 10.29 | 18138 | 1/2 | 0/5 | nothing-structural |
| preservation changes no leaf prompt and puts the developer's rationale nowhere a verifier leaf reads: the preserved commit is unreachable from HEAD and its message carries no rationale | 2 | 1 | 0 | 0 | 0 | 0 | 141 | 24 | 40 | 10676 | 1031982 | 97603 | 1.76 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 1 | 1 | 44 | 1 | 0 | 1 | 1 | 2 | 1 | 2 | 238 | 237 | 236 | 2 | 1 | 1 | 2 | 1 | 1 | 2 | 35 | 35 | 35 | 35 | 35 | 29 | 30 | 29 | 36 | 16 | 16 | 16 | 15 | 17 | 45 | 53 | 32 | 0 | 0 | 61 | 61 | 0 | 242 | 10 | 35 | 3 |
| fast | 3 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 1 | 1 | 2 | 2 | 3 | 35 | 37 | 37 | 17 | 32 | 33 | 33 | 0 | 3 | 2 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 247 | 243 | 245 | 252 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 766 | 1376 | 351994 | 40934476 | 2624555 | 55.52 |
