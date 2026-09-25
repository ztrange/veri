### 📊 Metrics — issue 389

Wall time for the issue: 9220 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 11 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/467.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 13 | 2 | 4 | 1492 | 56969 | 35339 | 0.32 |
| red | 22 | 11 | 0 | 0 | 1016 | 883 | 197 | 382 | 83950 | 9848170 | 1064479 | 12.17 |
| green | 24 | 11 | 1 | 0 | 5136 | 1106 | 280 | 550 | 101600 | 13449612 | 1096546 | 13.50 |
| refactor | 22 | 11 | 0 | 0 | 2132 | 813 | 196 | 390 | 76762 | 9613938 | 990871 | 11.39 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1137 | 2.23 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| SKILL.md's *Launching a leaf* runs `stop-requested.sh` before every leaf launch: exit 3 launches as normal, mode `at-ledger` launches the leaf anyway, and modes `at-leaf` and `now` launch nothing and go to *Stopping* ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 291 | 59 | 112 | 28796 | 2846206 | 283005 | 3.41 | 667 | unknown | 1/5 | nothing-structural |
| SKILL.md runs `stop-requested.sh` immediately after the atomic green commit's push and stops there on any mode ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 221 | 57 | 114 | 19409 | 2849617 | 276217 | 3.17 | 679 | unknown | 1/5 | nothing-structural |
| SKILL.md runs `stop-requested.sh` immediately after the refactor-pending clear's push, and after a pin's `test:` commit, and stops there on any mode ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 269 | 63 | 124 | 25174 | 3227774 | 297271 | 3.53 | 578 | unknown | 1/5 | structural-owed |
| SKILL.md treats `stop-requested.sh` exit 2 as a stop in mode `at-ledger`, narrating that the request was unreadable ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 227 | 48 | 96 | 18509 | 2202878 | 263019 | 2.92 | 621 | unknown | 0/5 | nothing-left |
| SKILL.md's three ledger-commit checkpoints (the green push, the refactor-pending clear, the pin's `test:` commit) send a `stop-requested.sh` exit 2 found there to *Stopping* as `at-ledger`, narrating that the request was unreadable ⟦added⟧ ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 243 | 58 | 116 | 23986 | 2826209 | 272931 | 3.23 | 848 | unknown | 2/5 | structural-owed |
| SKILL.md asks `stop-requested.sh` before reading a leaf's `wait-leaf.sh` exit 2 as `killed-stuck`, and a pending `now` sends the run to *Stopping* instead of *Bailing* ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 322 | 80 | 156 | 31054 | 4151075 | 298518 | 3.84 | 1208 | unknown | 3/5 | nothing-structural |
| each phase's own leaf-exit-2 branch in SKILL.md (develop-red, green, refactor, revise, verify-plan) points back to the checkpoints spelled once in *Launching a leaf* — ask `stop-requested.sh` before reading the exit 2 as `killed-stuck` ⟦added⟧ ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 290 | 65 | 130 | 27991 | 3404894 | 294372 | 3.60 | 956 | unknown | 2/5 | structural-owed |
| SKILL.md's *Bailing* keeps a bail condition reached first — a `REJECT` exhausting `REVISE_BUDGET`, or a killed-stuck leaf with no `now` pending — as a bail, and its bail comment says a stop was pending when one was | 6 | 3 | 0 | 0 | 0 | 0 | 235 | 58 | 114 | 22549 | 2796801 | 278919 | 3.24 | 722 | unknown | 1/5 | nothing-structural |
| SKILL.md's Draft PR step runs to completion with a stop request pending, clears it with `stop-requested.sh --clear`, and says in the final `### ✅ Done` comment that a stop arrived after the last step ⟦criterion 5⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 332 | 80 | 156 | 30938 | 3916856 | 377905 | 4.43 | 1521 | 1/2 | 1/5 | nothing-structural |
| SKILL.md checkpoints the repair step a red full run appends at the Draft PR step like any other step — both checkpoints apply to it ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 179 | 54 | 102 | 16631 | 2344389 | 256184 | 2.85 | 532 | unknown | 0/5 | nothing-left |
| SKILL.md's step 1.2 runs `stop-requested.sh --clear` beside the `.tdd/conductor.pid` write, so a stale request from a killed run cannot stop the run that resumes it ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 193 | 51 | 102 | 17275 | 2345021 | 253555 | 2.84 | 457 | unknown | 1/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 0 | 9 | 69 | 0 | 88 | 90 | 0 | 1 | 0 | 0 | 87 | 88 | 1 | 1 | 0 | 0 | 0 | 0 | 88 | 0 | 88 | 0 | 0 | 1 | 1 | 1 | 0 | 88 | 2 | 88 | 0 | 88 | 0 | 1 | 0 | 88 | 88 | 88 | 1 | 1 | 1 | 0 | 1 | 0 | 72 | 88 | 89 | 89 | 89 | 0 | 0 | 0 | 8 | 89 | 1 | 0 | 0 | 88 | 90 | 88 | 88 | 88 | 1 | 1 | 1 | 1 | 1 | 0 | 71 | 0 | 89 | 88 | 1 | 1 | 1 | 0 | 88 | 88 | 22 | 22 | 9 | 73 | 89 | 89 | 1 | 1 | 1 | 1 | 0 | 9 | 74 | 93 | 0 | 91 | 1 | 1 | 0 | 75 | 92 | 1 | 1 |
| fast | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| probe | 23 | 23 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 294 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 675 | 1326 | 263804 | 32968689 | 3187235 | 37.37 |
