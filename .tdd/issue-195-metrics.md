### 📊 Metrics — issue 195

Wall time for the issue: 9662 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/444.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 325 | 42 | 6 | 10 | 3134 | 217144 | 42719 | 0.61 |
| red | 15 | 7 | 0 | 0 | 1759 | 1589 | 259 | 446 | 118521 | 13815719 | 922896 | 19.10 |
| green | 14 | 7 | 0 | 0 | 3528 | 1411 | 260 | 472 | 104169 | 13985085 | 827356 | 17.87 |
| refactor | 14 | 7 | 0 | 0 | 2452 | 1329 | 230 | 438 | 107807 | 12856302 | 773939 | 16.86 |
| pin | 1 | 1 | 0 | 0 | 87 | 68 | 16 | 26 | 5669 | 706721 | 54387 | 1.04 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| SKILL.md step 2 pushes the branch and opens a draft PR whose body carries Closes #<n> and whose title marks the work in progress, right after the plan commit and before the Plan comment | 6 | 3 | 0 | 0 | 0 | 0 | 653 | 117 | 218 | 52398 | 6984801 | 371422 | 8.52 | 1342 | unknown | 2/5 | structural-owed |
| SKILL.md updates the PR body with the done-of-total step count read from the ledger at each step tick | 6 | 3 | 0 | 0 | 0 | 0 | 507 | 101 | 186 | 38107 | 5409249 | 345065 | 7.11 | 873 | unknown | 1/5 | structural-owed |
| SKILL.md step 4 creates no PR: it rewrites the existing one's title and body and marks it ready for review | 6 | 3 | 0 | 0 | 0 | 0 | 691 | 110 | 192 | 56625 | 5962485 | 383946 | 8.24 | 1379 | unknown | 2/5 | structural-owed |
| SKILL.md resume reuses the open PR already on the run's branch and never creates a second one | 6 | 3 | 0 | 0 | 0 | 0 | 699 | 107 | 192 | 49256 | 5579322 | 347113 | 7.49 | 1073 | unknown | 1/5 | structural-owed |
| SKILL.md Bailing leaves the draft PR open carrying the bail diagnostic, in place of opening no PR | 6 | 3 | 0 | 0 | 0 | 0 | 423 | 98 | 170 | 35545 | 4862143 | 336631 | 6.69 | 794 | unknown | 1/5 | structural-owed |
| solvable-issues.sh leaves out an issue claimed by an open PR saying Closes #<n> even when no conductor pid answers | 2 | 1 | 0 | 0 | 0 | 0 | 162 | 37 | 66 | 12500 | 2040349 | 121912 | 2.55 | 233 | unknown | unknown | unknown |
| CONTEXT.md, the solvable-issues.sh header comment and a new ADR state that an open PR is the cross-machine claim and the pid lock is only the same-machine worktree guard | 6 | 3 | 0 | 0 | 0 | 0 | 800 | 103 | 190 | 59280 | 5914467 | 360034 | 8.04 | 1863 | unknown | 2/5 | structural-owed |
| SKILL.md step 1.2 no longer says the only claim before the PR is one opened once every step is green | 6 | 3 | 0 | 0 | 0 | 0 | 462 | 92 | 168 | 32455 | 4611011 | 312455 | 6.24 | 953 | unknown | 1/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 0 | 0 | 77 | 77 | 77 | 76 | 76 | 1 | 0 | 0 | 76 | 0 | 77 | 76 | 1 | 1 | 1 | 76 | 77 | 77 | 75 | 76 | 77 | 1 | 1 | 1 | 0 | 76 | 0 | 78 | 0 | 76 | 0 | 0 | 1 | 76 | 77 | 76 | 1 | 5 | 4 | 5 | 4 | 279 | 280 | 283 | 4 | 5 | 7 | 5 | 0 | 0 | 0 | 0 | 76 | 0 | 77 | 76 | 77 |
| fast | 2 | 3 | 3 | 3 | 2 | 2 | 3 | 2 | 3 | 2 | 2 | 2 | 2 | 3 | 3 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 0 | 0 | 0 | 5 | 5 | 4 | 5 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 771 | 1392 | 339300 | 41580971 | 2621297 | 55.49 |
