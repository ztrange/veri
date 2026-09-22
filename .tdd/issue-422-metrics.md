### 📊 Metrics — issue 422

Wall time for the issue: 18283 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 11 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/423.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 19 | 8 | 0 | 0 | 2781 | 2448 | 309 | 568 | 196362 | 18042442 | 1235765 | 26.29 |
| green | 20 | 9 | 1 | 0 | 7166 | 3267 | 386 | 732 | 214829 | 24218000 | 1288287 | 41.55 |
| refactor | 20 | 9 | 1 | 0 | 4771 | 2413 | 359 | 698 | 201061 | 22683328 | 1254846 | 28.92 |
| pin | 2 | 2 | 0 | 0 | 217 | 159 | 30 | 56 | 13072 | 1491325 | 106000 | 2.13 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1481 | 6.58 | 0 | 0.00 |
| refactor | 1927 | 4.85 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A guard names `<suite>:<line>` and fails the run when a suite that declares `pipefail` ends a pipeline in `grep -*q` ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 1311 | 158 | 292 | 106698 | 9967530 | 540838 | 13.06 | 3844 | 1/2 | 0/5 | malformed |
| The same guard also names a pipeline that ends in `head` ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 898 | 112 | 212 | 75170 | 7259583 | 413969 | 9.65 | 1115 | unknown | 5/5 | budget |
| The guard exempts a site listed in an exemption table carrying a reason per entry, and refuses an entry whose reason is missing ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 896 | 129 | 248 | 70700 | 8670327 | 428311 | 10.39 | 1415 | unknown | 4/5 | nothing-structural |
| A planted offender turns the guard red naming it, and the guard is green again once the plant is removed ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 189 | 35 | 66 | 15308 | 2125283 | 130412 | 2.75 | unknown | unknown | unknown | unknown |
| `prompt-test-tiers.test.sh`'s prompt probes give the same verdict on a matching and a non-matching prompt whether or not the writer is preempted ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 714 | 89 | 172 | 59836 | 4921564 | 346530 | 7.42 | 951 | unknown | 3/5 | structural-owed |
| `count-line-guard.test.sh`'s pipeline-fed matches give the same verdict on a matching and a non-matching input whether or not the writer is preempted ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 313 | 48 | 90 | 25470 | 2761950 | 120910 | 3.23 | unknown | unknown | unknown | unknown |
| Every remaining site the guard names is repaired or exempted, so the guard passes over the whole tree as it stands ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 1 | 0 | 1297 | 96 | 178 | 57763 | 6244954 | 366275 | 19.41 | 4612 | unknown | 4/5 | structural-owed |
| the guard names a site whose pipeline is split across lines — the `|` ending one line and the early-exiting reader opening the next — so a suite that declares `pipefail` cannot escape it by wrapping ⟦added⟧ ⟦criterion 4⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 1135 | 169 | 326 | 94646 | 10741989 | 552077 | 13.26 | 2286 | 1/2 | 3/5 | structural-owed |
| the guard's roster case says what it found when `make -n test` names no suite, instead of failing the run — so a tree that has no Makefile (every scratch plant `sigpipe-guard.test.sh` builds) gets the guard's real verdict ⟦added⟧ ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 569 | 86 | 162 | 41036 | 4921506 | 371250 | 7.20 | 800 | unknown | 3/5 | structural-owed |
| `CLAUDE.md`'s testing idiom section states the pipefail/SIGPIPE rule once ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 569 | 91 | 176 | 47562 | 5173797 | 346683 | 7.24 | 1085 | unknown | 3/5 | structural-owed |
| `no-nested-suites.test.sh` is green over the sigpipe guard's exemption table: a table key naming a suite and a line is not read as launching that suite ⟦added⟧ ⟦criterion 5⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 396 | 71 | 132 | 31135 | 3646612 | 267643 | 5.28 | 913 | unknown | 1/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 58 | 0 | 50 | 314 | 3 | 0 | 0 | 1 | 2 | 1 | 2 | 2 | 2 | 3 | 2 | 2 | 0 | 0 | 0 | 3 | 2 | 315 | 1 | 3 | 3 | 2 | 2 | 3 | 1 | 1 | 1 | 1 | 2 | 66 | 1 | 1 | 1 | 2 | 22 | 21 | 20 | 4 | 4 | 0 | 144 | 138 | 146 | 158 | 2 | 1 | 4 | 3 | 0 | 193 | 11 | 2 | 2 | 13 | 12 | 10 | 8 | 9 | 9 | 9 | 2 | 3 | 3 | 11 | 10 | 10 | 10 | 10 | 10 | 1 | 1 | 0 | 60 | 59 | 60 | 60 | 60 | 2 | 0 | 1 | 372 | 0 | 3 | 3 | 1 |
| fast | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 3 | 4 | 4 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 20 | 20 | 4 | 2 | 2 | 2 | 1 | 3 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 311 | 368 | 369 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 1084 | 2054 | 625324 | 66435095 | 3884898 | 98.89 |
