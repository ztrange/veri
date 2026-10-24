### 📊 Metrics — issue 2300

Wall time for the issue: 1955 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Every figure in this report is wall-clock: the log carries no awake-clock reading, so time the machine spent asleep is counted in them.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2302.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.36 over 73 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90072 |
| 2 | $0.03 | 91146 |
| 3 | $0.03 | 93078 |
| 4 | $0.02 | 93378 |
| 5 | $0.02 | 93770 |
| 6 | $0.02 | 94100 |
| 7 | $0.02 | 94424 |
| 8 | $0.02 | 95087 |
| 9 | $0.04 | 98170 |
| 10 | $0.05 | 102267 |
| 11 | $0.11 | 112859 |
| 12 | $0.04 | 114674 |
| 13 | $0.03 | 115617 |
| 14 | $0.03 | 116362 |
| 15 | $0.04 | 117844 |
| 16 | $0.03 | 118773 |
| 17 | $0.03 | 119722 |
| 18 | $0.03 | 120735 |
| 19 | $0.03 | 121844 |
| 20 | $0.03 | 123050 |
| 21 | $0.03 | 123772 |
| 22 | $0.03 | 124573 |
| 23 | $0.03 | 125624 |
| 24 | $0.03 | 126449 |
| 25 | $0.03 | 127630 |
| 26 | $0.04 | 129118 |
| 27 | $0.03 | 129963 |
| 28 | $0.04 | 131792 |
| 29 | $0.03 | 132514 |
| 30 | $0.04 | 134047 |
| 31 | $0.03 | 134764 |
| 32 | $0.04 | 136110 |
| 33 | $0.04 | 137251 |
| 34 | $0.05 | 139724 |
| 35 | $0.04 | 140691 |
| 36 | $0.04 | 142240 |
| 37 | $0.04 | 143244 |
| 38 | $0.04 | 145243 |
| 39 | $0.05 | 147514 |
| 40 | $0.04 | 148321 |
| 41 | $0.04 | 149837 |
| 42 | $0.04 | 151041 |
| 43 | $0.04 | 151925 |
| 44 | $0.05 | 153963 |
| 45 | $0.05 | 156435 |
| 46 | $0.04 | 157208 |
| 47 | $0.04 | 158029 |
| 48 | $0.03 | 158384 |
| 49 | $0.04 | 159054 |
| 50 | $0.04 | 160647 |
| 51 | $0.04 | 162068 |
| 52 | $0.04 | 162690 |
| 53 | $0.04 | 164055 |
| 54 | $0.04 | 165026 |
| 55 | $0.04 | 165790 |
| 56 | $0.04 | 166798 |
| 57 | $0.04 | 167191 |
| 58 | $0.04 | 167857 |
| 59 | $0.04 | 169108 |
| 60 | $0.04 | 169789 |
| 61 | $0.04 | 170560 |
| 62 | $0.04 | 171732 |
| 63 | $0.05 | 173532 |
| 64 | $0.04 | 174547 |
| 65 | $0.04 | 175252 |
| 66 | $0.04 | 176153 |
| 67 | $0.04 | 176887 |
| 68 | $0.04 | 177702 |
| 69 | $0.04 | 178141 |
| 70 | $0.04 | 178698 |
| 71 | $0.04 | 179540 |
| 72 | $0.04 | 180490 |
| 73 | $0.04 | 181056 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 2 | 4 | 872 | 31257 | 33437 | 0.10 |
| red | 10 | 4 | 0 | 0 | 198 | 126 | 46 | 92 | 15549 | 1396619 | 204273 | 0.81 |
| green | 8 | 4 | 0 | 0 | 243 | 71 | 32 | 60 | 8093 | 831243 | 125715 | 0.48 |
| refactor | 7 | 3 | 0 | 0 | 131 | 60 | 25 | 50 | 6626 | 688717 | 103286 | 0.39 |
| pin | 2 | 2 | 0 | 0 | 40 | 24 | 9 | 18 | 2121 | 244765 | 28251 | 0.12 |
| cover | 3 | 0 | 0 | 0 | 103 | 44 | 18 | 36 | 4929 | 518749 | 45616 | 0.22 |
| predicate | 2 | 0 | 0 | 0 | 14 | 10 | 4 | 8 | 982 | 92848 | 26402 | 0.09 |
| structural | 1 | 0 | 0 | 0 | 7 | 5 | 3 | 6 | 547 | 77985 | 14061 | 0.05 |
| transform | 1 | 0 | 1 | 0 | 8 | 5 | 3 | 6 | 433 | 73925 | 11288 | 0.04 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 15 | 14 | 1 | 0 | 302 | 116 | 49 | 98 | 11634 | 1262771 | 233679 | 0.83 |
| developer | claude-sonnet-5-5 | 20 | 0 | 0 | 0 | 452 | 237 | 93 | 182 | 28518 | 2693337 | 358650 | 1.45 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 8 | 0.04 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A first grader reply whose GRADES block names one requirement ID twice relaunches the grader, and a well-formed second reply grades normally: grade-prose exits 0 after 2 launches (a small case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py with the grader stubbed in-process) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 43 | 18 | 34 | 5257 | 458664 | 100782 | 0.35 | 181 | unknown | 0/5 | nothing-left |  |  | full |
| A first grader reply whose GRADES block names an ID the requirements list does not hold relaunches the grader, and a well-formed second reply grades normally: grade-prose exits 0 after 2 launches (a small case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py with the grader stubbed in-process) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 55 | 25 | 48 | 6683 | 689042 | 97542 | 0.38 | 208 | unknown | 1/5 | structural-owed |  |  | full |
| A first grader reply whose GRADES block carries a grade word other than PASS or FAIL relaunches the grader, and a well-formed second reply grades normally: grade-prose exits 0 after 2 launches (a small case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py with the grader stubbed in-process) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 54 | 22 | 44 | 6128 | 619665 | 98543 | 0.37 | 198 | unknown | 1/5 | structural-owed |  |  | full |
| A first grader reply with text after END GRADES relaunches the grader, and a well-formed second reply grades normally: grade-prose exits 0 after 2 launches (a small case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py with the grader stubbed in-process) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 56 | 22 | 44 | 6340 | 614038 | 95682 | 0.36 | 200 | unknown | 1/5 | nothing-structural |  |  | full |
| With VERI_NO_VERDICT_RETRIES=2, a grader whose every reply names one requirement ID twice is launched 3 times, then grade-prose exits 2 with the same "GRADES block names requirement IDs repeated" message and appends no grading event (a small case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py with the grader stubbed in-process) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 13 | 26 | 4182 | 421911 | 36475 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_grade_prose_process.py — FAILED test_a_malformed_grade_word_in_the_first_reply_is_named_without_a_follow_up_grader_call_2215 - AssertionError: (2, 2, ...) expected (2, 1, True): a malformed grade word now relaunches the grader within VERI_NO_VERDICT_RETRIES, so the case must expect retries + 1 launches and still no missing-IDs follow-up ⟦suite-repair⟧ ⟦criterion 1⟧ | 9 | 1 | 1 | 0 | 0 | 0 | 96 | 40 | 80 | 10690 | 1121531 | 129868 | 0.54 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A first grader reply whose GRADES block names one requirement ID twice relaunches the grader, and a well-formed second reply grades normally: grade-prose exits 0 after 2 launches (a small case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py with the grader stubbed in-process) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |
| A first grader reply whose GRADES block names an ID the requirements list does not hold relaunches the grader, and a well-formed second reply grades normally: grade-prose exits 0 after 2 launches (a small case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py with the grader stubbed in-process) ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 39 | 0.11 |
| A first grader reply whose GRADES block carries a grade word other than PASS or FAIL relaunches the grader, and a well-formed second reply grades normally: grade-prose exits 0 after 2 launches (a small case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py with the grader stubbed in-process) ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 41 | 0.12 |
| A first grader reply with text after END GRADES relaunches the grader, and a well-formed second reply grades normally: grade-prose exits 0 after 2 launches (a small case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py with the grader stubbed in-process) ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 45 | 0.12 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 9 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 10 | 11 | 12 | 10 | 10 | 10 |
| fast | 15 | 15 | 16 | 15 | 15 | 15 | 16 | 15 | 16 | 16 | 16 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 1 | 1 | 1 | 1 | 1 | 3 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 142 | 280 | 40152 | 3956108 | 592329 | 2.28 |
