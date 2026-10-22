### 📊 Metrics — issue 2092

Wall time for the issue: 4119 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run bailed — untestable-criterion, a process failure.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.91 over 74 turns, in 3 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 86034 |
| 2 | $0.03 | 87117 |
| 3 | $0.04 | 89076 |
| 4 | $0.03 | 89422 |
| 5 | $0.03 | 89941 |
| 6 | $0.02 | 90232 |
| 7 | $0.03 | 90534 |
| 8 | $0.03 | 91099 |
| 9 | $0.03 | 91543 |
| 10 | $0.03 | 91944 |
| 11 | $0.03 | 92312 |
| 12 | $0.03 | 92963 |
| 13 | $0.56 | 86018 |
| 14 | $0.03 | 86570 |
| 15 | $0.03 | 87385 |
| 16 | $0.04 | 89291 |
| 17 | $0.03 | 89634 |
| 18 | $0.02 | 90071 |
| 19 | $0.04 | 90833 |
| 20 | $0.04 | 92716 |
| 21 | $0.03 | 93304 |
| 22 | $0.03 | 93623 |
| 23 | $0.55 | 86052 |
| 24 | $0.03 | 87086 |
| 25 | $0.03 | 88977 |
| 26 | $0.02 | 89414 |
| 27 | $0.02 | 89841 |
| 28 | $0.02 | 90212 |
| 29 | $0.02 | 90513 |
| 30 | $0.02 | 90988 |
| 31 | $0.02 | 91401 |
| 32 | $0.02 | 91818 |
| 33 | $0.02 | 92396 |
| 34 | $0.02 | 92733 |
| 35 | $0.05 | 96060 |
| 36 | $0.03 | 97763 |
| 37 | $0.04 | 100197 |
| 38 | $0.03 | 101918 |
| 39 | $0.03 | 103120 |
| 40 | $0.03 | 103896 |
| 41 | $0.03 | 105252 |
| 42 | $0.03 | 106163 |
| 43 | $0.03 | 106981 |
| 44 | $0.03 | 107976 |
| 45 | $0.03 | 108880 |
| 46 | $0.03 | 109635 |
| 47 | $0.03 | 111144 |
| 48 | $0.03 | 111693 |
| 49 | $0.03 | 112420 |
| 50 | $0.03 | 113642 |
| 51 | $0.04 | 115298 |
| 52 | $0.03 | 116122 |
| 53 | $0.03 | 117129 |
| 54 | $0.04 | 118893 |
| 55 | $0.03 | 120039 |
| 56 | $0.04 | 121867 |
| 57 | $0.04 | 123657 |
| 58 | $0.03 | 124787 |
| 59 | $0.04 | 126334 |
| 60 | $0.04 | 127681 |
| 61 | $0.04 | 129369 |
| 62 | $0.03 | 130243 |
| 63 | $0.04 | 132015 |
| 64 | $0.03 | 132712 |
| 65 | $0.04 | 134116 |
| 66 | $0.04 | 135418 |
| 67 | $0.03 | 136147 |
| 68 | $0.04 | 137233 |
| 69 | $0.03 | 137804 |
| 70 | $0.05 | 140227 |
| 71 | $0.04 | 141337 |
| 72 | $0.04 | 142847 |
| 73 | $0.06 | 146804 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 850 | 0 | 30110 | 0.08 |
| red | 10 | 7 | 0 | 0 | 368 | 208 | 36 | 70 | 15381 | 924409 | 212957 | 0.78 |
| green | 5 | 2 | 0 | 0 | 556 | 94 | 26 | 48 | 8713 | 701502 | 71217 | 0.34 |
| refactor | 4 | 2 | 0 | 0 | 133 | 41 | 11 | 22 | 2359 | 270727 | 54658 | 0.19 |
| red-supersede | 2 | 0 | 0 | 0 | 49 | 32 | 6 | 10 | 4449 | 158329 | 23389 | 0.12 |
| diff | 2 | 1 | 0 | 0 | 158 | 17 | 6 | 12 | 1848 | 146094 | 23420 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 13 | 13 | 0 | 0 | 569 | 191 | 40 | 80 | 14642 | 998683 | 212623 | 0.78 |
| developer | claude-sonnet-5-5 | 11 | 0 | 0 | 0 | 706 | 209 | 46 | 84 | 18958 | 1202378 | 203128 | 0.82 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 45 | 0.12 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-supersede | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| develop-red | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The pytest suites register a `serial(reason)` mark for cases that must not run beside a full parallel load, and collection refuses a case carrying `serial` with no argument (or a blank one) naming why, with a usage error naming the case and the missing reason, as it already does for `process` and `tree_audit`; pinned by a small unit-tier case ⟦guard-subject: skills/tdd/scripts/tests/py/conftest.py⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 80 | 21 | 42 | 6457 | 538415 | 108027 | 0.39 | 515 | unknown | 0/5 | nothing-left |  |  | full |
| The pytest leg (`skills/tdd/scripts/veri/pytest_leg.py`) runs every case carrying the `serial` mark on its own, after the parallel cases finish: a parallel pass that leaves out `serial` cases, then a pass with no worker option holding only them, keeping whatever `-m` selection its arguments carry (so `make unit`'s and `make test`'s selections both still apply), still a single launcher invocation exiting 0 only when every pass passed; pinned by a small unit-tier case that drives the leg in-process with one `serial`-marked and one unmarked case and sees the marked one scheduled outside the parallel pass ⟦criterion 1⟧ | 14 | 8 | 0 | 0 | 0 | 0 | 275 | 54 | 102 | 22739 | 1451980 | 217542 | 0.92 | 788 | unknown | 0/5 | structural-owed |  |  | full |
| The two timeout cases `test_recipe_one_pytest_process.py::test_two_workers_pass_and_fail_the_same_cases_as_serial_and_name_a_failing_case_by_its_node_id` and `test_watch_runs_process.py::test_it_exits_only_when_the_second_of_two_running_conductors_exits_printing_that_issue_1930` carry the `serial` mark with a reason, and no production file changes ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 17 | 6 | 12 | 1848 | 146094 | 23420 | 0.09 | 220 | n/a | n/a | n/a |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py — FAILED skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py::test_two_workers_pass_and_fail_the_same_cases_as_serial_and_name_a_failing_case_by_its_node_id - Failed: Timeout (>30.0s) from pytest-timeout, even run alone in the serial pass, now that each nested make runs the leg's two passes ⟦suite-repair⟧ ⟦criterion 2⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 20 | 4 | 6 | 1706 | 64572 | 36652 | 0.12 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| The pytest suites register a `serial(reason)` mark for cases that must not run beside a full parallel load, and collection refuses a case carrying `serial` with no argument (or a blank one) naming why, with a usage error naming the case and the missing reason, as it already does for `process` and `tree_audit`; pinned by a small unit-tier case ⟦guard-subject: skills/tdd/scripts/tests/py/conftest.py⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 50 | 0.09 |
| The pytest leg (`skills/tdd/scripts/veri/pytest_leg.py`) runs every case carrying the `serial` mark on its own, after the parallel cases finish: a parallel pass that leaves out `serial` cases, then a pass with no worker option holding only them, keeping whatever `-m` selection its arguments carry (so `make unit`'s and `make test`'s selections both still apply), still a single launcher invocation exiting 0 only when every pass passed; pinned by a small unit-tier case that drives the leg in-process with one `serial`-marked and one unmarked case and sees the marked one scheduled outside the parallel pass ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 83 | 0.10 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 7 | 7 | 224 | 7 | 7 | 13 | 11 | 11 | 11 | 10 | 11 | 11 | 11 | 11 | 12 | 24 | 42 |
| fast | 17 | 18 | 18 | 22 | 21 | 29 | 28 |  |  |  |  |  |  |  |  |  |  |
| target | 7 | 8 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 86 | 164 | 33600 | 2201061 | 415751 | 1.60 |
