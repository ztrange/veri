### 📊 Metrics — issue 2927

Wall time for the issue: 3500 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3028.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $7.27 over 129 turns, in 3 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90173 tokens, largest 172007 tokens
Conductor context: first turn 90194 tokens, largest 135247 tokens
Conductor context: first turn 90188 tokens, largest 155623 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 90173 |
| 2 | $0.08 | 97156 |
| 3 | $0.04 | 98742 |
| 4 | $0.05 | 100302 |
| 5 | $0.03 | 100574 |
| 6 | $0.03 | 101261 |
| 7 | $0.03 | 101587 |
| 8 | $0.04 | 101873 |
| 9 | $0.03 | 102129 |
| 10 | $0.03 | 102719 |
| 11 | $0.04 | 104138 |
| 12 | $0.05 | 106099 |
| 13 | $0.09 | 113925 |
| 14 | $0.05 | 115389 |
| 15 | $0.03 | 115733 |
| 16 | $0.04 | 116502 |
| 17 | $0.04 | 117031 |
| 18 | $0.03 | 117515 |
| 19 | $0.04 | 118019 |
| 20 | $0.03 | 118204 |
| 21 | $0.04 | 118430 |
| 22 | $0.03 | 119047 |
| 23 | $0.05 | 120383 |
| 24 | $0.03 | 120730 |
| 25 | $0.04 | 121016 |
| 26 | $0.04 | 121817 |
| 27 | $0.04 | 122665 |
| 28 | $0.05 | 124327 |
| 29 | $0.04 | 124930 |
| 30 | $0.08 | 131198 |
| 31 | $0.04 | 131535 |
| 32 | $0.04 | 132063 |
| 33 | $0.04 | 132465 |
| 34 | $0.04 | 132998 |
| 35 | $0.04 | 133627 |
| 36 | $0.05 | 135122 |
| 37 | $0.04 | 136397 |
| 38 | $0.04 | 137170 |
| 39 | $0.05 | 137706 |
| 40 | $0.04 | 138507 |
| 41 | $0.04 | 139270 |
| 42 | $0.06 | 142176 |
| 43 | $0.05 | 142961 |
| 44 | $0.04 | 143405 |
| 45 | $0.04 | 144246 |
| 46 | $0.05 | 145131 |
| 47 | $0.04 | 145615 |
| 48 | $0.04 | 146584 |
| 49 | $0.05 | 147237 |
| 50 | $0.04 | 148236 |
| 51 | $0.05 | 148965 |
| 52 | $0.04 | 149799 |
| 53 | $0.05 | 150095 |
| 54 | $0.04 | 150771 |
| 55 | $0.04 | 151073 |
| 56 | $0.05 | 151631 |
| 57 | $0.06 | 154406 |
| 58 | $0.10 | 162749 |
| 59 | $0.06 | 164027 |
| 60 | $0.05 | 165356 |
| 61 | $0.08 | 169948 |
| 62 | $0.05 | 170777 |
| 63 | $0.05 | 172007 |
| 64 | $0.59 | 90194 |
| 65 | $0.08 | 97177 |
| 66 | $0.05 | 98751 |
| 67 | $0.04 | 100580 |
| 68 | $0.03 | 101121 |
| 69 | $0.08 | 106638 |
| 70 | $0.15 | 121688 |
| 71 | $0.05 | 124220 |
| 72 | $0.04 | 125127 |
| 73 | $0.05 | 126156 |
| 74 | $0.04 | 127217 |
| 75 | $0.08 | 132570 |
| 76 | $0.05 | 134311 |
| 77 | $0.04 | 135247 |
| 78 | $0.58 | 90188 |
| 79 | $0.08 | 97435 |
| 80 | $0.03 | 99010 |
| 81 | $0.03 | 100891 |
| 82 | $0.06 | 105801 |
| 83 | $0.06 | 110392 |
| 84 | $0.03 | 111969 |
| 85 | $0.03 | 112544 |
| 86 | $0.03 | 112994 |
| 87 | $0.03 | 113354 |
| 88 | $0.03 | 113719 |
| 89 | $0.03 | 114102 |
| 90 | $0.03 | 114821 |
| 91 | $0.06 | 118953 |
| 92 | $0.04 | 120568 |
| 93 | $0.04 | 121931 |
| 94 | $0.03 | 122848 |
| 95 | $0.03 | 123633 |
| 96 | $0.03 | 124178 |
| 97 | $0.03 | 124921 |
| 98 | $0.09 | 132987 |
| 99 | $0.03 | 134019 |
| 100 | $0.03 | 134550 |
| 101 | $0.03 | 135391 |
| 102 | $0.03 | 136234 |
| 103 | $0.05 | 139296 |
| 104 | $0.03 | 139954 |
| 105 | $0.03 | 140778 |
| 106 | $0.03 | 141540 |
| 107 | $0.03 | 141934 |
| 108 | $0.03 | 142399 |
| 109 | $0.03 | 143206 |
| 110 | $0.04 | 144622 |
| 111 | $0.03 | 145342 |
| 112 | $0.03 | 145680 |
| 113 | $0.04 | 146646 |
| 114 | $0.04 | 147745 |
| 115 | $0.04 | 148458 |
| 116 | $0.03 | 148828 |
| 117 | $0.04 | 149533 |
| 118 | $0.04 | 150756 |
| 119 | $0.04 | 151515 |
| 120 | $0.03 | 152061 |
| 121 | $0.03 | 152619 |
| 122 | $0.03 | 153143 |
| 123 | $0.03 | 153452 |
| 124 | $0.03 | 153766 |
| 125 | $0.03 | 154290 |
| 126 | $0.03 | 154556 |
| 127 | $0.03 | 154832 |
| 128 | $0.03 | 155152 |
| 129 | $0.03 | 155623 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 7 | 1 | 2 | 892 | 0 | 32038 | 0.09 |
| red | 8 | 1 | 0 | 0 | 3009 | 211 | 49 | 94 | 20273 | 1432090 | 236253 | 0.94 |
| green | 6 | 1 | 2 | 0 | 747 | 143 | 31 | 54 | 9241 | 801636 | 105644 | 0.44 |
| pin | 6 | 6 | 0 | 0 | 209 | 128 | 25 | 50 | 7645 | 690417 | 118177 | 0.44 |
| refactor | 3 | 0 | 0 | 0 | 77 | 65 | 10 | 20 | 4234 | 263382 | 100318 | 0.51 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 9 | 2 | 0 | 707 | 208 | 45 | 84 | 15298 | 1131061 | 237310 | 0.86 |
| developer | claude-sonnet-5-5 | 13 | 0 | 0 | 0 | 3348 | 346 | 71 | 136 | 26987 | 2056464 | 355120 | 1.55 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1494 | 0.87 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| After a `develop-*` or `revise-*` leaf launched through `supervise.sh` exits, a `.tdd/issue-*-mutations.md` the leaf rewrote (its content changed, truncated or appended to) is byte-identical to what it held before the leaf ⟦criterion 1⟧ | 15 | 4 | 2 | 0 | 0 | 0 | 315 | 70 | 128 | 24674 | 1807173 | 391725 | 1.60 | 29306 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| After a `develop-*` or `revise-*` leaf launched through `supervise.sh` exits, a `.tdd/issue-*-mutations.md` the leaf deleted is restored, byte-identical to what it held before the leaf ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 61 | 12 | 24 | 4116 | 353761 | 53608 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| After a `develop-*` or `revise-*` leaf launched through `supervise.sh` exits, a `.tdd/issue-*-mutations.md` that did not exist before the leaf and that the leaf created is removed ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 10 | 20 | 3278 | 299814 | 35217 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| When the supervisor restores or removes a `.tdd/issue-*-mutations.md` after a `develop-*` or `revise-*` leaf, it writes one event per restored file naming the leaf and the file ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 10 | 20 | 5013 | 316653 | 38863 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| A verify-pin verifier leaf launched through `supervise.sh` whose probe appends its record to `.tdd/issue-<n>-mutations.md` keeps that append after it exits, with no restore event (#2741's append-only rule unaffected) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 72 | 13 | 26 | 4312 | 410124 | 40979 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| After a `develop-*` or `revise-*` leaf launched through `supervise.sh` exits, a `.tdd/issue-*-mutations.md` the leaf rewrote (its content changed, truncated or appended to) is byte-identical to what it held before the leaf ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 1 | 77 | 0.51 |
| After a `develop-*` or `revise-*` leaf launched through `supervise.sh` exits, a `.tdd/issue-*-mutations.md` the leaf rewrote (its content changed, truncated or appended to) is byte-identical to what it held before the leaf ⟦criterion 1⟧ | 2 | 0/5 | nothing-left | skipped | 1 | 77 | 0.51 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 17 | 16 | 24 | 3 | 13 | 30 | 12 | 25 | 14 | 14 | 17 | 12 | 12 | 15 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 61 | 43 | 35 | 51 | 51 | 38 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 6 | 6 | 4 | 6 | 5 | 6 | 5 | 5 | 5 | 6 | 4 | 6 | 5 | 5 | 5 | 6 | 6 | 5 | 5 | 6 | 4 | 6 | 6 | 5 | 5 | 5 | 5 | 9 | 8 | 9 | 8 | 8 | 6 | 4 | 5 | 5 | 6 | 3 | 3 | 3 | 3 | 4 | 3 | 4 | 4 | 4 | 4 | 3 | 4 | 3 | 4 | 3 | 4 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 4 | 3 | 4 | 3 | 6 | 4 | 4 | 3 | 4 | 3 | 3 | 3 | 4 | 4 | 3 | 3 | 4 | 4 | 6 | 7 | 4 | 3 | 3 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 116 | 220 | 42285 | 3187525 | 592430 | 9.68 (estimate) |
