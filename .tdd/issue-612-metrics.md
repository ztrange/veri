### 📊 Metrics — issue 612

Wall time for the issue: 1981 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/632.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 14 | 2 | 4 | 1382 | 52549 | 36761 | 0.33 |
| red | 6 | 2 | 0 | 0 | 375 | 263 | 52 | 100 | 23917 | 2496513 | 276087 | 3.19 |
| pin | 2 | 2 | 0 | 0 | 88 | 41 | 8 | 16 | 3626 | 312471 | 78404 | 0.76 |
| green | 4 | 2 | 0 | 0 | 242 | 117 | 28 | 56 | 10679 | 1271608 | 166365 | 1.80 |
| refactor | 4 | 2 | 0 | 0 | 160 | 101 | 25 | 48 | 9631 | 1052602 | 161059 | 1.69 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| claude-md-guards-green.test.sh fails, naming the missing guard, when a planted `make -n test` roster lacks any one of the four CLAUDE.md guards ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 108 | 16 | 30 | 10332 | 812705 | 100104 | 1.17 | unknown | unknown | unknown | unknown |  |  | pin |
| claude-md-guards-green.test.sh fails when `make -n test` names no suite at all ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 13 | 26 | 5488 | 584566 | 82117 | 0.88 | unknown | unknown | unknown | unknown |  |  | pin |
| claude-md-guards-green.test.sh starts none of the four guard suites as a child process, and passes on a roster holding all four even when a guard itself would fail ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 200 | 45 | 90 | 17791 | 2110691 | 257110 | 2.84 | 419 | unknown | 2/5 | structural-owed |  |  | full |
| claude-md-guards-green.test.sh's header states that it pins the four guards' presence in `make test`'s roster and why the re-run was dropped, and states no cost in seconds ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 157 | 39 | 74 | 14242 | 1625232 | 242584 | 2.55 | 333 | unknown | 0/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| claude-md-guards-green.test.sh starts none of the four guard suites as a child process, and passes on a roster holding all four even when a guard itself would fail ⟦criterion 3⟧ | 1 | 2/5 | structural-owed | PASS | 0 | 97 | 0.93 |
| claude-md-guards-green.test.sh's header states that it pins the four guards' presence in `make test`'s roster and why the re-run was dropped, and states no cost in seconds ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 63 | 0.76 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | test-files-only |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 8 | 8 | 9 | 10 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| target | 8 | 8 | 9 | 9 | 0 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |
| fast | 16 | 17 | 15 | 16 | 18 | 16 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 115 | 224 | 49235 | 5185743 | 718676 | 7.77 |
