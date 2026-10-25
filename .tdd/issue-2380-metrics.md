### 📊 Metrics — issue 2380

Wall time for the issue: 3811 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2383.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.55 over 81 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 92796 tokens, largest 180541 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.60 | 92796 |
| 2 | $0.03 | 93891 |
| 3 | $0.07 | 99732 |
| 4 | $0.03 | 100458 |
| 5 | $0.02 | 100884 |
| 6 | $0.02 | 101254 |
| 7 | $0.02 | 101613 |
| 8 | $0.02 | 101914 |
| 9 | $0.02 | 102400 |
| 10 | $0.02 | 102748 |
| 11 | $0.03 | 103310 |
| 12 | $0.03 | 103952 |
| 13 | $0.03 | 104693 |
| 14 | $0.03 | 105639 |
| 15 | $0.04 | 107864 |
| 16 | $0.03 | 109095 |
| 17 | $0.03 | 110037 |
| 18 | $0.03 | 110597 |
| 19 | $0.03 | 111131 |
| 20 | $0.03 | 111713 |
| 21 | $0.03 | 113111 |
| 22 | $0.03 | 114124 |
| 23 | $0.04 | 115900 |
| 24 | $0.04 | 117675 |
| 25 | $0.03 | 118523 |
| 26 | $0.03 | 119198 |
| 27 | $0.04 | 121278 |
| 28 | $0.03 | 121933 |
| 29 | $0.05 | 125238 |
| 30 | $0.03 | 125696 |
| 31 | $0.03 | 126003 |
| 32 | $0.03 | 127116 |
| 33 | $0.03 | 128007 |
| 34 | $0.03 | 128783 |
| 35 | $0.04 | 130354 |
| 36 | $0.03 | 131456 |
| 37 | $0.05 | 134192 |
| 38 | $0.04 | 135473 |
| 39 | $0.04 | 136631 |
| 40 | $0.06 | 140796 |
| 41 | $0.04 | 141804 |
| 42 | $0.04 | 142737 |
| 43 | $0.04 | 143725 |
| 44 | $0.04 | 145592 |
| 45 | $0.04 | 146444 |
| 46 | $0.04 | 148300 |
| 47 | $0.05 | 150531 |
| 48 | $0.04 | 151784 |
| 49 | $0.04 | 152446 |
| 50 | $0.04 | 153288 |
| 51 | $0.04 | 154441 |
| 52 | $0.04 | 155530 |
| 53 | $0.04 | 156287 |
| 54 | $0.03 | 156651 |
| 55 | $0.04 | 157619 |
| 56 | $0.04 | 158100 |
| 57 | $0.04 | 158926 |
| 58 | $0.04 | 159695 |
| 59 | $0.04 | 160511 |
| 60 | $0.04 | 161447 |
| 61 | $0.04 | 162081 |
| 62 | $0.04 | 162877 |
| 63 | $0.04 | 164000 |
| 64 | $0.04 | 164484 |
| 65 | $0.04 | 165605 |
| 66 | $0.04 | 166720 |
| 67 | $0.06 | 170124 |
| 68 | $0.04 | 171025 |
| 69 | $0.04 | 171415 |
| 70 | $0.04 | 172049 |
| 71 | $0.04 | 172553 |
| 72 | $0.04 | 173143 |
| 73 | $0.05 | 175491 |
| 74 | $0.05 | 176826 |
| 75 | $0.04 | 177416 |
| 76 | $0.04 | 177870 |
| 77 | $0.04 | 178646 |
| 78 | $0.04 | 179034 |
| 79 | $0.04 | 179671 |
| 80 | $0.04 | 179986 |
| 81 | $0.04 | 180541 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 12 | 1 | 2 | 840 | 0 | 30686 | 0.09 |
| red | 8 | 3 | 1 | 0 | 289 | 146 | 38 | 76 | 15220 | 1091673 | 185065 | 0.86 |
| green | 8 | 2 | 1 | 0 | 960 | 228 | 58 | 116 | 18755 | 1859552 | 176076 | 1.04 |
| red-contradicted | 1 | 0 | 0 | 0 | 80 | 43 | 8 | 16 | 3485 | 269826 | 22993 | 0.12 |
| pin | 2 | 1 | 1 | 0 | 78 | 28 | 8 | 16 | 2988 | 213563 | 30494 | 0.13 |
| refactor | 2 | 0 | 0 | 0 | 16 | 10 | 5 | 10 | 585 | 108586 | 46789 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 7 | 3 | 0 | 503 | 141 | 38 | 76 | 12179 | 1000878 | 176382 | 0.66 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 622 | 210 | 48 | 96 | 18561 | 1565009 | 184027 | 1.16 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 316 | 116 | 32 | 64 | 11133 | 977313 | 131694 | 0.54 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 161 | 0.60 | 0 | 0.00 |
| green | 678 | 0.79 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 0 | 0.00 |
| pin | 22 | 0.06 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A supervised leaf whose full `make test` waits on a held full-suite lock for longer than `VERI_TIMEOUT` (shrunk for the test), then runs a short suite, finishes with its own exit code and is not killed stuck (a medium case driving supervise.sh over a stub leaf at the process boundary, the lock held by the test) ⟦criterion 1⟧ | 14 | 3 | 3 | 0 | 0 | 0 | 354 | 84 | 168 | 30333 | 2576693 | 339004 | 1.77 | 1371 | red 1/2, green 2/2 | 0/5 | nothing-left |  |  | full |
| A supervised leaf whose full `make test` waits silently on a held full-suite lock for longer than the `VERI_HEARTBEAT` silence window (shrunk for the test) is not killed for silence, and finishes with its own exit code (a medium case at the process boundary, the lock held by the test) | 5 | 2 | 0 | 0 | 0 | 0 | 65 | 23 | 46 | 6208 | 666485 | 84262 | 0.34 | 382 | unknown | 0/5 | nothing-left |  |  | full |
| A supervised leaf that hangs after acquiring the full-suite lock is still killed stuck once `VERI_TIMEOUT` has elapsed counted from the acquisition, not from the leaf's start (a medium case at the process boundary, the lock held by the test and then released) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 10 | 20 | 4492 | 300022 | 38151 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A supervised leaf whose full `make test` waits on a held full-suite lock for longer than `VERI_TIMEOUT` (shrunk for the test), then runs a short suite, finishes with its own exit code and is not killed stuck (a medium case driving supervise.sh over a stub leaf at the process boundary, the lock held by the test) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.08 |
| A supervised leaf whose full `make test` waits silently on a held full-suite lock for longer than the `VERI_HEARTBEAT` silence window (shrunk for the test) is not killed for silence, and finishes with its own exit code (a medium case at the process boundary, the lock held by the test) | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 8 | 7 | 17 | 9 | 7 | 11 | 48 | 57 | 53 | 15 | 14 | 8 | 15 | 30 | 31 | 8 |
| fast | 28 | 31 | 67 | 27 | 28 | 32 | 45 | 24 |  |  |  |  |  |  |  |  |
| target | 4 | 5 | 8 | 12 | 6 | 33 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 118 | 236 | 41873 | 3543200 | 492103 | 2.36 |
