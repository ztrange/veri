### 📊 Metrics — issue 2208

Wall time for the issue: 879 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Every figure in this report is wall-clock: the log carries no awake-clock reading, so time the machine spent asleep is counted in them.
Steps done: 1 of 6 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.84 over 80 turns, in 2 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 88336 |
| 2 | $0.03 | 88782 |
| 3 | $0.04 | 90654 |
| 4 | $0.03 | 91027 |
| 5 | $0.04 | 91946 |
| 6 | $0.03 | 92258 |
| 7 | $0.03 | 92559 |
| 8 | $0.03 | 93136 |
| 9 | $0.03 | 93785 |
| 10 | $0.05 | 95637 |
| 11 | $0.03 | 96059 |
| 12 | $0.04 | 97459 |
| 13 | $0.04 | 98643 |
| 14 | $0.03 | 99046 |
| 15 | $0.04 | 99857 |
| 16 | $0.03 | 100439 |
| 17 | $0.04 | 101319 |
| 18 | $0.04 | 102719 |
| 19 | $0.04 | 103563 |
| 20 | $0.03 | 103909 |
| 21 | $0.04 | 104771 |
| 22 | $0.04 | 105878 |
| 23 | $0.04 | 106807 |
| 24 | $0.03 | 107263 |
| 25 | $0.04 | 108000 |
| 26 | $0.04 | 108921 |
| 27 | $0.04 | 109844 |
| 28 | $0.04 | 110771 |
| 29 | $0.03 | 111609 |
| 30 | $0.05 | 112673 |
| 31 | $0.04 | 113847 |
| 32 | $0.04 | 114897 |
| 33 | $0.06 | 119030 |
| 34 | $0.04 | 119416 |
| 35 | $0.06 | 122453 |
| 36 | $0.04 | 123410 |
| 37 | $0.04 | 123805 |
| 38 | $0.57 | 88337 |
| 39 | $0.02 | 88848 |
| 40 | $0.02 | 89647 |
| 41 | $0.03 | 91520 |
| 42 | $0.03 | 92663 |
| 43 | $0.03 | 93701 |
| 44 | $0.02 | 94069 |
| 45 | $0.02 | 94623 |
| 46 | $0.02 | 94870 |
| 47 | $0.02 | 95135 |
| 48 | $0.02 | 95575 |
| 49 | $0.02 | 95950 |
| 50 | $0.02 | 96580 |
| 51 | $0.04 | 99651 |
| 52 | $0.02 | 100253 |
| 53 | $0.02 | 100824 |
| 54 | $0.03 | 101575 |
| 55 | $0.02 | 101814 |
| 56 | $0.10 | 112277 |
| 57 | $0.03 | 112900 |
| 58 | $0.03 | 113375 |
| 59 | $0.03 | 114192 |
| 60 | $0.03 | 114490 |
| 61 | $0.03 | 115130 |
| 62 | $0.03 | 115926 |
| 63 | $0.03 | 116281 |
| 64 | $0.03 | 116989 |
| 65 | $0.03 | 117574 |
| 66 | $0.03 | 117887 |
| 67 | $0.03 | 118617 |
| 68 | $0.03 | 119241 |
| 69 | $0.03 | 120063 |
| 70 | $0.03 | 120430 |
| 71 | $0.09 | 128108 |
| 72 | $0.03 | 129076 |
| 73 | $0.03 | 130126 |
| 74 | $0.03 | 130960 |
| 75 | $0.03 | 131282 |
| 76 | $0.03 | 132324 |
| 77 | $0.03 | 133225 |
| 78 | $0.03 | 133953 |
| 79 | $0.06 | 138440 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 16 | 2 | 4 | 1031 | 30370 | 32105 | 0.09 |
| red | 5 | 3 | 0 | 0 | 220 | 99 | 23 | 46 | 8313 | 689745 | 104233 | 0.41 |
| green | 5 | 0 | 0 | 0 | 418 | 129 | 39 | 74 | 8783 | 1140018 | 101510 | 0.65 |
| red-repair | 2 | 0 | 0 | 1 | 51 | 23 | 5 | 8 | 1605 | 110909 | 15046 | 0.06 |
| diff | 2 | 1 | 0 | 0 | 214 | 29 | 6 | 12 | 1521 | 114022 | 59856 | 0.18 |
| exhausted | 1 | 0 | 0 | 0 | 55 | 38 | 3 | 6 | 1356 | 80144 | 18196 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 270 | 62 | 14 | 28 | 4084 | 323999 | 93940 | 0.31 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 1 | 237 | 105 | 22 | 42 | 8386 | 621047 | 117300 | 0.44 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 473 | 167 | 42 | 80 | 10139 | 1220162 | 119706 | 0.79 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 220 | 0.41 |
| green | 0 | 0.00 | 418 | 0.65 |
| red-repair | 0 | 0.00 | 51 | 0.06 |
| diff | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 55 | 0.13 |
| develop-green | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| grade-prose reads a GRADES block naming every requirement ID exactly once but with two rows swapped out of file order, all PASS, as a PASS verdict: exit 0, a grading event with verdict=PASS, the unit's signature recorded in GRADED, as the same rows in file order would give ⟦criterion 1⟧ | 13 | 3 | 0 | 1 | 0 | 0 | 289 | 70 | 134 | 20057 | 2020816 | 238985 | 1.27 | unknown | 2/2 | unknown | unknown |  |  | full |
| test-only: test_a_grades_block_with_a_missing_an_extra_or_a_reordered_requirement_id_makes_grade_prose_exit_2_and_name_the_defect_on_stderr in skills/tdd/scripts/tests/py/test_grade_prose_process.py drops its reordered-block arm (the behaviour criterion 1 removes), keeping its missing-ID and extra-ID arms asserting exit 2 and the defect named on stderr, and is renamed to say missing or extra; no production change ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 6 | 12 | 1521 | 114022 | 59856 | 0.18 | 291 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 15 | 24 | 20 | 23 | 13 | 20 | 102 | 22 | 23 | 104 |
| fast | 16 | 27 | 21 | 21 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 78 | 150 | 22609 | 2165208 | 330946 | 1.54 |
