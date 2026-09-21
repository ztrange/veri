### 📊 Metrics — issue 387

Wall time for the issue: 9588 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 11 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/410.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 19 | 8 | 0 | 0 | 2308 | 1465 | 216 | 382 | 111702 | 10245261 | 1004316 | 17.96 |
| green | 20 | 8 | 2 | 0 | 2889 | 1225 | 260 | 458 | 91127 | 11850456 | 973184 | 17.94 |
| refactor | 18 | 8 | 1 | 0 | 2952 | 1914 | 282 | 532 | 147165 | 15494803 | 985341 | 21.28 |
| pin | 3 | 3 | 0 | 0 | 120 | 96 | 28 | 50 | 7412 | 1194779 | 134487 | 2.13 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1741 | 6.86 | 0 | 0.00 |
| refactor | 1235 | 4.96 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| an unknown --mode value, both an issue and --all, neither, and a non-integer issue each exit 2, write no .tdd/stop and signal nothing | 8 | 3 | 1 | 0 | 0 | 0 | 688 | 108 | 192 | 54038 | 5012026 | 396290 | 7.82 | 2389 | 1/2 | 2/5 | structural-owed |
| stop-run.sh --mode with no value following it prints a named complaint on stderr and exits 2, instead of dying on an unbound $2 with exit 1 | 6 | 3 | 0 | 0 | 0 | 0 | 343 | 70 | 124 | 25240 | 3084334 | 273444 | 4.91 | 473 | unknown | 2/5 | nothing-structural |
| stop-run.sh --mode now <n> writes `now` as the only line of that run's .tdd/stop, names the run on stdout and exits 0 | 8 | 3 | 1 | 0 | 0 | 0 | 561 | 104 | 186 | 43074 | 4886206 | 397322 | 7.49 | 1197 | 1/2 | 2/5 | nothing-structural |
| stop-run.sh <n> with no --mode writes at-ledger | 2 | 1 | 0 | 0 | 0 | 0 | 84 | 20 | 36 | 7016 | 915753 | 92880 | 1.56 | unknown | unknown | unknown | unknown |
| a second call for the same run overwrites the mode already in .tdd/stop | 2 | 1 | 0 | 0 | 0 | 0 | 85 | 20 | 38 | 6712 | 955727 | 92458 | 1.57 | unknown | unknown | unknown | unknown |
| stop-run.sh --all writes the mode into every live run's .tdd/stop and into no other | 6 | 3 | 0 | 0 | 0 | 0 | 584 | 85 | 152 | 41706 | 4235197 | 321220 | 6.37 | 954 | unknown | 3/5 | nothing-structural |
| an issue with no worktree, an issue whose .tdd/conductor.pid names no live process, and --all with no live run each exit 3 and write no .tdd/stop | 6 | 3 | 0 | 0 | 0 | 0 | 466 | 77 | 136 | 35332 | 3840999 | 326062 | 6.07 | 602 | unknown | 3/5 | structural-owed |
| no main working tree to resolve exits 2 and writes nothing | 6 | 3 | 0 | 0 | 0 | 0 | 375 | 79 | 144 | 29572 | 3925314 | 307264 | 5.78 | 506 | unknown | 3/5 | nothing-structural |
| stop-run.sh --mode now <n> sends TERM to the pid in <run>/.tdd/<name>.pid whose process runs `supervise.sh <name> `, and to no pid whose process is gone or runs something else | 6 | 3 | 0 | 0 | 0 | 0 | 670 | 88 | 158 | 49658 | 4698865 | 348693 | 7.08 | 822 | unknown | 5/5 | budget |
| stop-run.sh --mode at-ledger <n> and --mode at-leaf <n> signal nothing | 2 | 1 | 0 | 0 | 0 | 0 | 138 | 22 | 42 | 8478 | 1154992 | 108478 | 1.87 | unknown | unknown | unknown | unknown |
| stop-run.sh never signals the pid in .tdd/conductor.pid | 8 | 3 | 1 | 0 | 0 | 0 | 706 | 113 | 214 | 56580 | 6075886 | 433217 | 8.79 | 1734 | 1/2 | 0/5 | nothing-left |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 232 | 0 | 3 | 1 | 41 | 41 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 240 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 240 | 0 | 1 | 1 | 1 | 0 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 4 | 3 | 3 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 2 | 49 | 2 | 2 | 1 | 2 | 2 | 2 | 241 | 2 |
| fast | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 3 | 3 | 3 | 2 | 2 | 2 | 3 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 232 | 232 | 233 | 239 | 242 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 786 | 1422 | 357406 | 38785299 | 3097328 | 59.31 |
