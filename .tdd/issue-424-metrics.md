### 📊 Metrics — issue 424

Wall time for the issue: 8156 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/425.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 12 | 4 | 1 | 0 | 3183 | 1368 | 176 | 316 | 106272 | 9440799 | 710908 | 14.49 |
| green | 12 | 4 | 2 | 0 | 3073 | 1305 | 199 | 378 | 98900 | 10937017 | 663151 | 14.57 |
| refactor | 8 | 4 | 0 | 0 | 1091 | 833 | 122 | 236 | 65720 | 6876840 | 430004 | 9.38 |
| pin | 1 | 1 | 0 | 0 | 84 | 71 | 12 | 20 | 5361 | 562030 | 54489 | 0.96 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 1540 | 4.53 | 0 | 0.00 |
| green | 1981 | 8.11 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A background process a veri script or test starts is killed by its recorded PID, never by a job spec, so it dies whether or not the starting shell is still alive | 11 | 3 | 2 | 0 | 0 | 0 | 980 | 140 | 268 | 73386 | 7084915 | 560203 | 10.98 | 3405 | 3/2 | 2/5 | structural-owed |
| A background process that is still running when its starting shell exits is reported, naming its PID and what started it, rather than being left silently | 8 | 3 | 1 | 0 | 0 | 0 | 903 | 128 | 238 | 67493 | 6846240 | 430840 | 9.42 | 1885 | 1/2 | 5/5 | budget |
| A guard names `<file>:<line>` and fails the run when a file under `skills/` kills a background process by job spec (`kill %…`), with an exemption table carrying a reason per entry | 6 | 3 | 0 | 0 | 0 | 0 | 921 | 117 | 222 | 74277 | 7234012 | 400876 | 9.48 | 1392 | unknown | 3/5 | structural-owed |
| A planted offender turns that guard red naming it, and the guard is green again once the plant is removed | 2 | 1 | 0 | 0 | 0 | 0 | 262 | 33 | 62 | 19818 | 2075969 | 131832 | 2.85 | unknown | unknown | unknown | unknown |
| The rule is stated once in `CLAUDE.md`, next to the existing note that a killed process's cleanup never runs | 6 | 3 | 0 | 0 | 0 | 0 | 511 | 91 | 160 | 41279 | 4575550 | 334801 | 6.67 | 862 | unknown | 1/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 5 | 5 | 57 | 0 | 77 | 76 | 53 | 0 | 53 | 54 | 0 | 0 | 53 | 0 | 0 | 0 | 52 | 46 | 54 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 6 | 74 | 75 | 2 | 46 | 53 | 1 | 6 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 53 | 47 | 55 | 53 | 1 |
| all | 247 | 247 | 246 | 243 | 247 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 509 | 950 | 276253 | 27816686 | 1858552 | 39.40 |
