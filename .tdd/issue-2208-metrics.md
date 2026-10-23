### 📊 Metrics — issue 2208

Wall time for the issue: 3782 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Every figure in this report is wall-clock: the log carries no awake-clock reading, so time the machine spent asleep is counted in them.
Steps done: 6 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2221.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $7.70 over 167 turns, in 3 sessions.
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
| 38 | $0.58 | 88337 |
| 39 | $0.03 | 88848 |
| 40 | $0.03 | 89647 |
| 41 | $0.04 | 91520 |
| 42 | $0.03 | 92663 |
| 43 | $0.04 | 93701 |
| 44 | $0.03 | 94069 |
| 45 | $0.03 | 94623 |
| 46 | $0.03 | 94870 |
| 47 | $0.03 | 95135 |
| 48 | $0.03 | 95575 |
| 49 | $0.03 | 95950 |
| 50 | $0.03 | 96580 |
| 51 | $0.06 | 99651 |
| 52 | $0.03 | 100253 |
| 53 | $0.03 | 100824 |
| 54 | $0.04 | 101575 |
| 55 | $0.03 | 101814 |
| 56 | $0.11 | 112277 |
| 57 | $0.03 | 112900 |
| 58 | $0.04 | 113375 |
| 59 | $0.04 | 114192 |
| 60 | $0.03 | 114490 |
| 61 | $0.04 | 115130 |
| 62 | $0.03 | 115926 |
| 63 | $0.04 | 116281 |
| 64 | $0.04 | 116989 |
| 65 | $0.03 | 117574 |
| 66 | $0.04 | 117887 |
| 67 | $0.03 | 118617 |
| 68 | $0.04 | 119241 |
| 69 | $0.04 | 120063 |
| 70 | $0.03 | 120430 |
| 71 | $0.10 | 128108 |
| 72 | $0.04 | 129076 |
| 73 | $0.04 | 130126 |
| 74 | $0.04 | 130960 |
| 75 | $0.04 | 131282 |
| 76 | $0.04 | 132324 |
| 77 | $0.05 | 133225 |
| 78 | $0.04 | 133953 |
| 79 | $0.07 | 138440 |
| 80 | $0.04 | 139404 |
| 81 | $0.05 | 140515 |
| 82 | $0.03 | 140761 |
| 83 | $0.57 | 88647 |
| 84 | $0.02 | 89184 |
| 85 | $0.02 | 89989 |
| 86 | $0.03 | 91846 |
| 87 | $0.02 | 92297 |
| 88 | $0.03 | 93620 |
| 89 | $0.05 | 97073 |
| 90 | $0.02 | 97584 |
| 91 | $0.02 | 97911 |
| 92 | $0.02 | 98232 |
| 93 | $0.03 | 98946 |
| 94 | $0.04 | 101969 |
| 95 | $0.04 | 104603 |
| 96 | $0.03 | 106212 |
| 97 | $0.03 | 106923 |
| 98 | $0.03 | 107573 |
| 99 | $0.03 | 108975 |
| 100 | $0.03 | 109965 |
| 101 | $0.03 | 111409 |
| 102 | $0.03 | 112665 |
| 103 | $0.03 | 113367 |
| 104 | $0.03 | 113687 |
| 105 | $0.03 | 114950 |
| 106 | $0.03 | 115624 |
| 107 | $0.03 | 116340 |
| 108 | $0.03 | 116858 |
| 109 | $0.03 | 118045 |
| 110 | $0.03 | 118602 |
| 111 | $0.03 | 119401 |
| 112 | $0.03 | 120586 |
| 113 | $0.03 | 121379 |
| 114 | $0.03 | 122525 |
| 115 | $0.03 | 123604 |
| 116 | $0.03 | 124337 |
| 117 | $0.03 | 124803 |
| 118 | $0.03 | 125546 |
| 119 | $0.03 | 125979 |
| 120 | $0.03 | 126737 |
| 121 | $0.03 | 127138 |
| 122 | $0.03 | 127857 |
| 123 | $0.03 | 128202 |
| 124 | $0.03 | 128833 |
| 125 | $0.03 | 129713 |
| 126 | $0.03 | 130597 |
| 127 | $0.03 | 131697 |
| 128 | $0.05 | 134135 |
| 129 | $0.03 | 134895 |
| 130 | $0.03 | 135150 |
| 131 | $0.03 | 135865 |
| 132 | $0.03 | 136478 |
| 133 | $0.04 | 137565 |
| 134 | $0.03 | 138075 |
| 135 | $0.03 | 138851 |
| 136 | $0.04 | 140679 |
| 137 | $0.03 | 141349 |
| 138 | $0.04 | 142785 |
| 139 | $0.03 | 143387 |
| 140 | $0.04 | 144203 |
| 141 | $0.04 | 145717 |
| 142 | $0.04 | 147005 |
| 143 | $0.04 | 147810 |
| 144 | $0.04 | 149483 |
| 145 | $0.04 | 150139 |
| 146 | $0.04 | 151782 |
| 147 | $0.04 | 152508 |
| 148 | $0.05 | 154875 |
| 149 | $0.04 | 155683 |
| 150 | $0.04 | 157374 |
| 151 | $0.04 | 158067 |
| 152 | $0.04 | 159645 |
| 153 | $0.04 | 160380 |
| 154 | $0.04 | 161589 |
| 155 | $0.04 | 161945 |
| 156 | $0.04 | 162363 |
| 157 | $0.04 | 163293 |
| 158 | $0.04 | 163829 |
| 159 | $0.04 | 164139 |
| 160 | $0.04 | 164995 |
| 161 | $0.04 | 165567 |
| 162 | $0.04 | 166048 |
| 163 | $0.04 | 166318 |
| 164 | $0.04 | 166677 |
| 165 | $0.04 | 166983 |
| 166 | $0.04 | 167606 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 16 | 2 | 4 | 1031 | 30370 | 32105 | 0.09 |
| red | 15 | 8 | 0 | 0 | 535 | 263 | 61 | 122 | 23596 | 1730940 | 303765 | 1.17 |
| green | 14 | 4 | 0 | 0 | 1211 | 271 | 89 | 166 | 20366 | 2436954 | 222748 | 1.20 |
| red-repair | 4 | 0 | 0 | 2 | 83 | 38 | 10 | 18 | 3240 | 257456 | 31307 | 0.14 |
| diff | 2 | 1 | 0 | 0 | 214 | 29 | 6 | 12 | 1521 | 114022 | 59856 | 0.18 |
| exhausted | 1 | 0 | 0 | 0 | 55 | 38 | 3 | 6 | 1356 | 80144 | 18196 | 0.13 |
| refactor | 8 | 4 | 0 | 0 | 287 | 81 | 24 | 46 | 4558 | 588163 | 118538 | 0.40 |
| pin | 1 | 1 | 0 | 0 | 28 | 19 | 4 | 8 | 1254 | 104938 | 13888 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 19 | 19 | 0 | 0 | 1021 | 230 | 62 | 122 | 16446 | 1525574 | 296669 | 1.06 |
| developer | claude-sonnet-5-5 | 21 | 0 | 0 | 2 | 941 | 358 | 95 | 180 | 30337 | 2597251 | 384028 | 1.52 |
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
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| develop-green | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| grade-prose reads a GRADES block naming every requirement ID exactly once but with two rows swapped out of file order, all PASS, as a PASS verdict: exit 0, a grading event with verdict=PASS, the unit's signature recorded in GRADED, as the same rows in file order would give ⟦criterion 1⟧ | 13 | 3 | 0 | 1 | 0 | 0 | 289 | 70 | 134 | 20057 | 2020816 | 238985 | 1.27 | unknown | 2/2 | unknown | unknown |  |  | full |
| test-only: test_a_grades_block_with_a_missing_an_extra_or_a_reordered_requirement_id_makes_grade_prose_exit_2_and_name_the_defect_on_stderr in skills/tdd/scripts/tests/py/test_grade_prose_process.py drops its reordered-block arm (the behaviour criterion 1 removes), keeping its missing-ID and extra-ID arms asserting exit 2 and the defect named on stderr, and is renamed to say missing or extra; no production change ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 6 | 12 | 1521 | 114022 | 59856 | 0.18 | 291 | n/a | n/a | n/a |  |  | full |
| grade-prose reads a GRADES block naming every requirement ID exactly once but with two rows swapped out of file order, all PASS, as a PASS verdict: exit 0, an events.jsonl grading event whose verdict field is PASS, the unit's signature recorded in GRADED, as the same rows in file order would give ⟦criterion 1⟧ | 10 | 4 | 0 | 1 | 0 | 0 | 144 | 39 | 76 | 10702 | 1050755 | 153531 | 0.60 | 642 | unknown | 0/5 | nothing-left |  |  | full |
| grade-prose reads a GRADES block naming every requirement ID exactly once with a FAIL row swapped out of file order as a REJECT verdict: exit 1, the FAIL row printed and an events.jsonl grading event whose verdict field is REJECT, naming it, as the same rows in file order would give ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 9 | 18 | 3778 | 255549 | 33993 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| a GRADES block that leaves out one requirement ID makes grade-prose exit 2 with no verdict, its stderr naming the missing ID as missing, and no grading event appended ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 84 | 22 | 40 | 6377 | 534143 | 94771 | 0.35 | 386 | unknown | 0/5 | nothing-left |  |  | full |
| a GRADES block that names one requirement ID twice makes grade-prose exit 2 with no verdict, its stderr naming the repeated ID as repeated, and no grading event appended ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 84 | 26 | 52 | 6996 | 719847 | 98497 | 0.39 | 582 | unknown | 0/5 | nothing-left |  |  | full |
| a GRADES block that names an ID the unit's requirements list does not hold makes grade-prose exit 2 with no verdict, its stderr naming the unknown ID as unknown, and no grading event appended ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 66 | 25 | 46 | 6460 | 617485 | 88665 | 0.35 | 369 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| grade-prose reads a GRADES block naming every requirement ID exactly once but with two rows swapped out of file order, all PASS, as a PASS verdict: exit 0, an events.jsonl grading event whose verdict field is PASS, the unit's signature recorded in GRADED, as the same rows in file order would give ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 60 | 0.09 |
| a GRADES block that leaves out one requirement ID makes grade-prose exit 2 with no verdict, its stderr naming the missing ID as missing, and no grading event appended ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 70 | 0.10 |
| a GRADES block that names one requirement ID twice makes grade-prose exit 2 with no verdict, its stderr naming the repeated ID as repeated, and no grading event appended ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 94 | 0.12 |
| a GRADES block that names an ID the unit's requirements list does not hold makes grade-prose exit 2 with no verdict, its stderr naming the unknown ID as unknown, and no grading event appended ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 63 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 15 | 24 | 20 | 23 | 13 | 20 | 102 | 22 | 23 | 104 | 11 | 12 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 13 | 8 | 3 | 13 | 12 | 11 | 4 | 102 | 8 | 3 | 3 | 18 | 26 | 13 |
| fast | 16 | 27 | 21 | 21 | 17 | 18 | 18 | 18 | 19 | 51 | 28 | 21 | 60 | 58 | 22 | 59 | 18 | 18 | 25 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 11 | 3 | 3 | 5 | 3 | 12 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 199 | 382 | 56922 | 5342987 | 800403 | 3.37 |
