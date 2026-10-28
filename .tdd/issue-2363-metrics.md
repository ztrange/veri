### 📊 Metrics — issue 2363

Wall time for the issue: 1199 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run bailed — no-verdict, a system failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.33 over 53 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89282 tokens, largest 151715 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 89282 |
| 2 | $0.02 | 89831 |
| 3 | $0.03 | 90882 |
| 4 | $0.03 | 92967 |
| 5 | $0.02 | 93523 |
| 6 | $0.02 | 93990 |
| 7 | $0.02 | 94427 |
| 8 | $0.02 | 94722 |
| 9 | $0.02 | 95297 |
| 10 | $0.02 | 95612 |
| 11 | $0.03 | 97270 |
| 12 | $0.04 | 100065 |
| 13 | $0.03 | 101868 |
| 14 | $0.04 | 104895 |
| 15 | $0.03 | 105805 |
| 16 | $0.03 | 106294 |
| 17 | $0.03 | 107161 |
| 18 | $0.03 | 107667 |
| 19 | $0.03 | 108600 |
| 20 | $0.03 | 109978 |
| 21 | $0.03 | 111386 |
| 22 | $0.03 | 112383 |
| 23 | $0.03 | 113371 |
| 24 | $0.03 | 114662 |
| 25 | $0.03 | 115080 |
| 26 | $0.03 | 115668 |
| 27 | $0.03 | 116091 |
| 28 | $0.03 | 116729 |
| 29 | $0.03 | 117454 |
| 30 | $0.04 | 119962 |
| 31 | $0.03 | 121030 |
| 32 | $0.04 | 122660 |
| 33 | $0.09 | 131259 |
| 34 | $0.04 | 133448 |
| 35 | $0.03 | 134386 |
| 36 | $0.04 | 135742 |
| 37 | $0.03 | 136453 |
| 38 | $0.03 | 137377 |
| 39 | $0.03 | 138177 |
| 40 | $0.04 | 139286 |
| 41 | $0.04 | 140465 |
| 42 | $0.04 | 141449 |
| 43 | $0.03 | 142149 |
| 44 | $0.04 | 143098 |
| 45 | $0.04 | 144079 |
| 46 | $0.03 | 144345 |
| 47 | $0.03 | 144598 |
| 48 | $0.03 | 145149 |
| 49 | $0.04 | 145968 |
| 50 | $0.03 | 146365 |
| 51 | $0.03 | 146996 |
| 52 | $0.06 | 151113 |
| 53 | $0.04 | 151715 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 12 | 3 | 6 | 1510 | 63655 | 34176 | 0.11 |
| red | 5 | 3 | 0 | 0 | 86 | 66 | 17 | 32 | 6672 | 394599 | 117683 | 0.52 |
| green | 4 | 1 | 0 | 0 | 191 | 82 | 24 | 48 | 7085 | 758524 | 46122 | 0.26 |
| red-contradicted | 1 | 0 | 0 | 0 | 19 | 16 | 4 | 8 | 2107 | 115704 | 16765 | 0.07 |
| refactor | 1 | 0 | 0 | 0 | 7 | 5 | 2 | 4 | 194 | 48569 | 15318 | 0.05 |
| prose | 4 | 0 | 0 | 0 | 332 | 324 | 4 | 8 | 52145 | 4388 | 394813 | 1.51 |
| skill-edit | 1 | 0 | 0 | 0 | 8 | 6 | 2 | 4 | 284 | 143339 | 108035 | 0.29 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 94 | 57 | 15 | 30 | 5510 | 371490 | 92983 | 0.32 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 39 | 31 | 8 | 14 | 3805 | 164704 | 73447 | 0.36 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 185 | 93 | 27 | 54 | 8253 | 844857 | 63634 | 0.33 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `unpointed_sends` accepts a pointer only within the trigger's own sentence: a planted send whose event-file pointer sits in a neighbouring sentence on the same line is reported by event file and line (pinned by a small unit case in skills/tdd/scripts/tests/py/unit/test_skill_event_pointer_guard.py; no production change) ⟦guard-subject: skills/tdd/scripts/tests/py/unit/test_skill_event_files.py⟧ ⟦criterion 1⟧ | 11 | 4 | 0 | 0 | 0 | 0 | 169 | 47 | 92 | 16058 | 1317396 | 195888 | 0.90 | 532 | 1/2 | 0/5 | nothing-left |  |  | full |
| skills/tdd/SKILL.md: the *Launching a leaf* sentence sending `at-leaf` or `now` to *Stopping* is reworded so that no word of it can be read as naming the `now` stop mode, keeping its STOPPING.md pointer at the sentence's end, regraded against skills/tdd/REQUIREMENTS.md as it stands ⟦skill-edit⟧ ⟦criterion 2⟧ | 4 | 0 | 0 | 0 | 0 | 0 | 228 | 5 | 10 | 36137 | 147078 | 394794 | 1.36 | 262 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `unpointed_sends` accepts a pointer only within the trigger's own sentence: a planted send whose event-file pointer sits in a neighbouring sentence on the same line is reported by event file and line (pinned by a small unit case in skills/tdd/scripts/tests/py/unit/test_skill_event_pointer_guard.py; no production change) ⟦guard-subject: skills/tdd/scripts/tests/py/unit/test_skill_event_files.py⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 2 | 2 | 1 | 2 | 1 | 2 | 1 | 2 | 2 |
| fast | 17 | 17 | 16 | 17 | 17 |  |  |  |  |  |  |
| target | 2 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 56 | 110 | 69997 | 1528778 | 732912 | 5.13 (estimate) |
