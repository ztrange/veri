### 📊 Metrics — issue 2133

Wall time for the issue: 2961 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2150.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.29 over 57 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 86198 |
| 2 | $0.02 | 87074 |
| 3 | $0.03 | 89035 |
| 4 | $0.02 | 89325 |
| 5 | $0.02 | 89748 |
| 6 | $0.02 | 90043 |
| 7 | $0.02 | 90419 |
| 8 | $0.02 | 90854 |
| 9 | $0.02 | 91236 |
| 10 | $0.02 | 91848 |
| 11 | $0.03 | 93768 |
| 12 | $0.03 | 94655 |
| 13 | $0.07 | 101303 |
| 14 | $0.03 | 102666 |
| 15 | $0.03 | 103723 |
| 16 | $0.03 | 104659 |
| 17 | $0.03 | 106131 |
| 18 | $0.03 | 106960 |
| 19 | $0.03 | 108099 |
| 20 | $0.03 | 108854 |
| 21 | $0.03 | 109789 |
| 22 | $0.03 | 111111 |
| 23 | $0.03 | 111807 |
| 24 | $0.03 | 112686 |
| 25 | $0.03 | 113412 |
| 26 | $0.03 | 114056 |
| 27 | $0.03 | 114851 |
| 28 | $0.03 | 115561 |
| 29 | $0.03 | 116579 |
| 30 | $0.04 | 118667 |
| 31 | $0.03 | 119375 |
| 32 | $0.04 | 121027 |
| 33 | $0.03 | 121717 |
| 34 | $0.04 | 123323 |
| 35 | $0.03 | 124065 |
| 36 | $0.04 | 125353 |
| 37 | $0.03 | 125809 |
| 38 | $0.03 | 126812 |
| 39 | $0.03 | 127163 |
| 40 | $0.03 | 127782 |
| 41 | $0.03 | 128298 |
| 42 | $0.03 | 128991 |
| 43 | $0.03 | 129429 |
| 44 | $0.03 | 130504 |
| 45 | $0.03 | 131168 |
| 46 | $0.03 | 132149 |
| 47 | $0.03 | 132916 |
| 48 | $0.03 | 133881 |
| 49 | $0.04 | 135122 |
| 50 | $0.03 | 135749 |
| 51 | $0.03 | 136321 |
| 52 | $0.03 | 137169 |
| 53 | $0.03 | 138008 |
| 54 | $0.03 | 138501 |
| 55 | $0.03 | 139129 |
| 56 | $0.03 | 139440 |
| 57 | $0.03 | 139784 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 5 | 1 | 2 | 677 | 0 | 29842 | 0.08 |
| red | 4 | 2 | 0 | 0 | 128 | 61 | 14 | 26 | 5801 | 339161 | 88083 | 0.31 |
| green | 4 | 2 | 0 | 0 | 222 | 52 | 17 | 30 | 4851 | 398146 | 56530 | 0.23 |
| refactor | 4 | 2 | 0 | 0 | 118 | 40 | 11 | 20 | 2548 | 240836 | 54739 | 0.19 |
| cover | 2 | 0 | 0 | 0 | 49 | 16 | 7 | 14 | 1563 | 158129 | 41901 | 0.14 |
| predicate | 2 | 0 | 0 | 0 | 32 | 24 | 6 | 12 | 787 | 144861 | 20660 | 0.07 |
| structural | 1 | 0 | 0 | 0 | 52 | 22 | 7 | 12 | 1193 | 159202 | 12100 | 0.06 |
| transform | 1 | 1 | 0 | 0 | 28 | 11 | 4 | 8 | 826 | 82647 | 28554 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 306 | 91 | 24 | 48 | 7393 | 559991 | 140798 | 0.48 |
| developer | claude-sonnet-5-5 | 11 | 0 | 0 | 0 | 333 | 140 | 43 | 76 | 10853 | 962991 | 191611 | 0.68 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 49 | 0.14 |
| predicate | 0 | 0.00 | 32 | 0.07 |
| structural | 0 | 0.00 | 52 | 0.06 |
| transform | 0 | 0.00 | 28 | 0.09 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When `git reset --hard` or `git clean` fails after the `.tdd/` appends are captured, resume-clean exits 2 with one stderr line that still names the failed git command and also says the appends were saved, names the saved `kept-tdd-appends.diff` by its path, and lists the stray paths; pinned by a forced-failure case (a medium case, real git, in skills/tdd/scripts/tests/py/test_resume_clean_process.py) asserting that stderr ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 70 | 22 | 38 | 7345 | 478584 | 110231 | 0.40 | 379 | unknown | 0/5 | structural-owed |  |  | full |
| A ledger whose clean-up changes nothing is left byte-identical by resume-clean, CRLF line endings included; pinned by a case with a CRLF ledger and no tick to change (a medium case, real git, in skills/tdd/scripts/tests/py/test_resume_clean_process.py) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 83 | 20 | 38 | 5855 | 499559 | 89121 | 0.33 | 324 | unknown | 0/5 | structural-owed |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py — FAILED test_two_workers_pass_and_fail_the_same_cases_as_serial_and_name_a_failing_case_by_its_node_id - Failed: Timeout (>30.0s) ⟦suite-repair⟧ ⟦criterion 2⟧ | 6 | 1 | 0 | 0 | 0 | 0 | 73 | 24 | 46 | 4369 | 544839 | 103215 | 0.36 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When `git reset --hard` or `git clean` fails after the `.tdd/` appends are captured, resume-clean exits 2 with one stderr line that still names the failed git command and also says the appends were saved, names the saved `kept-tdd-appends.diff` by its path, and lists the stray paths; pinned by a forced-failure case (a medium case, real git, in skills/tdd/scripts/tests/py/test_resume_clean_process.py) asserting that stderr ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 57 | 0.10 |
| A ledger whose clean-up changes nothing is left byte-identical by resume-clean, CRLF line endings included; pinned by a case with a CRLF ledger and no tick to change (a medium case, real git, in skills/tdd/scripts/tests/py/test_resume_clean_process.py) ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 61 | 0.09 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 12 | 17 | 7 | 11 | 0 | 12 | 11 | 4 | 5 | 4 | 12 | 13 | 13 | 12 | 12 | 12 |
| fast | 18 | 19 | 18 | 17 | 17 | 16 |  |  |  |  |  |  |  |  |  |  |
| target | 13 | 13 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 67 | 124 | 18246 | 1522982 | 332409 | 1.17 |
