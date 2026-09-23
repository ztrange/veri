### 📊 Metrics — issue 431

Wall time for the issue: 8278 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/436.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 9 | 4 | 1 | 0 | 1554 | 1412 | 155 | 284 | 109338 | 9893915 | 607639 | 13.76 |
| green | 10 | 4 | 1 | 0 | 3477 | 1541 | 234 | 428 | 100797 | 14057241 | 679156 | 16.34 |
| refactor | 10 | 4 | 1 | 0 | 2253 | 1376 | 209 | 400 | 101809 | 12845900 | 598148 | 14.95 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 340 | 3.33 |
| green | 1814 | 6.86 | 475 | 2.83 |
| refactor | 0 | 0.00 | 1124 | 5.29 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A step title containing an apostrophe reaches a leaf intact through the documented launch mechanism, with no hand-written wrapper | 6 | 3 | 0 | 0 | 0 | 0 | 1130 | 149 | 274 | 84366 | 9681753 | 425004 | 11.20 | 1771 | unknown | 3/5 | structural-owed |
| SKILL.md states the step-title rule in one place and every documented launch line follows it | 8 | 3 | 1 | 0 | 0 | 0 | 1238 | 167 | 316 | 85801 | 11024812 | 575608 | 13.42 | 2794 | 1/2 | 3/5 | structural-owed |
| Every documented command line carrying text taken from the step's title follows the step-title rule — including the four lines that pass a fragment of it, tick-ledger.sh and clear-refactor-pending.sh and tick-issue-criterion.sh — and a test fails the run naming a line that single-quotes one | 8 | 3 | 1 | 0 | 0 | 0 | 994 | 155 | 286 | 77760 | 8573773 | 455266 | 10.78 | unknown | 1/2 | 1/5 | structural-owed |
| The guard fails naming file and line when a SKILL.md launch line inlines an unescaped step title, against an exemption table carrying a reason per entry | 6 | 3 | 0 | 0 | 0 | 0 | 918 | 117 | 222 | 60528 | 7206449 | 387058 | 8.99 | 1180 | unknown | 5/5 | budget |
| A background process is killed by the pid recorded when it started, never by that shell's own job spec | 1 | 0 | 1 | 0 | 0 | 0 | 49 | 10 | 14 | 3489 | 310269 | 42007 | 0.66 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 13 | 13 | 58 | 74 | 13 | 12 | 12 | 13 | 13 | 0 | 0 | 81 | 0 | 73 | 70 | 1 | 0 | 79 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 77 | 80 | 76 | 80 | 77 | 78 | 1 | 0 | 2 | 3 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 1 |
| fast | 3 | 2 | 2 | 3 | 2 | 3 | 2 | 2 | 4 | 2 | 2 | 3 | 3 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 12 | 0 | 0 | 1 | 0 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 256 | 254 | 256 | 280 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 598 | 1112 | 311944 | 36797056 | 1884943 | 45.05 |
