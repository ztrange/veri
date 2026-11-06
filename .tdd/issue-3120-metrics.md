### 📊 Metrics — issue 3120

Wall time for the issue: 11534 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3137.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.84 over 68 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 91914 tokens, largest 153582 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.60 | 91914 |
| 2 | $0.08 | 99248 |
| 3 | $0.03 | 100553 |
| 4 | $0.04 | 102485 |
| 5 | $0.02 | 102917 |
| 6 | $0.02 | 103281 |
| 7 | $0.02 | 103651 |
| 8 | $0.02 | 104111 |
| 9 | $0.02 | 104421 |
| 10 | $0.02 | 104723 |
| 11 | $0.02 | 105025 |
| 12 | $0.03 | 105543 |
| 13 | $0.02 | 106008 |
| 14 | $0.02 | 106452 |
| 15 | $0.02 | 106856 |
| 16 | $0.03 | 107664 |
| 17 | $0.03 | 108263 |
| 18 | $0.05 | 111189 |
| 19 | $0.04 | 113001 |
| 20 | $0.03 | 113355 |
| 21 | $0.03 | 114043 |
| 22 | $0.03 | 114585 |
| 23 | $0.03 | 115269 |
| 24 | $0.03 | 115722 |
| 25 | $0.03 | 116872 |
| 26 | $0.03 | 118186 |
| 27 | $0.04 | 119973 |
| 28 | $0.03 | 120661 |
| 29 | $0.03 | 121401 |
| 30 | $0.03 | 122071 |
| 31 | $0.03 | 123079 |
| 32 | $0.03 | 124209 |
| 33 | $0.03 | 125077 |
| 34 | $0.03 | 126276 |
| 35 | $0.05 | 129362 |
| 36 | $0.03 | 130356 |
| 37 | $0.06 | 135146 |
| 38 | $0.05 | 137689 |
| 39 | $0.03 | 137936 |
| 40 | $0.03 | 138298 |
| 41 | $0.03 | 139130 |
| 42 | $0.03 | 139803 |
| 43 | $0.04 | 140838 |
| 44 | $0.04 | 141953 |
| 45 | $0.04 | 142850 |
| 46 | $0.03 | 143446 |
| 47 | $0.03 | 144099 |
| 48 | $0.03 | 144824 |
| 49 | $0.03 | 145163 |
| 50 | $0.03 | 145892 |
| 51 | $0.03 | 146540 |
| 52 | $0.04 | 147328 |
| 53 | $0.03 | 147690 |
| 54 | $0.03 | 148021 |
| 55 | $0.03 | 148352 |
| 56 | $0.03 | 148683 |
| 57 | $0.03 | 149000 |
| 58 | $0.03 | 149293 |
| 59 | $0.03 | 149700 |
| 60 | $0.03 | 150273 |
| 61 | $0.04 | 151186 |
| 62 | $0.03 | 151522 |
| 63 | $0.03 | 151821 |
| 64 | $0.03 | 152119 |
| 65 | $0.03 | 152515 |
| 66 | $0.03 | 152847 |
| 67 | $0.03 | 153246 |
| 68 | $0.03 | 153582 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 5 | 1 | 2 | 515 | 0 | 31644 | 0.08 |
| red | 2 | 1 | 0 | 0 | 299 | 48 | 11 | 20 | 4533 | 304720 | 61163 | 0.23 |
| green | 4 | 1 | 1 | 0 | 1273 | 103 | 26 | 52 | 8044 | 773486 | 107575 | 0.58 |
| red-missing | 1 | 0 | 0 | 0 | 59 | 28 | 4 | 8 | 3382 | 101021 | 36515 | 0.14 |
| pin | 1 | 0 | 1 | 0 | 65 | 21 | 4 | 8 | 1701 | 113458 | 17061 | 0.07 |
| refactor | 1 | 0 | 0 | 0 | 7 | 3 | 2 | 4 | 147 | 30975 | 31725 | 0.08 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 3 | 2 | 0 | 943 | 85 | 19 | 36 | 6193 | 469557 | 116579 | 0.40 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 219 | 65 | 13 | 26 | 6949 | 358123 | 113199 | 0.39 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 553 | 58 | 16 | 32 | 5180 | 495980 | 55905 | 0.40 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1273 | 0.58 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 65 | 0.07 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| On the supersede-diff route (verify's `diff` phase run with `--supersede-base <git stash create snapshot>`), a pytest case an earlier step added that the uncommitted working-tree edits delete — still present in HEAD — is reported by `deleted_cases` (the working tree compared with that snapshot), so verify exits 1 naming it as a deleted case, the same as a committed deletion ⟦criterion 1⟧ | 9 | 2 | 2 | 0 | 0 | 0 | 203 | 47 | 92 | 17807 | 1323660 | 254039 | 1.10 | 2106 | 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| On the supersede-diff route (verify's `diff` phase run with `--supersede-base <git stash create snapshot>`), a pytest case an earlier step added that the uncommitted working-tree edits delete — still present in HEAD — is reported by `deleted_cases` (the working tree compared with that snapshot), so verify exits 1 naming it as a deleted case, the same as a committed deletion ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.08 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 108 | 19 | 61 | 59 | 0 | 12 | 84 | 57 |  |  |  |  |  |  |  |  |
| fast | 71 | 71 | 108 | 65 |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 8 | 12 | 12 | 9 | 5 | 6 | 5 | 6 | 6 | 6 | 6 | 6 | 6 | 8 | 6 | 7 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 48 | 94 | 18322 | 1323660 | 285683 | 4.02 (estimate) |
