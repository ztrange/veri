### 📊 Metrics — issue 2888

Wall time for the issue: 4017 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 6 planned.
Outcome: the run bailed — no-verdict, a system failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.02 over 61 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88049 tokens, largest 182099 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 88049 |
| 2 | $0.07 | 95191 |
| 3 | $0.04 | 97304 |
| 4 | $0.02 | 97857 |
| 5 | $0.03 | 99395 |
| 6 | $0.03 | 100064 |
| 7 | $0.02 | 100540 |
| 8 | $0.02 | 100866 |
| 9 | $0.02 | 101251 |
| 10 | $0.03 | 101878 |
| 11 | $0.02 | 102201 |
| 12 | $0.09 | 110837 |
| 13 | $0.06 | 115718 |
| 14 | $0.08 | 122631 |
| 15 | $0.04 | 125150 |
| 16 | $0.06 | 130019 |
| 17 | $0.03 | 130420 |
| 18 | $0.03 | 131084 |
| 19 | $0.03 | 131561 |
| 20 | $0.03 | 131884 |
| 21 | $0.03 | 132625 |
| 22 | $0.04 | 133936 |
| 23 | $0.03 | 134804 |
| 24 | $0.04 | 136180 |
| 25 | $0.04 | 137880 |
| 26 | $0.03 | 138478 |
| 27 | $0.03 | 139268 |
| 28 | $0.03 | 139621 |
| 29 | $0.03 | 140305 |
| 30 | $0.03 | 140978 |
| 31 | $0.04 | 142154 |
| 32 | $0.03 | 142844 |
| 33 | $0.03 | 143253 |
| 34 | $0.03 | 144019 |
| 35 | $0.03 | 144716 |
| 36 | $0.03 | 145120 |
| 37 | $0.03 | 145782 |
| 38 | $0.03 | 146374 |
| 39 | $0.05 | 149585 |
| 40 | $0.04 | 150857 |
| 41 | $0.04 | 151486 |
| 42 | $0.04 | 152445 |
| 43 | $0.04 | 153694 |
| 44 | $0.05 | 156423 |
| 45 | $0.04 | 157206 |
| 46 | $0.09 | 164939 |
| 47 | $0.05 | 166836 |
| 48 | $0.04 | 167737 |
| 49 | $0.04 | 167983 |
| 50 | $0.04 | 169190 |
| 51 | $0.04 | 170383 |
| 52 | $0.04 | 171256 |
| 53 | $0.05 | 172676 |
| 54 | $0.04 | 173470 |
| 55 | $0.04 | 174617 |
| 56 | $0.04 | 174976 |
| 57 | $0.04 | 175648 |
| 58 | $0.04 | 175987 |
| 59 | $0.04 | 176258 |
| 60 | $0.04 | 177320 |
| 61 | $0.07 | 182099 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 12 | 1 | 2 | 1307 | 0 | 33289 | 0.10 |
| red | 6 | 2 | 0 | 0 | 858 | 226 | 39 | 76 | 20906 | 1325144 | 226469 | 1.19 |
| green | 4 | 2 | 0 | 0 | 1095 | 88 | 23 | 44 | 7703 | 701763 | 75136 | 0.34 |
| refactor | 3 | 1 | 0 | 0 | 310 | 53 | 13 | 26 | 2650 | 359007 | 87672 | 0.28 |
| pin | 2 | 1 | 1 | 0 | 113 | 29 | 6 | 12 | 2806 | 157116 | 36515 | 0.14 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 7 | 1 | 0 | 1316 | 129 | 27 | 52 | 9891 | 698390 | 154069 | 0.55 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 760 | 151 | 34 | 66 | 11878 | 1035956 | 203972 | 0.73 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 315 | 128 | 21 | 42 | 13603 | 808684 | 101040 | 0.75 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 314 | 0.19 |
| green | 0 | 0.00 | 516 | 0.13 |
| refactor | 0 | 0.00 | 21 | 0.10 |
| pin | 113 | 0.14 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Go: after two `rerecord-refactored` runs, each following its own verified refactor (`.tdd/verdict-refactor.exit` = 0, its own green sha) that changes the assertion lines of a helper the frozen case calls, the case's record holds exactly one `helpers:` line, matching HEAD, and `check-earlier` exits 0; the existing case `test_check_earlier_exits_1_for_a_go_case_after_a_later_rerecord_refactored_over_a_t_fatal_line_deleted_from_its_helper_2867` stays green, so the helper change is accepted only when the helper at the green sha matches the recorded `helpers:` digest (a git repo in tmp_path: a medium case marked process, in test_tests_frozen_process.py) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 158 | 34 | 68 | 11899 | 1097436 | 164419 | 0.64 | 2030 | unknown | 1/5 | nothing-left |  |  | full |
| Python: an `assert` line deleted from a called helper by a non-refactor commit after a re-record is not absorbed by a later `rerecord-refactored` run over a verified refactor whose green sha is that commit: `check-earlier` still exits 1 naming the case (a git repo in tmp_path: a medium case marked process, in test_tests_frozen_process.py) ⟦criterion 2⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 157 | 27 | 54 | 16409 | 965800 | 137555 | 0.89 | unknown | 1/2 | unknown | unknown |  |  | pin |
| Reordering the assertion lines of a helper a re-recorded frozen case calls, with no line added or removed, leaves `check-earlier` at exit 0 (a git repo in tmp_path: a medium case marked process, in test_tests_frozen_process.py) ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 81 | 20 | 36 | 5757 | 479794 | 123818 | 0.42 | unknown | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Go: after two `rerecord-refactored` runs, each following its own verified refactor (`.tdd/verdict-refactor.exit` = 0, its own green sha) that changes the assertion lines of a helper the frozen case calls, the case's record holds exactly one `helpers:` line, matching HEAD, and `check-earlier` exits 0; the existing case `test_check_earlier_exits_1_for_a_go_case_after_a_later_rerecord_refactored_over_a_t_fatal_line_deleted_from_its_helper_2867` stays green, so the helper change is accepted only when the helper at the green sha matches the recorded `helpers:` digest (a git repo in tmp_path: a medium case marked process, in test_tests_frozen_process.py) ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 289 | 0.18 |
| Reordering the assertion lines of a helper a re-recorded frozen case calls, with no line added or removed, leaves `check-earlier` at exit 0 (a git repo in tmp_path: a medium case marked process, in test_tests_frozen_process.py) ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 21 | 0.10 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 51 | 48 | 39 | 54 | 72 | 66 | 0 | 16 | 16 | 16 | 20 | 77 | 72 | 72 | 78 | 81 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 47 | 63 | 98 | 116 | 100 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 8 | 11 | 14 | 11 | 17 | 10 | 12 | 11 | 11 | 11 | 11 | 14 | 13 | 11 | 12 | 9 | 13 | 9 | 9 | 11 | 12 | 10 | 10 | 10 | 10 | 9 | 9 | 9 | 11 | 10 | 12 | 10 | 10 | 9 | 9 | 11 | 14 | 13 | 14 | 13 | 14 | 14 | 13 | 11 | 13 | 15 | 14 | 12 | 12 | 15 | 16 | 16 | 15 | 14 | 14 | 13 | 21 | 12 | 18 | 13 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 82 | 160 | 35372 | 2543030 | 459081 | 5.05 (estimate) |
