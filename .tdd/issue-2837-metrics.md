### 📊 Metrics — issue 2837

Wall time for the issue: 1216 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 1 of 4 planned.
Outcome: the run bailed — needs-user, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.78 over 25 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87691 tokens, largest 163788 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87691 |
| 2 | $0.09 | 96746 |
| 3 | $0.04 | 98863 |
| 4 | $0.02 | 99379 |
| 5 | $0.02 | 99748 |
| 6 | $0.02 | 100125 |
| 7 | $0.02 | 100445 |
| 8 | $0.06 | 105532 |
| 9 | $0.05 | 109104 |
| 10 | $0.14 | 124408 |
| 11 | $0.03 | 125262 |
| 12 | $0.03 | 125502 |
| 13 | $0.04 | 127450 |
| 14 | $0.03 | 128333 |
| 15 | $0.04 | 130619 |
| 16 | $0.03 | 131404 |
| 17 | $0.11 | 141636 |
| 18 | $0.05 | 144530 |
| 19 | $0.07 | 149116 |
| 20 | $0.06 | 152439 |
| 21 | $0.04 | 153308 |
| 22 | $0.05 | 155206 |
| 23 | $0.04 | 156376 |
| 24 | $0.05 | 158247 |
| 25 | $0.08 | 163788 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 959 | 0 | 33651 | 0.09 |
| red | 3 | 1 | 0 | 0 | 234 | 66 | 19 | 38 | 8167 | 681509 | 94543 | 0.39 |
| pin | 2 | 2 | 0 | 0 | 59 | 27 | 8 | 16 | 2676 | 227680 | 34938 | 0.14 |
| green | 4 | 0 | 2 | 0 | 510 | 71 | 22 | 40 | 7409 | 619090 | 75126 | 0.32 |
| red-missing | 1 | 0 | 0 | 0 | 46 | 33 | 8 | 16 | 3858 | 280450 | 23961 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 4 | 2 | 0 | 472 | 88 | 23 | 44 | 8623 | 607158 | 122877 | 0.45 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 389 | 118 | 35 | 68 | 14446 | 1201571 | 139342 | 0.61 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 192 | 0.23 |
| pin | 0 | 0.00 | 28 | 0.07 |
| green | 0 | 0.00 | 510 | 0.32 |
| red-missing | 0 | 0.00 | 46 | 0.13 |
| verify-green | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| After a refactor deletes a frozen Go case's `t.Fatal` line without moving it anywhere, `rerecord-refactored` leaves the record and `check-earlier` for a later step still exits 1 naming the case: the weakening guard of #2626 holds, and with the guard removed this case goes red (a pin in skills/tdd/scripts/tests/py/test_tests_frozen_process.py: a git repo in tmp_path, a medium case marked process, no production change) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 10 | 20 | 4065 | 311311 | 61736 | 0.23 | unknown | unknown | unknown | unknown |  |  | pin |
| After a refactor moves a frozen Go case's `t.Fatal` lines into a helper that the case calls, `rerecord-refactored` rewrites the case's record and `check-earlier` for a later step exits 0 (in skills/tdd/scripts/tests/py/test_tests_frozen_process.py: a git repo in tmp_path, a medium case marked process) ⟦criterion 1⟧ | 8 | 2 | 2 | 0 | 0 | 0 | 165 | 47 | 90 | 18045 | 1497418 | 166832 | 0.75 | unknown | unknown | unknown | unknown |  |  | already-satisfied |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 8 | 27 | 33 | 28 | 19 | 24 | 22 | 9 |
| target | 6 | 7 | 3 | 4 | 24 |  |  |  |  |
| fast | 32 | 31 | 36 | 39 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 58 | 112 | 23069 | 1808729 | 262219 | 2.84 (estimate) |
