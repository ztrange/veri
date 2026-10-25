### 📊 Metrics — issue 2381

Wall time for the issue: 980 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2384.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.44 over 30 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 93110 tokens, largest 118725 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.61 | 93110 |
| 2 | $0.03 | 94231 |
| 3 | $0.03 | 96051 |
| 4 | $0.02 | 96357 |
| 5 | $0.02 | 96696 |
| 6 | $0.02 | 96992 |
| 7 | $0.02 | 97285 |
| 8 | $0.02 | 97849 |
| 9 | $0.02 | 98264 |
| 10 | $0.05 | 101635 |
| 11 | $0.03 | 102602 |
| 12 | $0.03 | 103211 |
| 13 | $0.03 | 103756 |
| 14 | $0.03 | 104479 |
| 15 | $0.03 | 105849 |
| 16 | $0.03 | 106620 |
| 17 | $0.05 | 109711 |
| 18 | $0.03 | 111278 |
| 19 | $0.03 | 112021 |
| 20 | $0.03 | 112997 |
| 21 | $0.03 | 113720 |
| 22 | $0.03 | 114537 |
| 23 | $0.03 | 115275 |
| 24 | $0.03 | 115966 |
| 25 | $0.03 | 116309 |
| 26 | $0.03 | 117302 |
| 27 | $0.03 | 117733 |
| 28 | $0.03 | 117996 |
| 29 | $0.03 | 118320 |
| 30 | $0.03 | 118725 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 14 | 4 | 8 | 1237 | 93334 | 32563 | 0.10 |
| red | 2 | 1 | 0 | 0 | 67 | 43 | 8 | 16 | 4753 | 204709 | 54605 | 0.20 |
| green | 2 | 1 | 0 | 0 | 145 | 24 | 10 | 20 | 2555 | 287454 | 31727 | 0.13 |
| refactor | 1 | 0 | 0 | 0 | 7 | 3 | 2 | 4 | 152 | 47822 | 12840 | 0.04 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 130 | 40 | 12 | 24 | 3922 | 308837 | 64295 | 0.23 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 108 | 44 | 12 | 24 | 4775 | 324482 | 67440 | 0.25 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A merge-lock.sh taker waiting on a held lock exits 0 holding the lock once the holder releases, however long the holder waited before releasing and even when the release removes the lock while the waiter is reading its holder record: pinned by a delayed-release two-takers race case in skills/tdd/scripts/tests/py/test_merge_lock_process.py (a process case, a real merge-lock.sh shim), whose outcome does not depend on machine load ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 70 | 20 | 40 | 7460 | 539985 | 99172 | 0.38 | 331 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A merge-lock.sh taker waiting on a held lock exits 0 holding the lock once the holder releases, however long the holder waited before releasing and even when the release removes the lock while the waiter is reading its holder record: pinned by a delayed-release two-takers race case in skills/tdd/scripts/tests/py/test_merge_lock_process.py (a process case, a real merge-lock.sh shim), whose outcome does not depend on machine load ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 9 | 8 | 9 | 17 |
| fast | 26 | 45 |  |  |
| target | 3 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 24 | 48 | 8697 | 633319 | 131735 | 0.48 |
