### 📊 Metrics — issue 2989

Wall time for the issue: 4674 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 7 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.40 over 70 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89513 tokens, largest 191466 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 89513 |
| 2 | $0.08 | 96662 |
| 3 | $0.03 | 98394 |
| 4 | $0.03 | 100288 |
| 5 | $0.03 | 101665 |
| 6 | $0.02 | 102144 |
| 7 | $0.02 | 102514 |
| 8 | $0.02 | 102876 |
| 9 | $0.03 | 103533 |
| 10 | $0.04 | 105885 |
| 11 | $0.10 | 115613 |
| 12 | $0.03 | 116999 |
| 13 | $0.03 | 117873 |
| 14 | $0.04 | 119861 |
| 15 | $0.04 | 121554 |
| 16 | $0.04 | 123287 |
| 17 | $0.04 | 124752 |
| 18 | $0.03 | 125081 |
| 19 | $0.03 | 126079 |
| 20 | $0.03 | 126601 |
| 21 | $0.03 | 126914 |
| 22 | $0.03 | 127579 |
| 23 | $0.04 | 128893 |
| 24 | $0.03 | 129667 |
| 25 | $0.03 | 130377 |
| 26 | $0.03 | 131110 |
| 27 | $0.03 | 131828 |
| 28 | $0.04 | 133028 |
| 29 | $0.04 | 134325 |
| 30 | $0.09 | 142366 |
| 31 | $0.04 | 144046 |
| 32 | $0.04 | 144994 |
| 33 | $0.04 | 145818 |
| 34 | $0.03 | 146411 |
| 35 | $0.04 | 147548 |
| 36 | $0.04 | 148573 |
| 37 | $0.06 | 151801 |
| 38 | $0.03 | 152148 |
| 39 | $0.04 | 152963 |
| 40 | $0.04 | 154167 |
| 41 | $0.04 | 154729 |
| 42 | $0.04 | 156220 |
| 43 | $0.04 | 156810 |
| 44 | $0.04 | 158098 |
| 45 | $0.04 | 158558 |
| 46 | $0.04 | 159531 |
| 47 | $0.04 | 160153 |
| 48 | $0.04 | 161006 |
| 49 | $0.04 | 161793 |
| 50 | $0.05 | 164512 |
| 51 | $0.04 | 164913 |
| 52 | $0.05 | 166862 |
| 53 | $0.04 | 167557 |
| 54 | $0.05 | 169154 |
| 55 | $0.04 | 170370 |
| 56 | $0.04 | 170972 |
| 57 | $0.04 | 171853 |
| 58 | $0.05 | 173184 |
| 59 | $0.05 | 175334 |
| 60 | $0.04 | 176493 |
| 61 | $0.04 | 176944 |
| 62 | $0.06 | 179448 |
| 63 | $0.04 | 180437 |
| 64 | $0.05 | 182116 |
| 65 | $0.04 | 182764 |
| 66 | $0.04 | 183089 |
| 67 | $0.05 | 184323 |
| 68 | $0.04 | 185007 |
| 69 | $0.05 | 186861 |
| 70 | $0.07 | 191466 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 12 | 3 | 6 | 1462 | 66368 | 35380 | 0.11 |
| red | 9 | 4 | 0 | 0 | 1018 | 177 | 38 | 76 | 20290 | 1091528 | 252961 | 1.24 |
| green | 9 | 2 | 2 | 0 | 1878 | 145 | 49 | 96 | 15522 | 1412503 | 194363 | 0.89 |
| refactor | 2 | 0 | 0 | 0 | 19 | 9 | 4 | 8 | 787 | 80424 | 51155 | 0.14 |
| pin | 3 | 0 | 3 | 0 | 149 | 47 | 10 | 20 | 4775 | 255646 | 66407 | 0.24 |
| red-contradicted | 1 | 0 | 0 | 0 | 68 | 37 | 7 | 14 | 3800 | 236561 | 22438 | 0.12 |
| red-missing | 1 | 0 | 0 | 0 | 47 | 23 | 4 | 8 | 2811 | 120543 | 19289 | 0.09 |
| exhausted | 1 | 0 | 0 | 0 | 170 | 19 | 3 | 6 | 1990 | 80230 | 16755 | 0.14 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 7 | 5 | 0 | 1728 | 166 | 43 | 86 | 17937 | 1135581 | 254592 | 0.93 |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 967 | 168 | 48 | 94 | 18638 | 1427149 | 232418 | 0.91 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 672 | 135 | 27 | 54 | 14862 | 781073 | 171738 | 1.14 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 543 | 0.85 |
| green | 724 | 0.42 | 729 | 0.34 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 149 | 0.24 |
| red-contradicted | 0 | 0.00 | 68 | 0.12 |
| red-missing | 0 | 0.00 | 47 | 0.09 |
| exhausted | 0 | 0.00 | 170 | 0.14 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When a unit's first-pass grade FAILs a row and the first confirming re-grade reply has no `BEGIN GRADES` block, grade-prose relaunches that re-grade, and when the relaunch answers with a valid block the run gets its verdict (exit 0 or 1), not exit 2 (unit-tier case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py, faking only the leaf launch; default VERI_NO_VERDICT_RETRIES) ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 79 | 25 | 50 | 8868 | 651883 | 177991 | 0.71 | 1297 | 1/2 | 0/5 | nothing-left |  |  | full |
| When a confirming re-grade reply carries a `BEGIN GRADES` block that keeps_protocol rejects (a repeated requirement ID), grade-prose relaunches that re-grade the same way, and a valid relaunch gives the run its verdict (exit 0 or 1), not exit 2 (unit-tier case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py, faking only the leaf launch) ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 58 | 19 | 38 | 6831 | 535916 | 106722 | 0.39 | 1016 | unknown | 0/5 | nothing-left |  |  | full |
| With VERI_NO_VERDICT_RETRIES=0, a confirming re-grade's first protocol break is not relaunched: grade-prose exits 2 with `the re-grade has no GRADES block for the rows it was asked about` after one launch of that re-grade (unit-tier case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py, faking only the leaf launch) ⟦criterion 3⟧ | 14 | 2 | 4 | 0 | 0 | 0 | 320 | 71 | 140 | 34276 | 2089636 | 338655 | 1.77 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When a unit's first-pass grade FAILs a row and the first confirming re-grade reply has no `BEGIN GRADES` block, grade-prose relaunches that re-grade, and when the relaunch answers with a valid block the run gets its verdict (exit 0 or 1), not exit 2 (unit-tier case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py, faking only the leaf launch; default VERI_NO_VERDICT_RETRIES) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.09 |
| When a confirming re-grade reply carries a `BEGIN GRADES` block that keeps_protocol rejects (a repeated requirement ID), grade-prose relaunches that re-grade the same way, and a valid relaunch gives the run its verdict (exit 0 or 1), not exit 2 (unit-tier case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py, faking only the leaf launch) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.05 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 8 | 87 | 92 | 88 | 7 | 86 | 86 | 86 | 105 | 95 | 0 | 9 | 9 | 91 | 114 | 9 | 105 | 8 | 100 | 10 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 66 | 71 | 52 | 63 | 101 | 71 | 83 | 59 | 92 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 7 | 7 | 7 | 6 | 6 | 6 | 6 | 7 | 7 | 10 | 7 | 8 | 8 | 7 | 7 | 6 | 6 | 7 | 7 | 8 | 8 | 7 | 7 | 6 | 7 | 7 | 9 | 7 | 8 | 7 | 8 | 8 | 8 | 7 | 8 | 8 | 12 | 13 | 9 | 11 | 10 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 118 | 234 | 51437 | 3343803 | 658748 | 6.38 (estimate) |
