### 📊 Metrics — issue 2973

Wall time for the issue: 11216 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2982.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.19 over 75 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88992 tokens, largest 164501 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88992 |
| 2 | $0.07 | 95969 |
| 3 | $0.03 | 97712 |
| 4 | $0.03 | 99297 |
| 5 | $0.03 | 100728 |
| 6 | $0.03 | 101461 |
| 7 | $0.02 | 101826 |
| 8 | $0.02 | 102201 |
| 9 | $0.02 | 102499 |
| 10 | $0.02 | 102840 |
| 11 | $0.02 | 103310 |
| 12 | $0.02 | 103702 |
| 13 | $0.03 | 104380 |
| 14 | $0.02 | 104892 |
| 15 | $0.05 | 108956 |
| 16 | $0.04 | 110985 |
| 17 | $0.03 | 111933 |
| 18 | $0.03 | 112367 |
| 19 | $0.03 | 112975 |
| 20 | $0.03 | 113508 |
| 21 | $0.03 | 114218 |
| 22 | $0.03 | 114654 |
| 23 | $0.04 | 116699 |
| 24 | $0.03 | 117522 |
| 25 | $0.05 | 120218 |
| 26 | $0.03 | 120934 |
| 27 | $0.09 | 128607 |
| 28 | $0.03 | 129565 |
| 29 | $0.03 | 130589 |
| 30 | $0.03 | 131414 |
| 31 | $0.03 | 131671 |
| 32 | $0.03 | 132502 |
| 33 | $0.03 | 133189 |
| 34 | $0.03 | 134043 |
| 35 | $0.03 | 134710 |
| 36 | $0.04 | 136245 |
| 37 | $0.04 | 137577 |
| 38 | $0.04 | 138863 |
| 39 | $0.03 | 139435 |
| 40 | $0.03 | 140132 |
| 41 | $0.03 | 140892 |
| 42 | $0.03 | 141642 |
| 43 | $0.04 | 142858 |
| 44 | $0.04 | 143664 |
| 45 | $0.04 | 144549 |
| 46 | $0.03 | 145283 |
| 47 | $0.03 | 145776 |
| 48 | $0.04 | 146717 |
| 49 | $0.04 | 147835 |
| 50 | $0.04 | 148947 |
| 51 | $0.04 | 149912 |
| 52 | $0.04 | 150863 |
| 53 | $0.04 | 151548 |
| 54 | $0.04 | 152620 |
| 55 | $0.04 | 153892 |
| 56 | $0.04 | 154802 |
| 57 | $0.04 | 156110 |
| 58 | $0.04 | 156675 |
| 59 | $0.04 | 157366 |
| 60 | $0.04 | 158254 |
| 61 | $0.04 | 158925 |
| 62 | $0.04 | 159837 |
| 63 | $0.03 | 160143 |
| 64 | $0.03 | 160445 |
| 65 | $0.03 | 160761 |
| 66 | $0.04 | 161255 |
| 67 | $0.04 | 161803 |
| 68 | $0.03 | 162078 |
| 69 | $0.03 | 162367 |
| 70 | $0.03 | 162656 |
| 71 | $0.04 | 163004 |
| 72 | $0.04 | 163451 |
| 73 | $0.04 | 163761 |
| 74 | $0.04 | 164175 |
| 75 | $0.04 | 164501 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 11 | 1 | 2 | 1019 | 17157 | 15417 | 0.05 |
| red | 7 | 2 | 0 | 0 | 883 | 325 | 58 | 116 | 29933 | 2197922 | 250100 | 1.52 |
| pin | 3 | 1 | 2 | 0 | 157 | 77 | 15 | 30 | 5055 | 447300 | 37542 | 0.19 |
| green | 4 | 2 | 0 | 0 | 911 | 129 | 22 | 44 | 6863 | 687866 | 74662 | 0.32 |
| refactor | 3 | 1 | 0 | 0 | 239 | 51 | 12 | 24 | 2564 | 346119 | 50472 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 7 | 2 | 0 | 911 | 195 | 38 | 76 | 13250 | 1119785 | 143425 | 0.60 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 559 | 234 | 38 | 76 | 21735 | 1525266 | 161147 | 1.15 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 738 | 164 | 32 | 64 | 10449 | 1051313 | 123621 | 0.52 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 157 | 0.19 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Go: a frozen case whose body record digest equals neither its body at the green sha nor its body at HEAD is still skipped by `rerecord-refactored` after a verified refactor (`.tdd/verdict-refactor.exit` = 0), a `skipped: <file> <case>` line on stderr, and its record file left byte-for-byte untouched, `helpers:` line included (a git repo in tmp_path: a medium case marked process, in test_tests_frozen_process.py) ⟦criterion 2⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 179 | 36 | 72 | 15431 | 1419431 | 108122 | 0.76 | unknown | 1/2 | unknown | unknown |  |  | pin |
| Go: a frozen case whose body record already equals its body at HEAD, after a verified refactor that lost or added an assertion line of the case or a helper it calls, is still skipped by `rerecord-refactored`, naming the case on a `skipped: <file> <case>` line, with its stale `helpers:` line left as recorded (a git repo in tmp_path: a medium case marked process, in test_tests_frozen_process.py) ⟦criterion 3⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 254 | 39 | 78 | 18231 | 1236320 | 166812 | 0.90 | 1894 | 1/2 | 0/5 | nothing-left |  |  | full |
| Go, the issue's steps 1-4: a frozen case recorded at green, then a verified `refactor:` commit that changes the case body and moves (loses none of) the assertion lines of a helper it calls, then its body line re-recorded at HEAD with `tests-frozen.sh record` leaving the old `helpers:` line: `rerecord-refactored <ledger> <green-sha>` leaves the case's `helpers:` line holding HEAD's helper digest, prints no `skipped:` line for it, and `check-earlier --step "<next step>"` exits 0 (a git repo in tmp_path: a medium case marked process, in test_tests_frozen_process.py) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 149 | 32 | 64 | 10753 | 1023456 | 137842 | 0.55 | 1534 | unknown | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Go: a frozen case whose body record already equals its body at HEAD, after a verified refactor that lost or added an assertion line of the case or a helper it calls, is still skipped by `rerecord-refactored`, naming the case on a `skipped: <file> <case>` line, with its stale `helpers:` line left as recorded (a git repo in tmp_path: a medium case marked process, in test_tests_frozen_process.py) ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 24 | 0.06 |
| Go, the issue's steps 1-4: a frozen case recorded at green, then a verified `refactor:` commit that changes the case body and moves (loses none of) the assertion lines of a helper it calls, then its body line re-recorded at HEAD with `tests-frozen.sh record` leaving the old `helpers:` line: `rerecord-refactored <ledger> <green-sha>` leaves the case's `helpers:` line holding HEAD's helper digest, prints no `skipped:` line for it, and `check-earlier --step "<next step>"` exits 0 (a git repo in tmp_path: a medium case marked process, in test_tests_frozen_process.py) ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 215 | 0.12 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 20 | 19 | 12 | 15 | 11 | 58 | 65 | 9 | 10 | 62 | 50 | 0 | 51 | 11 | 59 | 54 | 53 | 54 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 13 | 10 | 10 | 11 | 7 | 9 | 8 | 7 | 9 | 7 | 6 | 7 | 7 | 7 | 8 | 8 | 10 | 10 | 12 | 10 | 10 | 9 | 8 | 6 | 7 | 9 | 10 | 9 | 11 | 12 | 10 | 9 | 10 | 11 | 12 | 14 | 12 | 10 | 12 | 11 | 12 | 11 | 9 | 10 | 10 | 11 | 12 | 12 | 8 | 12 | 13 | 12 | 11 | 10 | 11 | 9 | 8 | 12 | 11 | 13 | 13 | 14 | 10 | 9 | 10 | 9 | 9 | 7 | 8 | 6 | 6 | 8 | 7 | 8 | 6 | 8 | 7 | 11 | 10 | 8 | 7 | 6 | 6 | 6 | 6 | 6 | 7 | 7 | 7 | 6 | 8 | 8 | 7 | 7 | 8 | 6 | 7 | 7 | 12 | 11 | 14 | 10 | 11 | 9 | 10 | 11 | 11 | 9 | 10 | 12 | 12 | 14 | 10 | 13 | 10 | 8 | 8 | 8 | 8 | 8 | 9 | 10 | 9 | 9 | 8 | 9 |
| fast | 87 | 69 | 58 | 70 | 66 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 108 | 216 | 45434 | 3696364 | 428193 | 5.46 (estimate) |
