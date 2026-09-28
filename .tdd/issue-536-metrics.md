### 📊 Metrics — issue 536

Wall time for the issue: 730 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/547.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 6 | 1 | 2 | 570 | 11207 | 34958 | 0.29 |
| red | 5 | 2 | 0 | 0 | 202 | 168 | 33 | 64 | 15528 | 1552418 | 240431 | 2.54 |
| green | 6 | 2 | 1 | 0 | 1128 | 238 | 57 | 114 | 23315 | 2741058 | 224791 | 2.81 |
| refactor | 4 | 2 | 0 | 0 | 213 | 150 | 37 | 74 | 14254 | 1826345 | 177476 | 2.07 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 41 | 0.50 |
| green | 1033 | 1.91 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| develop-red | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A shell that set an EXIT trap before calling `bg_start` still runs that earlier trap at exit, and still gets the survivor report for a process left running ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 319 | 72 | 144 | 30604 | 3498524 | 317847 | 3.86 | 1328 | 1/2 | 1/5 | structural-owed |  |  | full |
| A shell that set an EXIT trap and then calls `bg_start` more than once, with the same record and with a second record, reports each survivor exactly once and runs its own earlier trap exactly once ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 207 | 51 | 100 | 19766 | 2447213 | 274005 | 3.08 | 363 | unknown | 1/5 | structural-owed |  |  | full |
| Running `workqueue.test.sh` leaves no scratch directory of its own behind in `$TMPDIR` ⟦criterion 3⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 30 | 4 | 8 | 2727 | 174084 | 50846 | 0.50 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A shell that set an EXIT trap before calling `bg_start` still runs that earlier trap at exit, and still gets the survivor report for a process left running ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 111 | 1.01 |
| A shell that set an EXIT trap and then calls `bg_start` more than once, with the same record and with a second record, reports each survivor exactly once and runs its own earlier trap exactly once ⟦criterion 2⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 102 | 1.06 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 18 | 0 | 1 | 0 | 1 | 7 | 8 | 1 | 7 | 7 | 1 | 0 | 1 | 7 | 8 | 0 | 0 | 0 | 7 | 1 | 0 |
| fast | 7 | 7 | 7 | 8 | 7 | 7 | 6 | 6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 613 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 128 | 254 | 53667 | 6131028 | 677656 | 7.72 |
