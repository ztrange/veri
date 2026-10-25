### 📊 Metrics — issue 2338

Wall time for the issue: 8106 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run bailed — suite-red, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $8.46 over 165 turns, in 3 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 91003 tokens, largest 156310 tokens
Conductor context: first turn 90932 tokens, largest 103865 tokens
Conductor context: first turn 91138 tokens, largest 207703 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.60 | 91003 |
| 2 | $0.03 | 91338 |
| 3 | $0.04 | 92192 |
| 4 | $0.04 | 94120 |
| 5 | $0.04 | 94456 |
| 6 | $0.03 | 94823 |
| 7 | $0.03 | 95159 |
| 8 | $0.03 | 95489 |
| 9 | $0.04 | 95783 |
| 10 | $0.03 | 96594 |
| 11 | $0.04 | 96967 |
| 12 | $0.09 | 104993 |
| 13 | $0.06 | 108278 |
| 14 | $0.05 | 111179 |
| 15 | $0.06 | 113966 |
| 16 | $0.04 | 115119 |
| 17 | $0.04 | 115578 |
| 18 | $0.04 | 116402 |
| 19 | $0.04 | 116961 |
| 20 | $0.04 | 117736 |
| 21 | $0.04 | 118336 |
| 22 | $0.05 | 120418 |
| 23 | $0.05 | 121598 |
| 24 | $0.04 | 122277 |
| 25 | $0.04 | 123148 |
| 26 | $0.04 | 123802 |
| 27 | $0.05 | 125328 |
| 28 | $0.04 | 125736 |
| 29 | $0.04 | 126588 |
| 30 | $0.04 | 127171 |
| 31 | $0.04 | 127474 |
| 32 | $0.05 | 128682 |
| 33 | $0.04 | 129572 |
| 34 | $0.05 | 130679 |
| 35 | $0.09 | 137913 |
| 36 | $0.06 | 140577 |
| 37 | $0.05 | 141878 |
| 38 | $0.05 | 142740 |
| 39 | $0.05 | 144663 |
| 40 | $0.05 | 145998 |
| 41 | $0.05 | 146872 |
| 42 | $0.05 | 148056 |
| 43 | $0.05 | 148595 |
| 44 | $0.05 | 149839 |
| 45 | $0.08 | 154529 |
| 46 | $0.05 | 155445 |
| 47 | $0.04 | 156310 |
| 48 | $0.59 | 90932 |
| 49 | $0.03 | 91303 |
| 50 | $0.03 | 92178 |
| 51 | $0.03 | 92614 |
| 52 | $0.04 | 94399 |
| 53 | $0.04 | 96509 |
| 54 | $0.06 | 100551 |
| 55 | $0.03 | 101095 |
| 56 | $0.03 | 101508 |
| 57 | $0.03 | 101794 |
| 58 | $0.03 | 102078 |
| 59 | $0.03 | 102462 |
| 60 | $0.04 | 103206 |
| 61 | $0.03 | 103865 |
| 62 | $0.59 | 91138 |
| 63 | $0.02 | 91554 |
| 64 | $0.03 | 92863 |
| 65 | $0.05 | 97225 |
| 66 | $0.04 | 99369 |
| 67 | $0.05 | 103138 |
| 68 | $0.02 | 103527 |
| 69 | $0.03 | 104630 |
| 70 | $0.02 | 105042 |
| 71 | $0.02 | 105357 |
| 72 | $0.03 | 106087 |
| 73 | $0.03 | 106989 |
| 74 | $0.03 | 107751 |
| 75 | $0.03 | 108569 |
| 76 | $0.03 | 109968 |
| 77 | $0.03 | 111094 |
| 78 | $0.03 | 111927 |
| 79 | $0.03 | 112675 |
| 80 | $0.03 | 113801 |
| 81 | $0.03 | 114570 |
| 82 | $0.03 | 115590 |
| 83 | $0.03 | 116445 |
| 84 | $0.03 | 117062 |
| 85 | $0.03 | 117358 |
| 86 | $0.03 | 118065 |
| 87 | $0.03 | 118608 |
| 88 | $0.03 | 119708 |
| 89 | $0.03 | 120504 |
| 90 | $0.09 | 128262 |
| 91 | $0.04 | 130198 |
| 92 | $0.03 | 131115 |
| 93 | $0.03 | 131730 |
| 94 | $0.04 | 133433 |
| 95 | $0.03 | 134303 |
| 96 | $0.03 | 134781 |
| 97 | $0.03 | 135553 |
| 98 | $0.03 | 136281 |
| 99 | $0.03 | 136814 |
| 100 | $0.04 | 138290 |
| 101 | $0.03 | 139097 |
| 102 | $0.03 | 139957 |
| 103 | $0.04 | 141270 |
| 104 | $0.04 | 142155 |
| 105 | $0.04 | 143908 |
| 106 | $0.04 | 144815 |
| 107 | $0.03 | 145146 |
| 108 | $0.04 | 146882 |
| 109 | $0.04 | 147764 |
| 110 | $0.03 | 148205 |
| 111 | $0.05 | 150136 |
| 112 | $0.03 | 150562 |
| 113 | $0.04 | 151883 |
| 114 | $0.04 | 152715 |
| 115 | $0.05 | 155581 |
| 116 | $0.04 | 156113 |
| 117 | $0.04 | 156906 |
| 118 | $0.05 | 158876 |
| 119 | $0.04 | 159789 |
| 120 | $0.04 | 161276 |
| 121 | $0.04 | 162099 |
| 122 | $0.04 | 163003 |
| 123 | $0.04 | 163877 |
| 124 | $0.04 | 164602 |
| 125 | $0.04 | 165807 |
| 126 | $0.04 | 167032 |
| 127 | $0.05 | 168871 |
| 128 | $0.04 | 169587 |
| 129 | $0.04 | 169877 |
| 130 | $0.04 | 170679 |
| 131 | $0.05 | 172345 |
| 132 | $0.04 | 173417 |
| 133 | $0.05 | 175307 |
| 134 | $0.04 | 175711 |
| 135 | $0.04 | 176558 |
| 136 | $0.05 | 177817 |
| 137 | $0.04 | 178749 |
| 138 | $0.04 | 179041 |
| 139 | $0.05 | 180738 |
| 140 | $0.04 | 181226 |
| 141 | $0.05 | 182459 |
| 142 | $0.04 | 183211 |
| 143 | $0.05 | 184564 |
| 144 | $0.04 | 185290 |
| 145 | $0.05 | 186908 |
| 146 | $0.04 | 187806 |
| 147 | $0.05 | 189405 |
| 148 | $0.05 | 190569 |
| 149 | $0.05 | 191939 |
| 150 | $0.05 | 193800 |
| 151 | $0.05 | 194608 |
| 152 | $0.05 | 195718 |
| 153 | $0.04 | 196008 |
| 154 | $0.04 | 196259 |
| 155 | $0.04 | 196689 |
| 156 | $0.05 | 197937 |
| 157 | $0.05 | 199293 |
| 158 | $0.05 | 199961 |
| 159 | $0.05 | 200961 |
| 160 | $0.05 | 201912 |
| 161 | $0.04 | 202200 |
| 162 | $0.04 | 202555 |
| 163 | $0.04 | 203023 |
| 164 | $0.05 | 203641 |
| 165 | $0.07 | 207703 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 10 | 1 | 2 | 1204 | 0 | 31244 | 0.09 |
| diff | 6 | 3 | 0 | 0 | 1111 | 177 | 41 | 80 | 22943 | 1549995 | 214677 | 0.92 |
| red | 13 | 5 | 0 | 0 | 1156 | 346 | 82 | 164 | 38610 | 2764418 | 371959 | 1.97 |
| green | 25 | 3 | 8 | 0 | 3657 | 420 | 125 | 236 | 42842 | 3431383 | 527671 | 2.99 |
| exhausted | 1 | 0 | 0 | 0 | 21 | 18 | 3 | 6 | 1390 | 75532 | 14493 | 0.12 |
| refactor | 5 | 2 | 0 | 0 | 188 | 49 | 19 | 38 | 6089 | 514995 | 96566 | 0.35 |
| red-missing | 2 | 0 | 0 | 0 | 257 | 52 | 10 | 20 | 7422 | 307025 | 63187 | 0.26 |
| pin | 4 | 3 | 1 | 0 | 156 | 62 | 19 | 38 | 7341 | 521661 | 85003 | 0.34 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 26 | 17 | 9 | 0 | 2991 | 321 | 103 | 202 | 36277 | 2701263 | 466944 | 1.80 |
| developer | claude-sonnet-5-5 | 18 | 0 | 0 | 0 | 2274 | 449 | 119 | 234 | 58033 | 4170262 | 532763 | 2.51 |
| developer | claude-opus-5-5 | 13 | 0 | 0 | 0 | 1293 | 364 | 78 | 148 | 33531 | 2293484 | 405093 | 2.73 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 9688 | 5.89 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 35 | 0.07 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Older cases whose stub grader answers a grade with a FAIL row (in skills/tdd/scripts/tests/py/unit/test_grade_prose.py, skills/tdd/scripts/tests/py/test_grade_prose_process.py, skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py, skills/tdd/scripts/tests/py/test_skill_edit_step_process.py and skills/tdd/scripts/tests/py/unit/test_prose_owed_gate.py) also answer the re-grades that follow it — a reply grading only the rows it is asked about, failing the same rows again — so each keeps its own assertion when a FAIL row is confirmed by two re-grades; every such case stays green against today's code, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 129 | 22 | 42 | 17518 | 1068440 | 105895 | 0.55 | 338 | n/a | n/a | n/a |  |  | full |
| When a grade has one or more FAIL rows, grade-prose.sh re-grades the unit twice against only those rows (each re-grade's prompt lists the failed rows and no other), and a row that reads FAIL in both re-grades counts as failed: the unit is REJECT (exit 1) and the reason printed lists that row ⟦criterion 1⟧ | 18 | 4 | 4 | 0 | 0 | 0 | 333 | 93 | 176 | 36965 | 2687714 | 378360 | 2.13 | 2003 | 4/2 | 1/5 | nothing-left |  |  | full |
| `REJECT_THEN_PASS_STUB` in `skills/tdd/scripts/tests/py/test_grade_prose_process.py` records only first grades (grader calls whose `Requirements:` list includes A2), so `test_2037_the_draft_pr_regrade_block_run_as_written_on_two_signed_units_with_the_first_rejected_exits_non_zero_after_grading_both` keeps asserting one first grade per unit once re-grades exist; it stays green against the current code; test file only, no production change ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 19 | 6 | 12 | 2101 | 116413 | 61501 | 0.19 | 369 | n/a | n/a | n/a |  |  | full |
| A first-grade FAIL row that reads PASS in either re-grade does not count as failed: when no row counts as failed the unit is PASS (exit 0), and when some rows count the printed reason lists only the rows that counted as failed, never one a re-grade passed ⟦criterion 1⟧ | 15 | 4 | 3 | 0 | 0 | 0 | 274 | 72 | 142 | 29251 | 2028754 | 367672 | 1.85 | 2198 | green 2/2, red 1/2 | 1/5 | nothing-left |  |  | full |
| A grade with no FAIL row makes no further grader call: grade-prose.sh launches the grader exactly once and exits 0 ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 14 | 28 | 5658 | 464451 | 43128 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| A re-grade that returns no verdict (the grader leaf exits non-zero, or its reply has no well-formed GRADES block for the rows it was asked about) makes grade-prose.sh exit 2, as a first grade's no-verdict does; it is never read as a PASS of the rows it was asked about ⟦criterion 2⟧ | 13 | 3 | 2 | 0 | 0 | 0 | 224 | 59 | 116 | 22948 | 1763195 | 285908 | 1.48 | 1122 | red 1/2, green 2/2 | 0/5 | structural-owed |  |  | already-satisfied |
| specs/utility-skills.md states, beside the G grading requirements, the rule that a FAIL row counts only when two re-grades against the failed rows both read it FAIL, with its why: one grader sample is noisy over a large list, and a REJECT has to reproduce before it costs an author attempt ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 13 | 26 | 3324 | 365142 | 47281 | 0.19 | 638 | n/a | n/a | n/a |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_skill_edit_step_process.py — FAILED test_changed_ids_that_pass_with_an_unchanged_id_failing_make_no_commit_before_the_author_and_do_not_exit_3 - AssertionError: (3, ... (harvest-usage.sh: the closing result record in .tdd/grade-prose.log carries no usage) ⟦suite-repair⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 72 | 20 | 40 | 8872 | 670900 | 83811 | 0.37 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When a grade has one or more FAIL rows, grade-prose.sh re-grades the unit twice against only those rows (each re-grade's prompt lists the failed rows and no other), and a row that reads FAIL in both re-grades counts as failed: the unit is REJECT (exit 1) and the reason printed lists that row ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 94 | 0.19 |
| A first-grade FAIL row that reads PASS in either re-grade does not count as failed: when no row counts as failed the unit is PASS (exit 0), and when some rows count the printed reason lists only the rows that counted as failed, never one a re-grade passed ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 86 | 0.12 |
| A re-grade that returns no verdict (the grader leaf exits non-zero, or its reply has no well-formed GRADES block for the rows it was asked about) makes grade-prose.sh exit 2, as a first grade's no-verdict does; it is never read as a PASS of the rows it was asked about ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | skipped | 0 | 8 | 0.05 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 22 | 22 | 23 | 24 | 23 | 24 | 50 | 26 | 60 | 42 | 49 | 43 | 25 | 24 | 23 | 26 | 54 | 32 | 24 | 24 | 23 | 22 | 23 | 25 | 22 | 22 | 23 | 22 | 22 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 27 | 32 | 3 | 3 | 4 | 17 | 21 | 20 | 113 | 67 | 44 | 50 | 142 | 150 | 137 | 146 | 127 | 21 | 18 | 23 | 151 | 0 | 20 | 132 | 141 | 159 | 156 | 7 | 8 | 20 | 21 | 21 | 23 | 20 | 18 | 18 | 149 | 18 | 7 | 17 | 17 | 19 | 22 | 21 | 19 | 17 | 0 | 215 | 229 | 29 | 164 |
| target | 4 | 3 | 8 | 8 | 7 | 8 | 8 | 20 | 8 | 5 | 6 | 8 | 6 | 7 | 8 | 6 | 6 | 8 | 9 | 13 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 300 | 584 | 127841 | 9165009 | 1404800 | 7.04 |
