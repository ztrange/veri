### 📊 Metrics — issue 363

Wall time for the issue: 6351 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/398.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 10 | 5 | 0 | 0 | 752 | 688 | 132 | 230 | 50791 | 6118836 | 499860 | 9.33 |
| green | 12 | 5 | 1 | 0 | 2561 | 807 | 196 | 350 | 64442 | 9499012 | 592527 | 12.29 |
| refactor | 10 | 5 | 0 | 0 | 2236 | 949 | 146 | 286 | 68459 | 8066114 | 492279 | 10.67 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1083 | 4.34 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `classify-bail.sh step-too-big` prints `process` on stdout and exits 0 | 6 | 3 | 0 | 0 | 0 | 0 | 240 | 60 | 106 | 17888 | 2363454 | 233707 | 3.97 | 560 | unknown | 0/5 | nothing-left |
| The prompt `build-develop-prompt.sh green …` builds lets the leaf report one to three `SPLIT: <behaviour-level criterion>` lines instead of an implementation, changing no production code | 6 | 3 | 0 | 0 | 0 | 0 | 490 | 85 | 160 | 33168 | 4314297 | 307165 | 6.06 | 1394 | unknown | 1/5 | nothing-structural |
| The prompt `build-develop-prompt.sh revise green …` builds offers the same `SPLIT:` report | 6 | 3 | 0 | 0 | 0 | 0 | 413 | 93 | 168 | 31906 | 4451588 | 298022 | 6.00 | 1366 | unknown | 1/5 | structural-owed |
| SKILL.md's Green section, on `SPLIT:`, restores the tree to `HEAD`, adds the split steps before STEP in one `add-ledger-step.sh` call, commits the ledger, emits `step-split` and returns to `next-unchecked.sh` | 8 | 3 | 1 | 0 | 0 | 0 | 867 | 148 | 276 | 64698 | 8444989 | 439482 | 10.24 | 2043 | 1/2 | 5/5 | budget |
| SKILL.md bails with cause `step-too-big` when `add-ledger-step.sh` exits 1 on a split, and its Bailing section lists that cause as a process failure | 6 | 3 | 0 | 0 | 0 | 0 | 434 | 88 | 156 | 36032 | 4109634 | 306290 | 6.02 | 681 | unknown | 3/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 1 | 0 | 2 | 1 | 1 | 184 | 183 | 200 | 200 | 2 | 1 | 2 | 198 | 207 | 204 | 205 | 1 | 0 | 65 | 64 | 207 | 206 | 0 | 53 | 52 | 53 | 1 | 1 | 60 | 1 | 1 | 60 | 60 | 0 | 0 | 0 | 0 |
| fast | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 1 | 0 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 206 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 474 | 866 | 183692 | 23683962 | 1584666 | 32.29 |
